// One-time / scheduled sync: pull folder index + all folder file listings from
// Apps Script backend, then upsert into Supabase cache tables.
// Usage: node backend/_sync_drive_to_supabase.js [--refresh-files] [--dry-run] [--limit N]
// Env:   SYNC_CONCURRENCY (default 3), SYNC_LOG (append progress log), SYNC_STALE_HOURS (default 48)
//
// 2026-09-30 fix: the old loop restarted at names[0] on every run with no cursor, so with
// ~347 folders x 1.5-2.5s sequential Apps Script calls the run always exceeded the wrapper
// timeout and the tail of the list stayed stale forever. Now: oldest-updated folders first
// (resumable), bounded concurrency, per-item retry, and progress appended to a log file so a
// killed run still leaves evidence.
const fs = require("fs");
const { Client } = require("pg");
const env = {};
for (const l of fs.readFileSync(".env", "utf8").split("\n")) {
  const t = l.trim();
  const i = t.indexOf("=");
  if (i > 0) env[t.slice(0, i).trim()] = t.slice(i + 1).trim();
}

// Apps Script exec URL from find_drive_links.js
const src = fs.readFileSync("backend/find_drive_links.js", "utf8");
const execUrl = src.match(/https:\/\/script\.google\.com\/macros\/s\/[A-Za-z0-9_-]+\/exec/)[0];

const REFRESH_FILES = process.argv.includes("--refresh-files");
const DRY_RUN = process.argv.includes("--dry-run");
const argLimit = process.argv.indexOf("--limit");
const LIMIT = argLimit > -1 ? parseInt(process.argv[argLimit + 1], 10) : 0;
const CONCURRENCY = Math.max(1, parseInt(process.env.SYNC_CONCURRENCY || "3", 10));
const STALE_HOURS = parseFloat(process.env.SYNC_STALE_HOURS || "48");
const LOG_PATH = process.env.SYNC_LOG || "";

function log(msg) {
  const line = `[${new Date().toISOString()}] ${msg}`;
  console.log(line);
  if (LOG_PATH) {
    try { fs.appendFileSync(LOG_PATH, line + "\n"); } catch (e) { /* logging must never kill the sync */ }
  }
}

async function callBackend(body) {
  const res = await fetch(execUrl, {
    method: "POST",
    headers: { "Content-Type": "text/plain;charset=utf-8" },
    body: JSON.stringify(body),
  });
  const text = await res.text();
  let parsed;
  try { parsed = JSON.parse(text); } catch (e) {
    throw new Error(`non-JSON response (http ${res.status}): ${text.slice(0, 120)}`);
  }
  return parsed;
}

async function callWithRetry(body, attempts = 3) {
  let lastErr;
  for (let a = 1; a <= attempts; a++) {
    try { return await callBackend(body); } catch (e) {
      lastErr = e;
      if (a < attempts) await new Promise((r) => setTimeout(r, 1000 * a));
    }
  }
  throw lastErr;
}

