#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Scan all 2027 foreigner guides for 입학금 (admission fee) and 지원비/응시료 (application fee) policies.
Goal: classify each university's fee structure for foreign freshmen:
  - 입학금 면제 / 부과 / 등록금에 포함
  - 지원비(응시료) 금액
"""
import os, re, pymupdf

DIR = r"C:/Users/USER/내 드라이브/02_Crawling_Sheet/University_Project/adiga_2027_외국인_모집요강/외국인"

print("=== 입학금 / 지원비 정책 스캔 ===")
for fn in sorted(os.listdir(DIR)):
    if not fn.endswith(".pdf"):
        continue
    try:
        doc = pymupdf.open(os.path.join(DIR, fn))
        full = "\n".join(p.get_text() for p in doc)
        doc.close()
    except Exception:
        continue

    parts = fn.split("_")
    name = parts[1] if len(parts) > 2 else fn
    name = re.sub(r"\[.*?\]", "", name)

    # find 입학금 mentions
    fee_parts = []
    for m in re.finditer(r"[^.\n]{0,40}입학금[^.\n]{0,60}", full):
        ctx = re.sub(r"\s+", " ", m.group(0)).strip()
        if "면제" in ctx:
            fee_parts.append("면제:" + ctx[:80])
        elif "부과" in ctx or "납부" in ctx or "1,0" in ctx or "000원" in ctx:
            fee_parts.append("부과:" + ctx[:80])
    # find 지원비/응시료 amounts
    app_parts = []
    for m in re.finditer(r"[^.\n]{0,30}(?:지원비|응시료|접수비)[^.\n]{0,50}", full):
        ctx = re.sub(r"\s+", " ", m.group(0)).strip()
        if re.search(r"\d{2,3},?\d{2,3}", ctx) or "원" in ctx:
            app_parts.append(ctx[:90])

    if fee_parts or app_parts:
        print(f"\n▶ {name}")
        for p in fee_parts[:3]:
            print(f"   [입학금] {p}")
        for p in app_parts[:3]:
            print(f"   [지원비] {p}")
