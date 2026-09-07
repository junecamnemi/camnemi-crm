const fs = require("fs");
const key = fs.readFileSync("index.html", "utf8").match(/DEFAULT_SUPABASE_KEY\s*=\s*'([^']+)'/)[1];
const SB = "https://zjdvzpylxazfbazioxto.supabase.co";
(async () => {
  const r = await fetch(SB + "/rest/v1/customers?id=eq.imp_anratana_5&select=id,name,stage,pipe,updated_at,recent", { headers: { apikey: key, Authorization: "Bearer " + key } });
  const rows = await r.json();
  console.log("BEFORE:", JSON.stringify(rows[0]));
  // Also check for any duplicate AN RATANA rows (different ids)
  const r2 = await fetch(SB + "/rest/v1/customers?name=eq.AN%20RATANA&select=id,name,stage,pipe,updated_at", { headers: { apikey: key, Authorization: "Bearer " + key } });
  const rows2 = await r2.json();
  console.log("ALL AN RATANA rows:", rows2.length);
  rows2.forEach(x => console.log("  ", x.id, "|", x.stage, "|", x.pipe, "|", (x.updated_at||"").slice(0,19)));
})().catch(e => console.error("ERR", e.message));
