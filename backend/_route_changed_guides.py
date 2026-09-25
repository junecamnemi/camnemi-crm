# Route today's CHANGED own-site guide PDFs into the matching adiga guide folder
# so guide_auto_analyze.py re-parses them into verified_kb.
import json, os, re, shutil, sys, datetime

BASE = r"C:\Users\wisew\camnemi-crm\backend"
UP = r"C:/Users/wisew/내 드라이브/02_Crawling_Sheet/University_Project"
TODAY = datetime.date.today().isoformat()

DEST = {
    ("ba", 2027):     f"{UP}/adiga_2027_외국인_모집요강/own_site",
    ("ma", 2027):     f"{UP}/adiga_2027_대학원_모집요강",
    ("ma", 2026):     f"{UP}/adiga_2026_대학원_모집요강",
    ("junior", 2027): f"{UP}/adiga_2027_전문대학_모집요강",
    ("junior", 2026): f"{UP}/adiga_2026_전문대학_모집요강",
    ("lang", 2027):   f"{UP}/adiga_2027_어학연수_모집요강",
    ("lang", 2026):   f"{UP}/adiga_2026_어학연수_모집요강",
    ("ba", 2026):     f"{UP}/adiga_2026_외국인_모집요강",
}

def pdf_year(path):
    try:
        from pypdf import PdfReader
    except ImportError:
        from PyPDF2 import PdfReader
    try:
        r = PdfReader(path)
        txt = ""
        for pg in r.pages[:3]:
            txt += pg.extract_text() or ""
    except Exception as e:
        return None, f"read-fail:{e}"
    if re.search(r"202\s?7\s*학년도", txt) or "2027학년도" in txt:
        return 2027, "text"
    if "2026학년도" in txt:
        return 2026, "text"
    return None, "no-year"

rows = [json.loads(l) for l in open(os.path.join(BASE, "_scrape_changes.jsonl"), encoding="utf-8") if l.strip()]
today = [r for r in rows if r.get("date") == TODAY and r["saved"].lower().endswith(".pdf")]
seen = set(); uniq = []
for r in today:
    k = (r["school"], r["level"])
    if k in seen: continue
    seen.add(k); uniq.append(r)

copied, skipped = [], []
for r in uniq:
    src = r["saved"]
    if not os.path.exists(src):
        skipped.append((r["school"], r["level"], "missing")); continue
    yr, how = pdf_year(src)
    if yr is None:
        skipped.append((r["school"], r["level"], how)); continue
    dest_dir = DEST.get((r["level"], yr))
    if not dest_dir or not os.path.isdir(dest_dir):
        skipped.append((r["school"], r["level"], f"nodir:{yr}")); continue
    school = r["school"]
    lvlmap = {"ba": "BA", "ma": "MA", "junior": "JR", "lang": "LANG"}
    fn = f"{school}_{lvlmap[r['level']]}_{yr}.pdf"
    dst = os.path.join(dest_dir, fn)
    shutil.copy2(src, dst)
    copied.append((school, r["level"], yr, dst))

print(f"[route] unique changed PDFs: {len(uniq)}")
print(f"[route] copied: {len(copied)}")
for c in copied: print("  +", c[0], c[1], c[2])
print(f"[route] skipped: {len(skipped)}")
for s in skipped: print("  -", s)
