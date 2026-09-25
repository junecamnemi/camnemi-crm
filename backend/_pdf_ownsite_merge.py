# -*- coding: utf-8 -*-
"""Consolidate _ownsite_daily PDFs into guides/ by program & year.
Foreigner HTML files stay in _ownsite_daily (they are the guide)."""
import os, re, shutil

UP = r"C:\Users\wisew\내 드라이브\02_Crawling_Sheet\University_Project"
GUIDES = os.path.join(UP, "guides")
OWNSITE = os.path.join(UP, "_ownsite_daily")

def detect_prog_year(fname):
    """Infer program & year from filename (e.g. 단국대_ba.pdf, 가톨릭대_lang.pdf, ..._junior.pdf)."""
    prog = None
    if "_ba" in fname or "ba_" in fname or "_BA" in fname: prog = "ba"
    elif "_ma" in fname or "ma_" in fname or "_MA" in fname: prog = "ma"
    elif "_lang" in fname or "lang_" in fname or "_LANG" in fname: prog = "lang"
    elif "_junior" in fname or "junior_" in fname or "_전문학사" in fname: prog = "junior"
    # year
    year = "2026"
    m = re.search(r'(20\d\d)', fname)
    if m: year = m.group(1)
    return prog, year

moved = 0
unclassified = []
for f in os.listdir(OWNSITE):
    if not f.lower().endswith(".pdf"): continue
    prog, year = detect_prog_year(f)
    if not prog:
        unclassified.append(f)
        continue
    dst_dir = os.path.join(GUIDES, prog, year)
    os.makedirs(dst_dir, exist_ok=True)
    sp = os.path.join(OWNSITE, f)
    dp = os.path.join(dst_dir, f)
    if os.path.exists(dp):
        if os.path.getsize(dp) >= os.path.getsize(sp):
            continue  # already have same/bigger
    shutil.copy2(sp, dp)
    moved += 1

print(f"ownsite -> guides 이동: {moved}")
print(f"분류 불가 (남김): {len(unclassified)}")
for f in unclassified[:20]:
    print("  ?", f)
