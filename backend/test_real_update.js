const fs = require("fs");
const key = fs.readFileSync("index.html", "utf8").match(/DEFAULT_SUPABASE_KEY\s*=\s*'([^']+)'/)[1];
const SB = "https://zjdvzpylxazfbazioxto.supabase.co";
const H = { apikey: key, Authorization: "Bearer " + key, "Content-Type": "application/json", Prefer: "resolution=merge-duplicates,return=representation" };

(async () => {
  // Replicate the EXACT mapping in supabaseWriteTables for AN RATANA
  const c = {
    id: "imp_anratana_5", pipe: "korea", stage: "stay", name: "AN RATANA",
    age: "", agency: "", program: "", school: "", appdate: "", contact: "", email: "",
    loan: "", topik: "", ielts: "", notes: [], birthdate: "", noqr: "", illegal: "", denied: "",
    loan_flag: "", payments: [], recent: "1799900000000", folder_id: "", folder_url: "",
    docs: [], hidden: "", siemreap: "", custom_fields: {}, major: "", parent_contact: "",
    parent_name: "", school_en: "", passport: "", highschool: "", gradmonth: "",
    appdocs: "[]", visadocs: "[]"
  };
  const body = {
    id: c.id, pipe: c.pipe, stage: c.stage, name: c.name,
    age: c.age || '', agency: c.agency || '', program: c.program || '', school: c.school || '',
    appdate: c.appdate || '', contact: c.contact || '', email: c.email || '', loan: c.loan || '',
    topik: c.topik || '', ielts: c.ielts || '', notes: c.notes || [], birthdate: c.birthdate || '',
    noqr: c.noqr || '', illegal: c.illegal || '', denied: c.denied || '',
    loan_flag: c.loan_flag || '',
    payments: typeof c.payments === 'string' && c.payments ? (function(){ try { return JSON.parse(c.payments); } catch(e){ return []; } })() : (c.payments || []),
    recent: c.recent || '', folder_id: c.folder_id || '', folder_url: c.folder_url || '',
    docs: c.docs || [], hidden: c.hidden || '', siemreap: c.siemreap || '',
    custom_fields: c.custom_fields || {}, major: c.major || '', parent_contact: c.parent_contact || '',
    parent_name: c.parent_name || '', school_en: c.school_en || '', passport: c.passport || '',
    highschool: c.highschool || '', gradmonth: c.gradmonth || '',
    appdocs: c.appdocs || '[]', visadocs: c.visadocs || '[]'
  };
  const r = await fetch(SB + "/rest/v1/customers?on_conflict=id", { method: "POST", headers: H, body: JSON.stringify([body]) });
  const txt = await r.text();
  console.log("STATUS:", r.status);
  console.log("BODY:", txt.slice(0, 400));
})().catch(e => console.error("ERR", e.message));