(async () => {
  const t0 = Date.now();
  log(`sync start (refresh-files=${REFRESH_FILES} dry-run=${DRY_RUN} limit=${LIMIT || "all"} concurrency=${CONCURRENCY})`);

  log("Fetching folder index from Apps Script...");
  const idxRes = await callWithRetry({ action: "getFolderIndex" });
  if (!idxRes.ok) throw new Error("getFolderIndex failed: " + JSON.stringify(idxRes));
  const index = idxRes.index || {};
  const names = Object.keys(index);
  log(`Index has ${names.length} student folders (index fetch ${Math.round((Date.now() - t0) / 1000)}s)`);

  if (DRY_RUN) log("DRY RUN: no Supabase connection, no writes.");

  let pg = null;
  const lastSync = {};
  if (!DRY_RUN) {
    pg = new Client({
      host: "aws-0-ap-northeast-2.pooler.supabase.com",
      port: 5432,
      database: "postgres",
      user: "postgres.zjdvzpylxazfbazioxto",
      password: env.SUPABASE_DB_PASSWORD,
      sslmode: "require",
    });
    await pg.connect();

    // Upsert index (name -> folder_id)
    for (let i = 0; i < names.length; i += 100) {
      const chunk = names.slice(i, i + 100);
      const values = chunk.map((n) => `('${n.replace(/'/g, "''")}','${index[n].replace(/'/g, "''")}')`).join(",");
      await pg.query(
        `insert into student_folder_index (name, folder_id) values ${values}
         on conflict (name) do update set folder_id = excluded.folder_id, updated_at = now()`
      );
    }
    log("Folder index upserted to Supabase");

    const prev = await pg.query("select name, updated_at from student_folder_files");
    for (const r of prev.rows) lastSync[r.name] = r.updated_at ? new Date(r.updated_at).getTime() : 0;
  }

  if (!REFRESH_FILES) {
    log("Skipping file listings (use --refresh-files to fetch them).");
    if (pg) await pg.end();
    return;
  }

  // Resume-safe ordering: never-synced first, then oldest updated_at first, so a run that
  // dies half-way continues where the previous one stopped instead of redoing the head.
  const queue = names.slice().sort((a, b) => (lastSync[a] || 0) - (lastSync[b] || 0));
  const todo = LIMIT > 0 ? queue.slice(0, LIMIT) : queue;

  let done = 0, withFiles = 0, empty = 0, errors = 0;
  const errorNames = [];

  async function handle(name) {
    try {
      const r = await callWithRetry({ action: "listStudentFolderFiles", name });
      if (DRY_RUN) {
        if (r.ok && r.found) withFiles++; else empty++;
        return;
      }
      if (r.ok && r.found) {
        withFiles++;
        await pg.query(
          `insert into student_folder_files (name, folder_id, folder_url, files)
           values ($1,$2,$3,$4::jsonb)
           on conflict (name) do update set folder_id=excluded.folder_id, folder_url=excluded.folder_url, files=excluded.files, updated_at=now()`,
          [name, r.folderId || index[name] || "", r.folderUrl || "", JSON.stringify(r.files || [])]
        );
      } else {
        empty++;
        // folder exists in index but no files found - still record empty
        await pg.query(
          `insert into student_folder_files (name, folder_id, files)
           values ($1,$2,'[]'::jsonb)
           on conflict (name) do update set folder_id=excluded.folder_id, updated_at=now()`,
          [name, index[name] || ""]
        );
      }
    } catch (e) {
      errors++;
      errorNames.push(name);
      log(`  ERR ${name}: ${e.message}`);
    } finally {
      done++;
      if (done % 25 === 0 || done === todo.length) {
        log(`  ${done}/${todo.length} (with files: ${withFiles}, empty: ${empty}, errors: ${errors}, ${Math.round((Date.now() - t0) / 1000)}s)`);
      }
    }
  }

  let cursor = 0;
  await Promise.all(
    Array.from({ length: Math.min(CONCURRENCY, todo.length) }, async () => {
      while (cursor < todo.length) {
        const name = todo[cursor++];
        await handle(name);
      }
    })
  );

  let stale = 0;
  if (!DRY_RUN) {
    if (STALE_HOURS > 0) {
      const s = await pg.query(
        `select count(*)::int n from student_folder_files where updated_at < now() - ($1 || ' hours')::interval`,
        [String(STALE_HOURS)]
      );
      stale = s.rows[0].n;
    } else {
      log("SYNC_STALE_HOURS <= 0: stale count skipped");
    }
    await pg.end();
  }

  log(`Done. processed=${done} withFiles=${withFiles} empty=${empty} errors=${errors} stale>${STALE_HOURS}h=${stale} elapsed=${Math.round((Date.now() - t0) / 1000)}s`);
  if (errorNames.length) log(`error folders: ${errorNames.slice(0, 20).join(", ")}${errorNames.length > 20 ? " ..." : ""}`);
  if (errors > 0) process.exit(2);
})().catch((e) => {
  log("FATAL " + (e && e.stack ? e.stack : e));
  process.exit(1);
});