const fs = require("fs");
const key = fs.readFileSync("index.html", "utf8").match(/DEFAULT_SUPABASE_KEY\s*=\s*'([^']+)'/)[1];
const SB = "https://zjdvzpylxazfbazioxto.supabase.co";
const H = { apikey: key, Authorization: "Bearer " + key };
(async () => {
  // Use the root endpoint to get the OpenAPI schema (lists tables & columns)
  const r = await fetch(SB + "/rest/v1/", { headers: { ...H, Accept: "application/openapi+json" } });
  const t = await r.text();
  // crude: find customers schema definition
  const i = t.indexOf('"customers"');
  console.log("openapi status:", r.status, "len:", t.length);
  // Try to parse
  try {
    const spec = JSON.parse(t);
    const cs = spec.components && spec.components.schemas && spec.components.schemas.customers;
    if (cs) { console.log("customers props:", Object.keys(cs.properties || {}).join(", ")); }
    else { console.log("no customers schema found; tables:", Object.keys(spec.components?.schemas||{}).join(", ").slice(0,400)); }
  } catch(e) { console.log("parse failed", e.message, t.slice(0,200)); }
})().catch(e => console.error("ERR", e.message));
