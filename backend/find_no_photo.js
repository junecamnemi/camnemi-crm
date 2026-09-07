const fs = require("fs");
const key = fs.readFileSync("index.html", "utf8").match(/DEFAULT_SUPABASE_KEY\s*=\s*'([^']+)'/)[1];
const SB = "https://zjdvzpylxazfbazioxto.supabase.co";
const H = { apikey: key, Authorization: "Bearer " + key };

function isPhoto(f) {
  const n = (f && f.name) || '';
  if (!/\.(jpe?g|png|webp|gif|bmp)$/i.test(n)) return false;
  if (/passport|여권|passeport|identity|신분증|주민증|residence|학생증|id card|idcard|정부|khmerid|certificate|서명|signature/i.test(n)) return false;
  return /photo|picture|사진|이미지|image|img|Ảnh/i.test(n);
}

(async () => {
  const r = await fetch(SB + "/rest/v1/customers?select=id,name,pipe,stage,docs,folder_url&pipe=eq.korea&limit=1000", { headers: H });
  const rows = await r.json();
  const noPhoto = [];
  rows.forEach(c => {
    const files = Array.isArray(c.docs) ? c.docs : (typeof c.docs === 'string' && c.docs ? (() => { try { return JSON.parse(c.docs); } catch(e){ return []; } })() : []);
    const hasImg = files.filter(isPhoto);
    if (!hasImg.length) {
      noPhoto.push({ name: c.name, stage: c.stage, nFiles: files.length, hasFolder: !!c.folder_url, sample: files.slice(0,3).map(f=>f.name) });
    }
  });
  console.log("Korea students without photo:", noPhoto.length);
  noPhoto.forEach(x => console.log("-", x.name, "| stage:", x.stage, "| files:", x.nFiles, "| folder:", x.hasFolder, "|", x.sample.join(', ')));
})().catch(e => console.error("ERR", e.message));
