const fs = require("fs");
const key = fs.readFileSync("index.html", "utf8").match(/DEFAULT_SUPABASE_KEY\s*=\s*'([^']+)'/)[1];
const SB = "https://zjdvzpylxazfbazioxto.supabase.co";
const H = { apikey: key, Authorization: "Bearer " + key };

(async () => {
  // Most recent 10 Move card activity entries
  const r = await fetch(SB + "/rest/v1/activity_log?select=time,student,action&action=ilike.*Move card*&order=id.desc&limit=10", { headers: H });
  const rows = await r.json();
  console.log("=== most recent Move card entries ===");
  rows.forEach(x => console.log(x.time, "|", x.student, "|", x.action));

  // For the newest moved student, check DB stage
  if (rows.length) {
    const nm = rows[0].student;
    const r2 = await fetch(SB + "/rest/v1/customers?name=eq." + encodeURIComponent(nm) + "&select=id,name,stage,pipe,updated_at", { headers: H });
    const custs = await r2.json();
    console.log("\n=== DB for", nm, "===");
    custs.forEach(c => console.log(" ", c.id, "|", c.stage, "|", c.pipe, "|", (c.updated_at||"").slice(0,19)));
  }
})().catch(e => console.error("ERR", e.message));
