const fs = require("fs");
const key = fs.readFileSync("backend/_anon_key.tmp", "utf8").trim();
const base = "https://zjdvzpylxazfbazioxto.supabase.co/rest/v1/customers";
const rows = JSON.parse(fs.readFileSync("backend/_cust_rows.json", "utf8"));

const TERMINAL = new Set(["giveup", "archived", "canceled"]);

// group by lowercase name
const g = {};
rows.forEach(x => {
  const n = (x.name || "").toLowerCase().trim();
  if (!n) return;
  (g[n] = g[n] || []).push(x);
});

const toDelete = [];
let kept = 0;
Object.values(g).forEach(arr => {
  if (arr.length <= 1) return;
  // pick keeper: prefer most-recent terminal, else most recent
  const term = arr.filter(r => TERMINAL.has(r.stage)).sort((a,b) => new Date(b.updated_at) - new Date(a.updated_at));
  const keeper = term.length ? term[0] : arr.sort((a,b) => new Date(b.updated_at) - new Date(a.updated_at))[0];
  arr.forEach(x => { if (x.id !== keeper.id) toDelete.push(x.id); });
  kept++;
});

console.log("groups processed:", kept, "| rows to delete:", toDelete.length);

(async () => {
  // delete in batches of 100 by id (REST supports in=.(id1,id2,...))
  let deleted = 0;
  for (let i = 0; i < toDelete.length; i += 80) {
    const batch = toDelete.slice(i, i + 80);
    const qs = new URLSearchParams({ id: `in.(${batch.join(",")})` }).toString();
    const r = await fetch(base + "?" + qs, {
      method: "DELETE",
      headers: { apikey: key, Authorization: "Bearer " + key, Prefer: "return=minimal" }
    });
    console.log("delete batch", i, "-> status", r.status);
    deleted += batch.length;
  }
  console.log("total deleted:", deleted);
  // verify
  const qs = new URLSearchParams({ select: "id", limit: "2000" }).toString();
  const rr = await fetch(base + "?" + qs, { headers: { apikey: key, Authorization: "Bearer " + key } });
  const all = await rr.json();
  const uniq = new Set(all.map(x => (x.name || "").toLowerCase().trim()));
  console.log("remaining rows:", all.length, "| distinct names:", uniq.size);
})().catch(e => console.error("ERR", e.message));
