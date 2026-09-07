#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Search for actual tuition amounts (₩X,XXX,XXX / X,XXX,XXX원) in each guide PDF."""
import os
import re
import pymupdf

DIR_ADIGA = r"C:/Users/USER/내 드라이브/02_Crawling_Sheet/University_Project/adiga_2027_외국인_모집요강/외국인"
DIR_GUIDE = r"C:\Users\USER\camnemi-crm\backend\_guide_pdfs"

targets = {
    "인하대학교": os.path.join(DIR_ADIGA, "0000169_인하대학교[본교]_2027_외국인.pdf"),
    "숙명여자대학교": os.path.join(DIR_ADIGA, "0000141_숙명여자대학교[본교]_2027_외국인.pdf"),
    "광운대학교": os.path.join(DIR_ADIGA, "0000074_광운대학교[본교]_2027_외국인.pdf"),
    "한양대학교(ERICA)": os.path.join(DIR_ADIGA, "0000204_한양대학교(ERICA)[분교]_2027_외국인.pdf"),
    "목원대학교": os.path.join(DIR_ADIGA, "0000112_목원대학교[본교]_2027_외국인.pdf"),
    "배재대학교": os.path.join(DIR_ADIGA, "0000113_배재대학교[본교]_2027_외국인.pdf"),
    "우송대학교": os.path.join(DIR_ADIGA, "0000240_우송대학교[본교]_2027_외국인.pdf"),
    "을지대학교": os.path.join(DIR_ADIGA, "0000161_을지대학교[본교]_2027_외국인.pdf"),
    "인제대학교": os.path.join(DIR_ADIGA, "0000164_인제대학교[본교]_2027_외국인.pdf"),
    "동신대학교": os.path.join(DIR_ADIGA, "0000104_동신대학교[본교]_2027_외국인.pdf"),
    "창신대학교": os.path.join(DIR_ADIGA, "0000249_창신대학교[본교]_2027_외국인.pdf"),
    "한일장신대학교": os.path.join(DIR_ADIGA, "0000206_한일장신대학교[본교]_2027_외국인.pdf"),
}

# Amount pattern: 3,000,000 / 3.000.000 / 3000000 / ₩
AMT = re.compile(r"(?:₩|￦)?\s*\d{1,3}(?:[,.]\d{3})+(?:\s*원)?")

for school, path in targets.items():
    if not os.path.exists(path):
        continue
    doc = pymupdf.open(path)
    full = "\n".join(p.get_text() for p in doc)
    doc.close()
    amounts = set()
    for m in AMT.finditer(full):
        ctx = full[max(0,m.start()-40):m.start()+30].replace("\n", " ")
        ctx = re.sub(r"\s+", " ", ctx)
        # filter out dates / phone / page numbers
        v = m.group(0).replace(",", "").replace(".", "").replace("₩","").replace("￦","").replace("원","").strip()
        if v.isdigit() and len(v) >= 6:  # >= 100,000
            amounts.add(f"{m.group(0)} | {ctx[:70]}")
    print(f"\n===== {school} — 금액 후보 =====")
    if not amounts:
        print("  (금액 없음)")
    else:
        for a in sorted(amounts)[:8]:
            print(f"  · {a}")
