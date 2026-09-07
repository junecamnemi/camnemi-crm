#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extract English-track majors + their language requirements for ALL 2027 foreigner PDFs,
focusing on schools I previously missed (경희, 광운, 한양ERICA, 한경국립, 서울대, 연세, 경북 등)."""
import os
import re
import json
import pymupdf

DIR = r"C:/Users/USER/내 드라이브/02_Crawling_Sheet/University_Project/adiga_2027_외국인_모집요강/외국인"

FOCUS = ["경희대학교","광운대학교","한양대학교(ERICA)","한경국립대학교","서울대학교","연세대학교",
         "경북대학교","선문대학교","한동대학교","고신대학교","영남대학교","동신대학교","중원대학교",
         "창신대학교","제주국제대학교","한일장신대학교","성균관대학교","고려대학교"]

pdf_files = {}
for fn in os.listdir(DIR):
    m = re.match(r"^\d+_(.+?)(?:\[.*?\])?_20\d+_외국인\.pdf$", fn)
    if m:
        pdf_files.setdefault(m.group(1), fn)

for school in FOCUS:
    fn = pdf_files.get(school)
    if not fn:
        print(f"===== {school}: PDF 없음 =====")
        continue
    doc = pymupdf.open(os.path.join(DIR, fn))
    full = "\n".join(p.get_text() for p in doc)
    doc.close()

    lines = full.split("\n")
    print(f"===== {school} =====")

    # 1) English track major sections - dump 모집단위 area around 영어트랙
    eng_blocks = []
    for i, line in enumerate(lines):
        l = line.strip()
        if re.search(r"영어트랙|영어\s*트랙|English\s*Track", l) and len(l) < 80:
            block = " ".join(x.strip() for x in lines[max(0,i-3):i+25])
            eng_blocks.append(block[:350])

    # 2) IELTS / English requirement context
    ielts_ctx = []
    for m in re.finditer(r"IELTS", full):
        ctx = full[max(0,m.start()-50):m.start()+60].replace("\n", " ")
        ielts_ctx.append(re.sub(r"\s+", " ", ctx)[:110])

    # 3) ENG-tagged majors
    eng_majors = []
    for i, line in enumerate(lines):
        l = line.strip()
        if len(l) > 90:
            continue
        if re.search(r"\(ENG\)|\(영어\)|\(English\)|◉", l) and re.search(r"[가-힣]{2,}(학과|학부|전공|대학)|[A-Za-z]+학과", l):
            eng_majors.append(l[:80])

    print(f"  [영어트랙 블록]")
    for b in eng_blocks[:2]:
        print(f"    {b}")
    print(f"  [IELTS 언급]")
    for c in ielts_ctx[:3]:
        print(f"    {c}")
    print(f"  [ENG 표기 학과]")
    for mm in eng_majors[:10]:
        print(f"    {mm}")
    print()
