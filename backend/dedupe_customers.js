const { Client } = require("pg");
const pw = require("fs").readFileSync(".env", "utf8").split("\n").find(l => l.startsWith("SUPABASE_DB_PASSWORD=")).split("=")[1].trim();

(async () => {
  const c = new Client({ host: "aws-0-ap-northeast-2.pooler.supabase.com", port: 5432, user: "postgres.zjdvzpylxazfbazioxto", password: pw, database: "postgres", ssl: { rejectUnauthorized: false } });
  await c.connect();

  // Terminal/deliberate stages should win regardless of recency.
  // Otherwise keep the most recently updated row.
  const TERMINAL = new Set(["giveup", "archived", "canceled"]);

  const groups = await c.query(`
    select lower(name) n from customers group by lower(name) having count(*) > 1
  `);

  let removed = 0;
  for (const { n } of groups.rows) {
    const rows = (await c.query(
      `select id, stage, updated_at from customers where lower(name)=$1 order by updated_at desc`,
      [n]
    )).rows;

    // pick keeper
    const terminalRow = rows.find(r => TERMINAL.has(r.stage));
    let keeper;
    if (terminalRow) {
      // prefer most recently updated terminal row; else most recent overall
      const termRows = rows.filter(r => TERMINAL.has(r.stage)).sort((a,b) => new Date(b.updated_at) - new Date(a.updated_at));
      keeper = termRows[0];
    } else {
      keeper = rows[0]; // most recent
    }

    const del = await c.query(`delete from customers where lower(name)=$1 and id <> $2`, [n, keeper.id]);
    removed += del.rowCount;
  }

  const t = await c.query("select count(*) n from customers");
  const d = await c.query("select count(distinct lower(name)) n from customers");
  console.log("removed duplicates:", removed);
  console.log("total rows now:", t.rows[0].n, "| distinct names:", d.rows[0].n);
  await c.end();
})().catch(e => { console.error(e.message); process.exit(1); });
