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
  const dir = path.join(__dirname, "_univ_batches", "rich");
  const files = fs.readdirSync(dir).filter(f => f.startsWith("r") && f.endsWith(".sql")).sort();
  for (const file of files) {
    process.stdout.write(file + " ... ");
    await client.query(fs.readFileSync(path.join(dir, file), "utf8"));
    console.log("ok");
  }
  const r = await client.query("select count(*) filter (where majors_ba <> '[]'::jsonb)::int as ba, count(*) filter (where scholarships <> '[]'::jsonb)::int as sch, count(*) filter (where req_note <> '')::int as rn, count(*) filter (where t is not null)::int as t from universities");
  console.log("RESULT", JSON.stringify(r.rows[0]));
  await client.end();
})().catch(e => { console.error("FAIL", e.message); process.exit(1); });
