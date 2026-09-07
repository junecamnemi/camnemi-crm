#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Show the admission qualification (지원자격) block for schools where IELTS 5.5 wasn't found,
to determine if they accept IELTS 5.5 (English track) or only TOPIK (Korean track)."""
import os
import re
import pymupdf

DIR = r"C:/Users/USER/내 드라이브/02_Crawling_Sheet/University_Project/adiga_2027_외국인_모집요강/외국인"

pdf_files = {}
for fn in os.listdir(DIR):
    m = re.match(r"^\d+_(.+?)(?:\[.*?\])?_20\d+_외국인\.pdf$", fn)
    if m:
        pdf_files.setdefault(m.group(1), fn)

focus = ["숙명여자대학교","연세대학교","국립경국대학교","국립창원대학교","덕성여자대학교",
         "서울여자대학교","제주대학교","청주대학교","영남대학교","가톨릭관동대학교","고려대학교"]

for school in focus:
    fn = pdf_files.get(school)
    if not fn:
        print(f"=== {school}: PDF 없음 ==="); print()
        continue
    doc = pymupdf.open(os.path.join(DIR, fn))
    full = "\n".join(p.get_text() for p in doc)
    doc.close()
    # find 지원자격 section
    idx = -1
    for pat in ["지원자격", "지원 자격", "가. 지원자격", "1. 지원자격"]:
        idx = full.find(pat)
        if idx != -1:
            break
    print(f"=== {school} (지원자격 섹션) ===")
    if idx == -1:
        print("  (지원자격 섹션 없음)")
    else:
        seg = full[idx: idx+1100].replace("\n", " ")
        # collapse multiple spaces
        seg = re.sub(r"\s+", " ", seg)
        print(" ", seg[:950])
    print()
