const fs = require("fs");
const { Client } = require("pg");

const created = JSON.parse(fs.readFileSync("backend/_created_folders.json", "utf8"));
const pw = fs.readFileSync(".env", "utf8").split("\n").find(l => l.startsWith("SUPABASE_DB_PASSWORD=")).split("=")[1].trim();

(async () => {
  const c = new Client({ host: "aws-0-ap-northeast-2.pooler.supabase.com", port: 5432, user: "postgres.zjdvzpylxazfbazioxto", password: pw, database: "postgres", ssl: { rejectUnauthorized: false } });
  await c.connect();
  let updated = 0;
  for (const r of created) {
    if (!r.ok || !r.folderId) continue;
    const res = await c.query(
      `update customers set folder_id=$1, folder_url=$2 where lower(name)=lower($3)`,
      [r.folderId, r.folderUrl, r.name]
    );
    updated += res.rowCount;
  }
  console.log("updated rows:", updated);
  const check = await c.query("select count(*) n from customers where folder_url is not null and folder_url<>''");
  const total = await c.query("select count(distinct lower(name)) n from customers");
  console.log("customers with folder_url now:", check.rows[0].n, "of", total.rows[0].n, "distinct students");
  await c.end();
})().catch(e => { console.error(e.message); process.exit(1); });
