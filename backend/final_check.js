const fs = require("fs");
const key = fs.readFileSync("index.html", "utf8").match(/DEFAULT_SUPABASE_KEY\s*=\s*'([^']+)'/)[1];
const SB = "https://zjdvzpylxazfbazioxto.supabase.co";
const H = { apikey: key, Authorization: "Bearer " + key };
(async () => {
  const r = await fetch(SB + "/rest/v1/customers?name=eq.AN%20RATANA&select=id,name,stage,pipe,updated_at", { headers: H });
  const rows = await r.json();
  console.log("AN RATANA now:", JSON.stringify(rows[0]));
})().catch(e => console.error("ERR", e.message));
