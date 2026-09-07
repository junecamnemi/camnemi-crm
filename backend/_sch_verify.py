#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extract scholarship conditions from actual guides for schools with missing enroll conditions:
한국외대, 을지대, 배재대, 한양대(ERICA)."""
import pymupdf, re, os

DIR_ADIGA = r"C:/Users/USER/내 드라이브/02_Crawling_Sheet/University_Project/adiga_2027_외국인_모집요강/외국인"
DIR_GUIDE = r"C:\Users\USER\camnemi-crm\backend\_guide_pdfs"

targets = {
    "한국외대": os.path.join(DIR_GUIDE, "한국외대.pdf"),
    "을지대": os.path.join(DIR_ADIGA, "0000161_을지대학교[본교]_2027_외국인.pdf"),
    "배재대": os.path.join(DIR_ADIGA, "0000113_배재대학교[본교]_2027_외국인.pdf"),
    "한양ERICA": os.path.join(DIR_ADIGA, "0000204_한양대학교(ERICA)[분교]_2027_외국인.pdf"),
}

for label, path in targets.items():
    if not os.path.exists(path):
        print(f"===== {label}: PDF 없음 =====")
        continue
    doc = pymupdf.open(path)
    full = "\n".join(p.get_text() for p in doc)
    doc.close()
    print(f"\n{'='*60}\n===== {label} — 장학금 섹션 =====")
    # find scholarship section
    idx = full.find("장학")
    if idx == -1:
        print("  (장학 언급 없음)")
        continue
    # print blocks around each 장학금 mention
    count = 0
    for m in re.finditer(r"(입학장학|신입생|입학생|총장|학장|글로벌인재|언어능력|성적우수|입학학기|외국인)", full):
        ctx = full[max(0,m.start()-30):m.start()+150].replace("\n", " ")
        ctx = re.sub(r"\s+", " ", ctx)
        if "장학" in ctx and count < 12:
            print(f"  · {ctx[:170]}")
            count += 1
