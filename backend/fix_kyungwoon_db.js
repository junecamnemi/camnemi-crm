const fs = require("fs");
const key = fs.readFileSync("index.html", "utf8").match(/DEFAULT_SUPABASE_KEY\s*=\s*'([^']+)'/)[1];
const base = "https://zjdvzpylxazfbazioxto.supabase.co/rest/v1/universities";

(async () => {
  // find kyungwoon by name_kr
  const qs = new URLSearchParams({ select: "id,name_kr,short_en", name_kr: "eq.경운대학교" }).toString();
  const r = await fetch(base + "?" + qs, { headers: { apikey: key, Authorization: "Bearer " + key } });
  console.log("status", r.status);
  const rows = await r.json();
  console.log("rows:", JSON.stringify(rows));
  if (Array.isArray(rows) && rows.length) {
    const id = rows[0].id;
    const up = await fetch(base + "?" + new URLSearchParams({ id: "eq." + id }).toString(), {
      method: "PATCH",
      headers: { apikey: key, Authorization: "Bearer " + key, "Content-Type": "application/json", Prefer: "return=representation" },
      body: JSON.stringify({ short_en: "KWU" })
    });
    console.log("patch", up.status);
    console.log("updated:", JSON.stringify(await up.json()));
  }
})().catch(e => console.error("ERR", e.message));
