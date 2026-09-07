const fs = require("fs");
const key = fs.readFileSync("index.html", "utf8").match(/DEFAULT_SUPABASE_KEY\s*=\s*'([^']+)'/)[1];
const SB = "https://zjdvzpylxazfbazioxto.supabase.co";
const H = { apikey: key, Authorization: "Bearer " + key };
(async () => {
  // use the OpenAPI/root endpoint to list columns? Simpler: try selecting specific columns
  const cols = ["id","name","stage","pipe","appdocs","visadocs","highschool","gradmonth","passport","parent_name","parent_contact","major","school_en","custom_fields","recent","hidden","siemreap"];
  const q = "select=" + cols.join(",") + "&limit=1";
  const r = await fetch(SB + "/rest/v1/customers?" + q, { headers: H });
  const t = await r.text();
  console.log("status:", r.status);
  console.log(t.slice(0, 300));
})().catch(e => console.error("ERR", e.message));
