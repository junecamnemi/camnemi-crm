// One-time / scheduled sync: pull folder index + all folder file listings from
// Apps Script backend, then upsert into Supabase cache tables.
// Usage: node backend/_sync_drive_to_supabase.js [--refresh-files]
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

async function callBackend(body) {
  const res = await fetch(execUrl, {
    method: "POST",
    headers: { "Content-Type": "text/plain;charset=utf-8" },
    body: JSON.stringify(body),
  });
  return JSON.parse(await res.text());
}

(async () => {
  console.log("Fetching folder index from Apps Script...");
  const idxRes = await callBackend({ action: "getFolderIndex" });
  if (!idxRes.ok) throw new Error("getFolderIndex failed: " + JSON.stringify(idxRes));
  const index = idxRes.index || {};
  const names = Object.keys(index);
  console.log(`Index has ${names.length} student folders`);

  const pg = new Client({
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
  console.log("Folder index upserted to Supabase");

  if (!REFRESH_FILES) {
    console.log("Skipping file listings (use --refresh-files to fetch them).");
    await pg.end();
    return;
  }

  // Fetch file listings per folder (can be slow; sequential to respect Apps Script quotas)
  let done = 0, found = 0;
  for (const name of names) {
    try {
      const r = await callBackend({ action: "listStudentFolderFiles", name });
      if (r.ok && r.found) {
        found++;
        await pg.query(
          `insert into student_folder_files (name, folder_id, folder_url, files)
           values ($1,$2,$3,$4::jsonb)
           on conflict (name) do update set folder_id=excluded.folder_id, folder_url=excluded.folder_url, files=excluded.files, updated_at=now()`,
          [name, r.folderId || index[name] || "", r.folderUrl || "", JSON.stringify(r.files || [])]
        );
      } else {
        // folder exists in index but no files found - still record empty
        await pg.query(
          `insert into student_folder_files (name, folder_id, files)
           values ($1,$2,'[]'::jsonb)
           on conflict (name) do update set folder_id=excluded.folder_id, updated_at=now()`,
          [name, index[name] || ""]
        );
      }
    } catch (e) {
      console.log(`  ERR ${name}: ${e.message}`);
    }
    done++;
    if (done % 25 === 0) console.log(`  ${done}/${names.length} (found files: ${found})`);
  }
  console.log(`Done. ${found}/${names.length} folders have files cached.`);
  await pg.end();
})().catch((e) => { console.error(e); process.exit(1); });
