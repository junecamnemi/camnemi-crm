const fs = require("fs");
const path = require("path");
const { Client } = require("pg");

function env(k) {
  const text = fs.readFileSync(path.join(__dirname, "..", ".env"), "utf8");
  for (const line of text.split(/\r?\n/)) {
    if (!line || line.startsWith("#") || !line.includes("=")) continue;
    const i = line.indexOf("=");
    if (line.slice(0, i).trim() === k) return line.slice(i + 1).trim();
  }
  return "";
}

(async () => {
  const password = env("SUPABASE_DB_PASSWORD");
  if (!password) throw new Error("missing password");
  const client = new Client({
    host: "aws-0-ap-northeast-2.pooler.supabase.com",
    port: 5432,
    user: "postgres.zjdvzpylxazfbazioxto",
    password,
    database: "postgres",
    ssl: { rejectUnauthorized: false },
  });
  await client.connect();

  const tiny = path.join(__dirname, "_univ_batches", "tiny");
  const files = fs.readdirSync(tiny)
    .filter((f) => f.startsWith("t") && f.endsWith(".sql"))
    .sort()
    .map((f) => path.join(tiny, f));

  // Only run files >= t250 (the remaining ones); earlier ones already applied.
  const remaining = files.filter((f) => {
    const base = path.basename(f);
    const num = parseInt(base.slice(1, 4), 10);
    return num >= 250;
  });

  for (const file of remaining) {
    const sql = fs.readFileSync(file, "utf8");
    process.stdout.write(path.basename(file) + " ... ");
    await client.query(sql);
    console.log("ok");
  }

  // guides
  const gfile = path.join(__dirname, "_univ_batches", "json", "guides.sql");
  process.stdout.write("guides.sql ... ");
  await client.query(fs.readFileSync(gfile, "utf8"));
  console.log("ok");

  const u = await client.query("select count(*)::int as n, count(*) filter (where type='univ')::int as univ, count(*) filter (where type='junior')::int as junior from universities");
  const g = await client.query("select count(*)::int as n from university_guides");
  console.log("RESULT universities", u.rows[0], "guides", g.rows[0].n);
  await client.end();
})().catch((e) => { console.error("FAIL", e.message); process.exit(1); });
