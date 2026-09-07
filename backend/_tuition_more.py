#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Search for tuition amount tables (등록금 책정표 / 수업료) in each guide, looking
for lines with '원' or '￦' amounts that are tuition (not fees/dormitory)."""
import os
import re
import pymupdf

DIR_ADIGA = r"C:/Users/USER/내 드라이브/02_Crawling_Sheet/University_Project/adiga_2027_외국인_모집요강/외국인"

targets = {
    "숙명여대": "0000141_숙명여자대학교[본교]_2027_외국인.pdf",
    "목원대": "0000112_목원대학교[본교]_2027_외국인.pdf",
    "배재대": "0000113_배재대학교[본교]_2027_외국인.pdf",
    "우송대": "0000240_우송대학교[본교]_2027_외국인.pdf",
    "을지대": "0000161_을지대학교[본교]_2027_외국인.pdf",
    "인제대": "0000164_인제대학교[본교]_2027_외국인.pdf",
    "동신대": "0000104_동신대학교[본교]_2027_외국인.pdf",
    "창신대": "0000249_창신대학교[본교]_2027_외국인.pdf",
    "한일장신대": "0000206_한일장신대학교[본교]_2027_외국인.pdf",
}

# Amounts that look like tuition (3~10 million won)
AMT = re.compile(r"(\d{1,3}(?:,\d{3})+)\s*원")
for label, fn in targets.items():
    path = os.path.join(DIR_ADIGA, fn)
    if not os.path.exists(path):
        print(f"{label}: PDF 없음")
        continue
    doc = pymupdf.open(path)
    full = "\n".join(p.get_text() for p in doc)
    doc.close()
    hits = []
    for m in AMT.finditer(full):
        v = m.group(1).replace(",", "")
        if 2_000_000 <= int(v) <= 12_000_000:  # plausible tuition range
            ctx = full[max(0,m.start()-60):m.start()+30].replace("\n", " ")
            ctx = re.sub(r"\s+", " ", ctx)
            hits.append(f"{m.group(0)} | {ctx[:90]}")
    print(f"\n===== {label} — 등록금 후보 =====")
    if not hits:
        print("  (2~12백만원 금액 없음)")
    else:
        seen = set()
        for h in hits:
            if h[:20] not in seen:
                seen.add(h[:20])
                print(f"  · {h}")
