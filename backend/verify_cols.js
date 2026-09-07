const fs = require("fs");
const key = fs.readFileSync("index.html", "utf8").match(/DEFAULT_SUPABASE_KEY\s*=\s*'([^']+)'/)[1];
const SB = "https://zjdvzpylxazfbazioxto.supabase.co";
const H = { apikey: key, Authorization: "Bearer " + key };
(async () => {
  const r = await fetch(SB + "/rest/v1/customers?select=id,name,appdocs,visadocs&limit=2", { headers: H });
  const t = await r.text();
  console.log("status:", r.status);
  console.log(t.slice(0, 300));
})().catch(e => console.error("ERR", e.message));
