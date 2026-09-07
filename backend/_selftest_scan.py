#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Find which majors are eligible via 자체시험 (own Korean test) in each verified 2027 foreigner guide.
Goal: confirm whether 자체시험 is limited to specific majors (as user suspects)."""
import os, re, pymupdf

DIR = r"C:/Users/USER/내 드라이브/02_Crawling_Sheet/University_Project/adiga_2027_외국인_모집요강/외국인"

# key schools that have selftest=true AND we have their PDF
TARGETS = ["건국대", "인하대", "세종대", "한국외국어대", "고려대", "동국대", "숭실대", "서울시립대",
           "광운대", "한양", "경희대", "단국대", "국민대", "가천대", "숙명여자"]

def extract_school(fn):
    m = re.match(r"\d+_(.+?)(?:\[.*\])?_", fn)
    return m.group(1) if m else fn

for fn in sorted(os.listdir(DIR)):
    if not fn.endswith(".pdf"):
        continue
    school = extract_school(fn)
    if not any(t in school for t in TARGETS):
        continue
    doc = pymupdf.open(os.path.join(DIR, fn))
    full = "\n".join(p.get_text() for p in doc)
    doc.close()

    # find 자체시험 / 자체 한국어 / 자체시험응시 관련 mentions
    hits = []
    for m in re.finditer(r"자체시험|자체 한국어|자체한국어", full):
        ctx = full[max(0, m.start()-80):m.start()+120].replace("\n", " ")
        ctx = re.sub(r"\s+", " ", ctx)
        hits.append(ctx[:180])
    if hits:
        print(f"\n===== {school} — 자체시험 언급 =====")
        for h in hits[:4]:
            print(f"  · {h}")
