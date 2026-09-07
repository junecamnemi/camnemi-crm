const fs = require("fs");
const key = fs.readFileSync("index.html", "utf8").match(/DEFAULT_SUPABASE_KEY\s*=\s*'([^']+)'/)[1];
const SB = "https://zjdvzpylxazfbazioxto.supabase.co";
const H = { apikey: key, Authorization: "Bearer " + key };

function validJSON(s) { try { JSON.parse(s); return true; } catch(e){ return false; } }

(async () => {
  const r = await fetch(SB + "/rest/v1/customers?select=id,name,notes,payments,docs,appdocs,visadocs&limit=500", { headers: H });
  const rows = await r.json();
  let bad = [];
  rows.forEach(c => {
    // notes may be array or string; payments may be array or string; docs array
    const checks = [];
    if (typeof c.notes === 'string' && c.notes && !validJSON(c.notes)) checks.push('notes');
    if (typeof c.payments === 'string' && c.payments && !validJSON(c.payments)) checks.push('payments');
    if (typeof c.docs === 'string' && c.docs && !validJSON(c.docs)) checks.push('docs');
    if (typeof c.appdocs === 'string' && c.appdocs && c.appdocs !== '[]' && !validJSON(c.appdocs)) checks.push('appdocs');
    if (typeof c.visadocs === 'string' && c.visadocs && c.visadocs !== '[]' && !validJSON(c.visadocs)) checks.push('visadocs');
    if (checks.length) bad.push({ name: c.name, id: c.id, bad: checks });
  });
  console.log("rows checked:", rows.length);
  console.log("rows with corrupt JSON:", bad.length);
  bad.slice(0, 15).forEach(b => console.log("  ", b.id, b.name, "-> bad:", b.bad.join(",")));
})().catch(e => console.error("ERR", e.message));
