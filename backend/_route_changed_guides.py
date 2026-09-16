# -*- coding: utf-8 -*-
"""Route today's CHANGED own-site guides (_ownsite_daily) into the correct
adiga guide folder used by guide_auto_analyze.FOLDER_MAP.

Year is detected from the PDF text (2027학년도 / 2026학년도), NOT assumed,
so 2027 authoritative data is never clobbered by an old 2026 file.
"""
import os, json, sys, shutil, re, datetime

B = r"C:\Users\USER\camnemi-crm\backend"
UP = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project"
CHANGES = os.path.join(B, "_scrape_changes.jsonl")

DEST = {
    ("ba", 2027):   f"{UP}/adiga_2027_외국인_모집요강/own_site",
    ("ma", 2027):   f"{UP}/adiga_2027_대학원_모집요강",
    ("ma", 2026):   f"{UP}/adiga_2026_대학원_모집요강",
    ("junior", 2027): f"{UP}/adiga_2027_전문대학_모집요강",
    ("junior", 2026): f"{UP}/adiga_2026_전문대학_모집요강",
    ("lang", 2027): f"{UP}/adiga_2027_어학연수_모집요강",
    ("lang", 2026): f"{UP}/adiga_2026_어학연수_모집요강",
}

today = sys.argv[1] if len(sys.argv) > 1 else datetime.date.today().isoformat()

def pdf_year(path):
    try:
        import pdfplumber
        with pdfplumber.open(path) as pdf:
            txt = ""
            for pg in pdf.pages[:4]:
                txt += (pg.extract_text() or "")
    except Exception:
        try:
            from pypdf import PdfReader
            r = PdfReader(path)
            txt = "".join((p.extract_text() or "") for p in r.pages[:4])
        except Exception:
            return None
    if re.search(r"2027\s*학년도", txt) or "2027학년도" in txt:
        return 2027
    if re.search(r"2026\s*학년도", txt):
        return 2026
    if "2027" in txt:
        return 2027
    if "2026" in txt:
        return 2026
    return None

rows = []
with open(CHANGES, encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            o = json.loads(line)
        except Exception:
            continue
        if o.get("date") == today:
            rows.append(o)

print(f"[route] today({today}) change rows: {len(rows)}")
copied = skipped_nonpdf = skipped_year = skipped_nodest = 0
detail = []
for o in rows:
    saved = o.get("saved") or ""
    lvl = (o.get("level") or "").lower()
    school = o.get("school") or ""
    if not saved or not os.path.isfile(saved) or not saved.lower().endswith(".pdf"):
        skipped_nonpdf += 1
        continue
    y = pdf_year(saved)
    if y is None:
        skipped_year += 1
        detail.append(f"  ? year-unknown {school}[{lvl}]")
        continue
    d = DEST.get((lvl, y))
    if not d or not os.path.isdir(d):
        skipped_nodest += 1
        detail.append(f"  x no-dest {school}[{lvl} {y}]")
        continue
    base = f"{school}_{y}_외국인.pdf" if lvl == "ba" else f"{school}_{lvl}_{y}.pdf"
    dst = os.path.join(d, base)
    shutil.copy2(saved, dst)
    copied += 1
    detail.append(f"  + {school}[{lvl} {y}] -> {os.path.basename(d)}/{base}")

for l in detail[:80]:
    print(l)
print(f"[route] copied={copied} nonpdf={skipped_nonpdf} year_unknown={skipped_year} no_dest={skipped_nodest}")
