const fs = require("fs");
const key = fs.readFileSync("index.html", "utf8").match(/DEFAULT_SUPABASE_KEY\s*=\s*'([^']+)'/)[1];
const SB = "https://zjdvzpylxazfbazioxto.supabase.co";
const H = { apikey: key, Authorization: "Bearer " + key, "Content-Type": "application/json" };

async function tryOp(name, fn) {
  try { const r = await fn(); const t = await r.text(); console.log((r.ok?"OK   ":"FAIL "), name, "->", r.status, t.slice(0,120)); }
  catch (e) { console.log("THROW", name, "->", e.message.slice(0,180)); }
}

(async () => {
  // SAFE: DELETE with a condition that matches NOTHING (id=__nonexistent__)
  // This tests whether anon can DELETE at all, without deleting any real rows.
  await tryOp("DELETE transactions (safe no-match)", () => fetch(SB + "/rest/v1/transactions?id=eq.__probe_none__", { method: "DELETE", headers: { ...H, Prefer: "return=minimal" } }));
  await tryOp("DELETE recs (safe no-match)", () => fetch(SB + "/rest/v1/recs?id=eq.__probe_none__", { method: "DELETE", headers: { ...H, Prefer: "return=minimal" } }));
  // check tables exist
  await tryOp("SELECT transactions", () => fetch(SB + "/rest/v1/transactions?select=id&limit=1", { headers: H }));
  await tryOp("SELECT recs", () => fetch(SB + "/rest/v1/recs?select=id&limit=1", { headers: H }));
  await tryOp("SELECT tasks", () => fetch(SB + "/rest/v1/tasks?select=id&limit=1", { headers: H }));
})().catch(e => console.error("FATAL", e.message));
