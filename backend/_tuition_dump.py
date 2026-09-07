#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dump ALL amount-like text from each guide, with more context, to find tuition tables."""
import os
import re
import pymupdf

DIR_ADIGA = r"C:/Users/USER/내 드라이브/02_Crawling_Sheet/University_Project/adiga_2027_외국인_모집요강/외국인"

targets = {
    "숙명여대": "0000141_숙명여자대학교[본교]_2027_외국인.pdf",
    "인제대": "0000164_인제대학교[본교]_2027_외국인.pdf",
    "을지대": "0000161_을지대학교[본교]_2027_외국인.pdf",
    "목원대": "0000112_목원대학교[본교]_2027_외국인.pdf",
}

for label, fn in targets.items():
    path = os.path.join(DIR_ADIGA, fn)
    doc = pymupdf.open(path)
    full = "\n".join(p.get_text() for p in doc)
    doc.close()
    print(f"\n{'='*50}\n{label} — 금액 포함 줄 전체 (3자리 콤마 숫자)")
    # find any comma-number >= 100000
    for line in full.split("\n"):
        if re.search(r"\d{1,3},\d{3}", line):
            line = line.strip()
            if re.search(r"(원|￦|등록금|수업료|학비)", line):
                print(f"  {line[:100]}")
