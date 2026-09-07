#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Analyze Kyungwoon Univ 2026 foreigner guide: majors, schedule, lang req, scholarship."""
import pymupdf, re

doc = pymupdf.open(r"C:\Users\USER\camnemi-crm\backend\_guide_pdfs\kyungwoon_2026.pdf")
full = "\n".join(p.get_text() for p in doc)
doc.close()
print("총 chars:", len(full))

# 1. 모집단위/학과
print("\n=== 모집단위(학과) 키워드 검색 ===")
idx = full.find("모집단위")
if idx == -1:
    idx = full.find("모집학과")
if idx == -1:
    idx = full.find("학과")
print(full[max(0,idx-50):idx+1200].replace("\n", " ")[:1200])

# 2. 전형일정
print("\n=== 전형일정 ===")
for kw in ["원서접수", "모집기간", "접수기간", "전형일정"]:
    i = full.find(kw)
    if i >= 0:
        print(f"[{kw}] {full[max(0,i-30):i+250].replace(chr(10),' ')[:250]}")
        print()

# 3. 어학능력
print("=== 어학능력(지원자격) ===")
for kw in ["IELTS", "TOPIK", "어학능력", "지원자격"]:
    for m in list(re.finditer(kw, full))[:2]:
        print(f"  {full[max(0,m.start()-50):m.start()+120].replace(chr(10),' ')[:160]}")
        print()
