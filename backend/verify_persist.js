const fs = require("fs");
const key = fs.readFileSync("index.html", "utf8").match(/DEFAULT_SUPABASE_KEY\s*=\s*'([^']+)'/)[1];
const SB = "https://zjdvzpylxazfbazioxto.supabase.co";
const H = { apikey: key, Authorization: "Bearer " + key, "Content-Type": "application/json", Prefer: "resolution=merge-duplicates,return=representation" };
const sleep = ms => new Promise(r => setTimeout(r, ms));

(async () => {
  const body = { id: "imp_anratana_5", pipe: "korea", stage: "stay", name: "AN RATANA",
    age: "", agency: "", program: "", school: "", appdate: "", contact: "", email: "", loan: "",
    topik: "", ielts: "", notes: [], birthdate: "", noqr: "", illegal: "", denied: "",
    loan_flag: "", payments: [], recent: String(Date.now()), folder_id: "", folder_url: "",
    docs: [], hidden: "", siemreap: "", custom_fields: {}, major: "", parent_contact: "",
    parent_name: "", school_en: "", passport: "", highschool: "", gradmonth: "",
    appdocs: "[]", visadocs: "[]"
  };
  const r = await fetch(SB + "/rest/v1/customers?on_conflict=id", { method: "POST", headers: H, body: JSON.stringify([body]) });
  console.log("write status:", r.status);
  for (let i = 0; i < 3; i++) {
    await sleep(4000);
    const rr = await fetch(SB + "/rest/v1/customers?id=eq.imp_anratana_5&select=id,stage,updated_at", { headers: H });
    const row = (await rr.json())[0];
    console.log("t+" + ((i+1)*4) + "s:", row.stage, "|", (row.updated_at||"").slice(0,19));
  }
})().catch(e => console.error("ERR", e.message));
