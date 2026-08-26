const fs = require("fs");
const key = fs.readFileSync("index.html", "utf8").match(/DEFAULT_SUPABASE_KEY\s*=\s*'([^']+)'/)[1];
const base = "https://zjdvzpylxazfbazioxto.supabase.co/rest/v1/customers";
const APPSCRIPT = "https://script.google.com/macros/s/AKfycbwJ7QxDviSojjDJrRHJokneMebb46aS19ooqYiIuyYQsXdxzcZmyzPDleJXr-7JCnonAQ/exec";

async function getIndex() {
  const r = await fetch(APPSCRIPT, { method: "POST", headers: { "Content-Type": "text/plain;charset=utf-8" }, body: JSON.stringify({ action: "getFolderIndex" }) });
  const txt = await r.text();
  try { return JSON.parse(txt); } catch(e){ return {}; }
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

  // Get all Korea + VISA customers missing folder_id
  const qs = new URLSearchParams({ select: "id,name,pipe,stage,folder_id,folder_url", or: "(pipe.eq.korea,stage.eq.visa)", folder_id: "is.null", limit: "500" }).toString();
  const r = await fetch(base + "?" + qs, { headers: { apikey: key, Authorization: "Bearer " + key } });
  const rows = await r.json();
  console.log("Korea/VISA rows missing folder_id:", Array.isArray(rows) ? rows.length : JSON.stringify(rows).slice(0,150));
  if (!Array.isArray(rows)) return;

  // also rows with empty folder_id
  const qs2 = new URLSearchParams({ select: "id,name,pipe,stage,folder_id,folder_url", or: "(pipe.eq.korea,stage.eq.visa)", folder_id: "eq.", limit: "500" }).toString();
  const r2 = await fetch(base + "?" + qs2, { headers: { apikey: key, Authorization: "Bearer " + key } });
  const rows2 = await r2.json();
  const all = (Array.isArray(rows) ? rows : []).concat(Array.isArray(rows2) ? rows2 : []);
  console.log("total (null + empty):", all.length);

  const seen = new Set();
  let updated = 0, skipped = 0;
  for (const x of all) {
    const nm = String(x.name||'').trim().toUpperCase();
    if (!nm || seen.has(nm)) continue;
    seen.add(nm);
    const fid = fuzzyFolderId(index, nm);
    if (!fid) { console.log("  no folder for", nm); skipped++; continue; }
    const folderUrl = "https://drive.google.com/drive/folders/" + fid;
    // update ALL rows with this name
    const q = new URLSearchParams({ name: "eq." + nm }).toString();
    const up = await fetch(base + "?" + q, { method: "PATCH", headers: { apikey: key, Authorization: "Bearer " + key, "Content-Type": "application/json" }, body: JSON.stringify({ folder_id: fid, folder_url: folderUrl }) });
    if (up.ok) { updated++; console.log("  ✓", nm, "->", fid); }
    else { console.log("  ✗ db fail", nm, up.status); }
  }
  console.log("\nDONE updated:", updated, "| no folder:", skipped);
})().catch(e => console.error("ERR", e.message));
