const fs = require("fs");
const key = fs.readFileSync("index.html", "utf8").match(/DEFAULT_SUPABASE_KEY\s*=\s*'([^']+)'/)[1];
const SB = "https://zjdvzpylxazfbazioxto.supabase.co";
const H = { apikey: key, Authorization: "Bearer " + key, "Content-Type": "application/json", Prefer: "resolution=merge-duplicates,return=representation" };

(async () => {
  // Exact field set that supabaseWriteTables sends
  const body = { id: "imp_anratana_5", pipe: "korea", stage: "stay", name: "AN RATANA",
    age: "", agency: "", program: "", school: "", appdate: "", contact: "", email: "", loan: "",
    topik: "", ielts: "", notes: [], birthdate: "", noqr: "", illegal: "", denied: "",
    loan_flag: "", payments: [], recent: "1799900000000", folder_id: "", folder_url: "",
    docs: [], hidden: "", siemreap: "", custom_fields: {}, major: "", parent_contact: "",
    parent_name: "", school_en: "", passport: "", highschool: "", gradmonth: "",
    appdocs: "[]", visadocs: "[]"
  };
  const r = await fetch(SB + "/rest/v1/customers?on_conflict=id", { method: "POST", headers: H, body: JSON.stringify([body]) });
  const txt = await r.text();
  console.log("STATUS:", r.status);
  if (r.ok) {
    const rows = JSON.parse(txt);
    console.log("UPDATED:", rows[0]?.id, rows[0]?.stage, "| updated_at:", (rows[0]?.updated_at||"").slice(0,19));
  } else {
    console.log("ERROR:", txt.slice(0, 300));
  }
})().catch(e => console.error("ERR", e.message));