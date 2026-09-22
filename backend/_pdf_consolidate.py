# -*- coding: utf-8 -*-
"""Consolidate all foreigner-only guide PDFs into a single managed folder:
University_Project/guides/{ba,ma,junior,lang}/{2026,2027}/
Foreigner HTML files stay in place (they are the guide)."""
import os, shutil, re

UP = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project"
GUIDES = os.path.join(UP, "guides")

# program -> list of (source_folder, year, subfolder-or-None, is_foreigner_only)
SOURCES = {
    "ba": [
        ("adiga_2026_외국인_모집요강", "2026", "외국인"),
        ("adiga_2027_외국인_모집요강", "2027", "외국인"),
        ("adiga_2027_외국인_모집요강", "2027", "own_site"),
    ],
    "ma": [
        ("adiga_2026_대학원_모집요강", "2026", None),
        ("adiga_2027_대학원_모집요강", "2027", None),
    ],
    "junior": [
        ("adiga_2026_전문대학_모집요강", "2026", None),
        ("adiga_2027_전문대학_모집요강", "2027", None),
    ],
    "lang": [
        ("adiga_2026_어학연수_모집요강", "2026", None),
        ("adiga_2027_어학연수_모집요강", "2027", None),
    ],
}

def norm_school(fname):
    m = re.search(r'([가-힣A-Za-z]+(?:대학교|대학|전문대학|교육원))', fname)
    return m.group(1) if m else fname

os.makedirs(GUIDES, exist_ok=True)
moved = 0
skipped_dup = 0
for prog, pairs in SOURCES.items():
    for (folder, year, sub) in pairs:
        src = os.path.join(UP, folder)
        if sub: src = os.path.join(src, sub)
        if not os.path.isdir(src): continue
        dst_dir = os.path.join(GUIDES, prog, year)
        os.makedirs(dst_dir, exist_ok=True)
        for f in os.listdir(src):
            if not f.lower().endswith(".pdf"): continue
            sp = os.path.join(src, f)
            dp = os.path.join(dst_dir, f)
            if os.path.exists(dp):
                # same name already there -> keep the larger (or skip)
                if os.path.getsize(dp) >= os.path.getsize(sp):
                    skipped_dup += 1
                    continue
            shutil.copy2(sp, dp)
            moved += 1

print(f"이동/복사: {moved} | 중복스킵: {skipped_dup}")
print("\n=== guides/ 구조 ===")
for root, dirs, files in os.walk(GUIDES):
    n = len([f for f in files if f.endswith(".pdf")])
    if n: print(f"  {os.path.relpath(root, GUIDES)}: {n}")
