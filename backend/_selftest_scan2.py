#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""1) Find '자체' (own-test) mentions in all guide PDFs + 2) list majors for selftest schools."""
import os, re, pymupdf

DIR = r"C:/Users/USER/내 드라이브/02_Crawling_Sheet/University_Project/adiga_2027_외국인_모집요강/외국인"

print("=" * 60)
print("1. 요강 PDF에서 '자체시험/자체 한국어' 문구 검색")
print("=" * 60)
def extract_school(fn):
    m = re.match(r"\d+_(.+?)(?:\[.*\])?_", fn)
    return m.group(1) if m else fn

for fn in sorted(os.listdir(DIR)):
    if not fn.endswith(".pdf"):
        continue
    school = extract_school(fn)
    doc = pymupdf.open(os.path.join(DIR, fn))
    full = "\n".join(p.get_text() for p in doc)
    doc.close()
    # search for any 자체 문구
    hits = []
    for m in re.finditer(r"자체", full):
        ctx = full[max(0, m.start()-30):m.start()+60].replace("\n", " ")
        ctx = re.sub(r"\s+", " ", ctx)
        hits.append(ctx)
    # filter meaningful (한국어시험/시험/면접 관련)
    meaningful = [h for h in hits if any(k in h for k in ["시험", "면접", "한국어", "평가", "응시"])]
    if meaningful:
        print(f"\n===== {school} =====")
        seen = set()
        for h in meaningful[:3]:
            if h[:25] not in seen:
                seen.add(h[:25])
                print(f"  · {h[:150]}")
