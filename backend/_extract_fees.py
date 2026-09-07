#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extract application fee (전형료/접수비/응시료/지원비) and admission fee (입학금)
amounts from every 2027 foreigner guide."""
import os, re, pymupdf

DIR = r"C:/Users/USER/내 드라이브/02_Crawling_Sheet/University_Project/adiga_2027_외국인_모집요강/외국인"
OUT = r"C:\Users\USER\camnemi-crm\backend\_fees_extracted.json"

results = {}
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
    name = re.sub(r"\[.*?\]", "", parts[1]) if len(parts) > 2 else fn

    # 1) application fee: 전형료/접수비/응시료/지원비 + amount
    app_fee = []
    for kw in ["전형료", "접수비", "응시료", "지원비"]:
        for m in re.finditer(kw, full):
            ctx = full[max(0, m.start() - 40):m.start() + 80]
            ctx = re.sub(r"\s+", " ", ctx)
            # require amount >= 1000 (skip page numbers like '7원')
            amt = re.findall(r"(\d{1,3}(?:,\d{3})*)\s*(?:원|KRW)", ctx)
            amt = [a for a in amt if int(a.replace(",", "")) >= 1000]
            if amt and amt[0] not in [a for a, _ in app_fee]:
                app_fee.append((amt[0], ctx.strip()[:70]))
            if len(app_fee) >= 2:
                break
        if len(app_fee) >= 2:
            break

    # 2) admission fee: 입학금
    adm_fee = []
    for m in re.finditer("입학금", full):
        ctx = full[max(0, m.start() - 30):m.start() + 70]
        ctx = re.sub(r"\s+", " ", ctx)
        if "면제" in ctx:
            adm_fee.append(("0", "면제 " + ctx[:50]))
            break
        amt = re.findall(r"(\d{1,3}(?:,\d{3})*)\s*원", ctx)
        amt = [a for a in amt if int(a.replace(",", "")) >= 1000]
        if amt:
            adm_fee.append((amt[0], ctx.strip()[:70]))
            break

    if app_fee or adm_fee:
        results[name] = {"app_fee": app_fee, "admission_fee": adm_fee}

import json
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"전형료/입학금 추출 학교: {len(results)}개")
for name, info in results.items():
    ap = info["app_fee"][:1]
    ad = info["admission_fee"][:1]
    ap_s = "전형료 " + ap[0][0] + "원" if ap else ""
    ad_s = "입학금 " + ad[0][0] + "원" if ad else ""
    print("  " + name + ": " + ap_s + " | " + ad_s)
