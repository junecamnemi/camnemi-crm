# -*- coding: utf-8 -*-
"""Scan the whole drive for collected guide PDFs, dedupe by school, report coverage.
Counts FOREIGNER-only guides (excludes 재외국민/own_site) by program & year."""
import os, re, json

UP = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project"

# program -> list of (folder, year, subfolder-or-None)
FOLDERS = {
    "BA": [("adiga_2026_외국인_모집요강", "2026", "외국인"), ("adiga_2027_외국인_모집요강", "2027", "외국인")],
    "MA": [("adiga_2026_대학원_모집요강", "2026", None), ("adiga_2027_대학원_모집요강", "2027", None)],
    "junior": [("adiga_2026_전문대학_모집요강", "2026", None), ("adiga_2027_전문대학_모집요강", "2027", None)],
    "lang": [("adiga_2026_어학연수_모집요강", "2026", None), ("adiga_2027_어학연수_모집요강", "2027", None)],
}

def norm_school(fname):
    # extract school name from filename
    m = re.search(r'([가-힣A-Za-z]+(?:대학교|대학|전문대학|교육원))', fname)
    if m: return m.group(1)
    return fname

def list_pdf(folder, sub):
    p = os.path.join(UP, folder)
    if sub: p = os.path.join(p, sub)
    if not os.path.isdir(p): return []
    return [f for f in os.listdir(p) if f.lower().endswith(".pdf")]

print("=== 외국인 전용 모집요강 PDF (전체 드라이브, 학교별 중복제거) ===")
for prog, pairs in FOLDERS.items():
    for (folder, year, sub) in pairs:
        files = list_pdf(folder, sub)
        schools = set()
        for f in files:
            s = norm_school(f)
            schools.add(s)
        print(f"  {prog} {year}: 파일 {len(files)} / 고유학교 {len(schools)}")
