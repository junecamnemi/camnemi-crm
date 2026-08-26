const fs = require("fs");
const key = fs.readFileSync("index.html", "utf8").match(/DEFAULT_SUPABASE_KEY\s*=\s*'([^']+)'/)[1];
const base = "https://zjdvzpylxazfbazioxto.supabase.co/rest/v1/customers";
const APPSCRIPT = "https://script.google.com/macros/s/AKfycbwJ7QxDviSojjDJrRHJokneMebb46aS19ooqYiIuyYQsXdxzcZmyzPDleJXr-7JCnonAQ/exec";

async function getIndex() {
  const r = await fetch(APPSCRIPT, { method: "POST", headers: { "Content-Type": "text/plain;charset=utf-8" }, body: JSON.stringify({ action: "getFolderIndex" }) });
  const txt = await r.text();
  try { return JSON.parse(txt); } catch(e){ console.log("index parse fail", txt.slice(0,100)); return {}; }
}

function fuzzyFolderId(index, name) {
  if (!index) return '';
  const label = String(name || '').replace(/[\\/:*?"<>|]/g, '').trim().toLowerCase();
  if (index[label]) return index[label];
  const tokens = label.split(/[\s,;]+/).filter(t => t.length > 1);
  if (!tokens.length) return '';
  if (tokens.length >= 2) {
    const reversed = tokens.slice(1).join(' ') + ' ' + tokens[0];
    if (index[reversed]) return index[reversed];
  }
  for (const k in index) {
    let all = true;
    for (const t of tokens) { if (k.indexOf(t) < 0) { all = false; break; } }
    if (all) return index[k];
  }
  if (tokens.length === 1) {
    for (const k in index) { if (k.indexOf(tokens[0]) >= 0) return index[k]; }
  }
  return '';
}

(async () => {
  const idx = await getIndex();
  const index = idx.index || {};
  console.log("folders in index:", Object.keys(index).length);

  // Get all customers
  const qs = new URLSearchParams({ select: "id,name,pipe,stage,folder_id,folder_url,hidden", limit: "500" }).toString();
  const r = await fetch(base + "?" + qs, { headers: { apikey: key, Authorization: "Bearer " + key } });
  const rows = await r.json();
  if (!Array.isArray(rows)) { console.log("err", JSON.stringify(rows).slice(0,200)); return; }
  console.log("customers in DB:", rows.length);

  // focus: VISA stage or Korea pipe
  const focus = rows.filter(x => x.pipe === 'korea' || x.stage === 'visa');
  console.log("focus (Korea + VISA):", focus.length);

  const matched = [], missing = [];
  const seen = new Set();
  for (const x of focus) {
    const nm = String(x.name||'').trim().toUpperCase();
    if (!nm || seen.has(nm)) continue;
    seen.add(nm);
    const fid = fuzzyFolderId(index, nm);
    if (fid) matched.push({ name: nm, id: x.id, folderId: fid, hasDbFolder: !!x.folder_id });
    else missing.push({ name: nm, id: x.id });
  }
  console.log("\nMATCHED to folder:", matched.length);
  console.log("MISSING (no folder in index):", missing.length);
  if (missing.length) {
    console.log("--- MISSING ---");
    missing.forEach(m => console.log("  " + m.name + " (" + m.id + ")"));
  }
  console.log("\n--- matched but NO folder in DB (need connection) ---");
  const needConn = matched.filter(m => !m.hasDbFolder);
  console.log("count:", needConn.length);
  needConn.forEach(m => console.log("  " + m.name + " -> " + m.folderId));

  fs.writeFileSync("backend/folder_connect_scan.json", JSON.stringify({ matched, missing, needConn }, null, 2));
  console.log("\nsaved backend/folder_connect_scan.json");
})().catch(e => console.error("ERR", e.message));
