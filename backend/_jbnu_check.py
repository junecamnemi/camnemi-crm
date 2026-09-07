#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pymupdf, re
doc = pymupdf.open(r"C:\Users\USER\camnemi-crm\backend\_guide_pdfs\jbnu_2026_spring.pdf")
full = "\n".join(p.get_text() for p in doc)
doc.close()

print("=== 전북대 2026 전기 국제이공학부 / 영어트랙 관련 ===")
seen = set()
for kw in ["국제이공", "글로벌융합", "영어트랙", "영어 트랙", "SIES", "영어로 진행", "영어강의", "International School"]:
    for m in re.finditer(re.escape(kw), full):
        ctx = full[max(0,m.start()-60):m.start()+110].replace("\n", " ")
        ctx = re.sub(r"\s+", " ", ctx)
        key = ctx[:50]
        if key not in seen:
            seen.add(key)
            print(f"[{kw}] {ctx[:140]}")
        if len(seen) > 25:
            break

print()
print("=== 모집단위 (영어 관련 학과 탐색) ===")
# Look for 모집단위 section and English-labeled majors
lines = full.split("\n")
for i, line in enumerate(lines):
    l = line.strip()
    if re.search(r"\(영어\)|\(ENG\)|English|영어트랙", l) and re.search(r"[가-힣]{2,}(학과|학부|전공)", l):
        print(f"  {l[:100]}")
