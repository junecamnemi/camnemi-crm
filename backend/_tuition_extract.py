#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extract tuition (등록금) from the 2027 foreigner guides for schools missing it in data.js."""
import os
import re
import pymupdf

DIR_ADIGA = r"C:/Users/USER/내 드라이브/02_Crawling_Sheet/University_Project/adiga_2027_외국인_모집요강/외국인"
DIR_GUIDE = r"C:\Users\USER\camnemi-crm\backend\_guide_pdfs"

# school -> pdf path
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

for school, path in targets.items():
    if not os.path.exists(path):
        print(f"{school}: PDF 없음")
        continue
    doc = pymupdf.open(path)
    full = "\n".join(p.get_text() for p in doc)
    doc.close()

    # find 등록금 section - look for patterns like 000,000 or 0,000,000원
    idx = full.find("등록금")
    if idx == -1:
        idx = full.find("수업료")
    if idx == -1:
        idx = full.find("Tuition")
    print(f"\n===== {school} =====")
    if idx == -1:
        print("  (등록금/수업료 섹션 없음)")
        continue
    # print around the 등록금 section
    seg = full[idx:idx+900].replace("\n", " ")
    seg = re.sub(r"\s+", " ", seg)
    print(f"  {seg[:700]}")
