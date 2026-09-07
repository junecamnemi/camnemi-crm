const fs = require("fs");
const key = fs.readFileSync("index.html", "utf8").match(/DEFAULT_SUPABASE_KEY\s*=\s*'([^']+)'/)[1];
const SB = "https://zjdvzpylxazfbazioxto.supabase.co";
const H = { apikey: key, Authorization: "Bearer " + key, "Content-Type": "application/json" };

async function del(table, col) {
  // DELETE with a condition that matches NOTHING (safe) — tests whether anon DELETE is permitted at all
  const q = col + "=eq.__definitely_not_a_real_value_9x";
  const r = await fetch(SB + "/rest/v1/" + table + "?" + q, { method: "DELETE", headers: { ...H, Prefer: "return=minimal" } });
  const t = await r.text();
  console.log((r.ok ? "OK   " : "FAIL "), "DELETE", table, "->", r.status, t.slice(0,120));
}
(async () => {
  await del("fees", "name");
  await del("partners", "name");
  await del("tasks", "title");
  await del("transactions", "date");
  await del("recs", "title");
  await del("agencies", "name");
})().catch(e => console.error("FATAL", e.message));
