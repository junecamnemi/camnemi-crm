const fs = require("fs");
const key = fs.readFileSync("index.html", "utf8").match(/DEFAULT_SUPABASE_KEY\s*=\s*'([^']+)'/)[1];
const base = "https://zjdvzpylxazfbazioxto.supabase.co/rest/v1/customers";
const APPSCRIPT = "https://script.google.com/macros/s/AKfycbwJ7QxDviSojjDJrRHJokneMebb46aS19ooqYiIuyYQsXdxzcZmyzPDleJXr-7JCnonAQ/exec";

async function getKoreaStudents() {
  const qs = new URLSearchParams({ select: "name", pipe: "eq.korea", limit: "500" }).toString();
  const r = await fetch(base + "?" + qs, { headers: { apikey: key, Authorization: "Bearer " + key } });
  const rows = await r.json();
  const seen = new Set();
  const names = [];
  rows.forEach(x => {
    const nm = String(x.name || "").trim().toUpperCase();
    if (nm && !seen.has(nm)) { seen.add(nm); names.push(nm); }
  });
  return names;
}

// Fetch the full index in ONE call, then fuzzy-match client-side (same logic as the app)
async function getIndex() {
  const r = await fetch(APPSCRIPT, { method: "POST", headers: { "Content-Type": "text/plain;charset=utf-8" }, body: JSON.stringify({ action: "getFolderIndex" }) });
  const j = JSON.parse(await r.text());
  return (j && j.index) || {};
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
  const names = await getKoreaStudents();
  const index = await getIndex();
  console.log("Korea students:", names.length, "| folders in index:", Object.keys(index).length);

  const matched = [], missed = [];
  for (const n of names) {
    const fid = fuzzyFolderId(index, n);
    if (fid) matched.push(n);
    else missed.push(n);
  }
  console.log("MATCHED:", matched.length, "| MISSED:", missed.length);
  if (missed.length) {
    console.log("--- missed students ---");
    missed.forEach(n => console.log("  " + n));
  }
  fs.writeFileSync("backend/korea_fuzzy_test.json", JSON.stringify({ matched, missed }, null, 2));
  console.log("saved backend/korea_fuzzy_test.json");
})().catch(e => console.error("ERR", e.message));
