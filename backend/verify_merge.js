const fs = require("fs");
const key = fs.readFileSync("index.html", "utf8").match(/DEFAULT_SUPABASE_KEY\s*=\s*'([^']+)'/)[1];
const base = "https://zjdvzpylxazfbazioxto.supabase.co/rest/v1/customers";

// Simulate the syncPush merge for AN RATANA:
// - remote: current DB row (welcome, has passport, updated 08-22)
// - local : what the DOM would export after the user moved to stay (recent=now, updated_at=now)
async function simulate(name, localRow) {
  const qs = new URLSearchParams({ select: "id,name,stage,pipe,recent,updated_at,passport", name: "eq." + name, limit: "3" }).toString();
  const r = await fetch(base + "?" + qs, { headers: { apikey: key, Authorization: "Bearer " + key } });
  const remote = await r.json();
  if (!remote.length) { console.log(name, "-> NOT IN DB"); return; }
  // merged: local first, then extras (remote rows not sharing local id)
  const localIds = new Set([localRow.id]);
  const extras = remote.filter(c => !localIds.has(c.id));
  const merged = [localRow].concat(extras);
  // dedupe by name (UPPERCASE), local wins
  const byName = new Map();
  for (const c of merged) {
    const keyN = String(c.name || '').trim().toUpperCase();
    const prev = byName.get(keyN);
    if (!prev) { byName.set(keyN, c); continue; }
    const cIsLocal = localIds.has(c.id);
    const pIsLocal = localIds.has(prev.id);
    if (cIsLocal && !pIsLocal) { byName.set(keyN, c); continue; }
    if (!cIsLocal && pIsLocal) { continue; }
  }
  const winner = Array.from(byName.values())[0];
  console.log(name, "-> remote:", remote[0].stage, "| local:", localRow.stage, "| MERGE WINNER:", winner.stage, winner.passport ? "(has passport)" : "");
}

(async () => {
  // AN RATANA moved to stay
  await simulate("AN RATANA", { id: "imp_anratana_5", name: "AN RATANA", stage: "stay", pipe: "korea", recent: String(Date.now()), updated_at: new Date().toISOString(), passport: "x" });
  // a student whose local lacks passport but remote has one
  await simulate("MES CHHALY", { id: "imp_meschhaly_55", name: "MES CHHALY", stage: "stay", pipe: "korea", recent: String(Date.now()), updated_at: new Date().toISOString() });
})().catch(e => console.error("ERR", e.message));
