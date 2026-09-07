#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Correct school name extraction + list schools accepting IELTS 5.0 or TOPIK-only."""
import os
import re
import pymupdf

DIR = r"C:/Users/USER/내 드라이브/02_Crawling_Sheet/University_Project/adiga_2027_외국인_모집요강/외국인"

IELTS = re.compile(r"IELTS\s*(\d+\.?\d*)")
TOEFL = re.compile(r"TOEFL(?:\s*iBT)?\s*(\d+)")

# sample filenames to understand pattern
fns = sorted(os.listdir(DIR))[:5]
print("파일명 예시:")
for f in fns:
    print("  ", f)

def extract_school(fn):
    # pattern: 0000063_가천대학교[본교]_2027_외국인.pdf
    m = re.match(r"\d+_(.+?)(?:\[.*\])?_(\d{4})_외국인\.pdf", fn)
    if m:
        return m.group(1)
    # fallback
    return fn.split("_")[0]

print("\n=== 결과 ===")
low_ielts = []
topik_only = []
all_schools = []
for fn in sorted(os.listdir(DIR)):
    if not fn.endswith(".pdf"):
        continue
    school = extract_school(fn)
    doc = pymupdf.open(os.path.join(DIR, fn))
    full = "\n".join(p.get_text() for p in doc)
    doc.close()

    ielts_vals = [float(x) for x in IELTS.findall(full)]
    min_ielts = min(ielts_vals) if ielts_vals else None
    toefl_vals = [int(x) for x in TOEFL.findall(full)]
    min_toefl = min(toefl_vals) if toefl_vals else None
    has_topik = bool(re.search(r"TOPIK\s*\d", full))

    all_schools.append((school, min_ielts, min_toefl, has_topik))
    if min_ielts is not None and min_ielts <= 5.0:
        low_ielts.append((school, min_ielts, min_toefl))
    if min_ielts is None and min_toefl is None and has_topik:
        topik_only.append(school)

print("\n### IELTS 5.0 이하 허용 학교:")
for s in low_ielts:
    print(f"  {s[0]}: IELTS {s[1]}, TOEFL {s[2]}")

print(f"\n### 영어요건 없음 + TOPIK만 요구 (영어불필요) — {len(topik_only)}개:")
for s in sorted(topik_only):
    print(f"  {s}")
