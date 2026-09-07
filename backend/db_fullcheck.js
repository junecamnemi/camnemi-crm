const fs = require("fs");
const key = fs.readFileSync("index.html", "utf8").match(/DEFAULT_SUPABASE_KEY\s*=\s*'([^']+)'/)[1];
const base = "https://zjdvzpylxazfbazioxto.supabase.co/rest/v1/customers";
(async () => {
  // 1) Check AN RATANA current state + all columns
  const r = await fetch(base + "?id=eq.imp_anratana_5", { headers: { apikey: key, Authorization: "Bearer " + key } });
  const rows = await r.json();
  console.log("AN RATANA:", JSON.stringify(rows[0], null, 1));
})().catch(e => console.error("ERR", e.message));
