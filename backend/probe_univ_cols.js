const fs = require("fs");
const key = fs.readFileSync("index.html", "utf8").match(/DEFAULT_SUPABASE_KEY\s*=\s*'([^']+)'/)[1];
const base = "https://zjdvzpylxazfbazioxto.supabase.co/rest/v1/universities";

(async () => {
  // fetch one row to see columns
  const r = await fetch(base + "?" + new URLSearchParams({ select: "*", limit: "1" }).toString(), { headers: { apikey: key, Authorization: "Bearer " + key } });
  const rows = await r.json();
  console.log("columns:", rows.length ? Object.keys(rows[0]).join(", ") : "none");
  if (rows.length) console.log("sample:", JSON.stringify(rows[0]).slice(0, 500));
})().catch(e => console.error("ERR", e.message));
