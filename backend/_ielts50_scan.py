#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extract the minimum English (IELTS/TOEFL) requirement from every 2027 foreigner guide PDF,
to find schools that accept IELTS 5.0 or lower, OR have no strict English requirement
(TOPIK-only / English-medium high school graduates)."""
import os
import re
import pymupdf

DIR = r"C:/Users/USER/내 드라이브/02_Crawling_Sheet/University_Project/adiga_2027_외국인_모집요강/외국인"

IELTS = re.compile(r"IELTS\s*(\d+\.?\d*)")
TOEFL = re.compile(r"TOEFL(?:\s*iBT)?\s*(\d+)")

results = []
for fn in sorted(os.listdir(DIR)):
    if not fn.endswith(".pdf"):
        continue
    school = fn.split("_")[-2]
    doc = pymupdf.open(os.path.join(DIR, fn))
    full = "\n".join(p.get_text() for p in doc)
    doc.close()

    # find min IELTS
    ielts_vals = [float(x) for x in IELTS.findall(full)]
    min_ielts = min(ielts_vals) if ielts_vals else None
    toefl_vals = [int(x) for x in TOEFL.findall(full)]
    min_toefl = min(toefl_vals) if toefl_vals else None

    # check if TOPIK-only (no English req) or has alternatives
    has_topik = bool(re.search(r"TOPIK\s*\d", full))
    has_engmed = bool(re.search(r"영어\s*[가-힣]*\s*고등학교|영어로\s*(?:진행|수업|교육)", full))
    # filter out scholarship/dorm mentions of IELTS (higher values) - use any mention <=5.0
    accepts_low = min_ielts is not None and min_ielts <= 5.0
    no_eng_req = (min_ielts is None and min_toefl is None and has_topik)

    results.append((school, min_ielts, min_toefl, has_topik, no_eng_req, accepts_low, has_engmed))

print(f"{'학교':<20} {'최저IELTS':<10} {'최저TOEFL':<10} {'TOPIK':<6} {'영어불필요':<9} {'IELTS<=5':<8}")
print("-" * 75)
for school, mi, mt, ht, ner, al, hem in results:
    print(f"{school:<20} {str(mi):<10} {str(mt):<10} {'O' if ht else 'X':<6} {'O' if ner else 'X':<9} {'O' if al else 'X':<8}")

# save full detail for low-accepting schools
print("\n=== IELTS 5.0 이하 허용 또는 영어요건 없음(TOPIK만) 학교 ===")
for school, mi, mt, ht, ner, al, hem in results:
    if al or ner:
        print(f"  {school}: minIELTS={mi}, minTOEFL={mt}, TOPIK={ht}, ENGmed={hem}")
