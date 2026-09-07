#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Scan all local adiga 2027 foreigner PDFs for an actual application period (전형일정/모집기간/원서접수).
Uses pymupdf for reliable Korean text extraction."""
import os
import re
import json

DIR = r"C:/Users/USER/내 드라이브/02_Crawling_Sheet/University_Project/adiga_2027_외국인_모집요강/외국인"

import pymupdf  # fitz

# keywords indicating schedule sections
SCHED_KW = ["전형일정", "모집일정", "원서접수", "접수기간", "모집기간", "지원일정", "일정"]

# date patterns commonly used: 2026. 7. 6(월) ~ 7. 10(금), 2026.07.06 ~ 2026.07.10, 2026.9.22.(화) ~ 10.3.(금)
DATE_RE = re.compile(
    r"(?:20\d{2}\s*[.\-년]\s*)?\d{1,2}\s*[.\-월]\s*\d{1,2}"
    r"(?:\s*[\(（]\s*[월화수목금토일]\s*[\)）])?"
    r"(?:\s*[~∼\-–]\s*(?:20\d{2}\s*[.\-년]\s*)?\d{1,2}\s*[.\-월]\s*\d{1,2}"
    r"(?:\s*[\(（]\s*[월화수목금토일]\s*[\)）])?)?"
)

def extract_text(path):
    try:
        doc = pymupdf.open(path)
        txt = ""
        for p in doc:
            txt += p.get_text()
        doc.close()
        return txt
    except Exception as e:
        return f"__ERR__ {e}"

results = {}
for fn in sorted(os.listdir(DIR)):
    if not fn.lower().endswith(".pdf"):
        continue
    path = os.path.join(DIR, fn)
    m = re.match(r"^\d+_(.+?)(?:\[.*?\])?_20\d+_외국인\.pdf$", fn)
    school = m.group(1) if m else fn
    txt = extract_text(path)
    if txt.startswith("__ERR__"):
        results[school] = {"file": fn, "error": txt}
        continue

    lines = txt.split("\n")
    found = []
    for i, line in enumerate(lines):
        if any(k in line for k in SCHED_KW):
            # gather context window
            ctx = " ".join(x.strip() for x in lines[max(0,i-1):i+6])
            dates = DATE_RE.findall(ctx)
            if dates:
                found.append({"kw": line.strip(), "ctx": ctx[:220], "dates": dates[:4]})
    has_period = bool(found)

    results[school] = {
        "file": fn,
        "has_period": has_period,
        "found": found[:3],
        "chars": len(txt),
    }

has = [s for s, v in results.items() if v.get("has_period")]
no = [s for s, v in results.items() if not v.get("has_period")]

print(f"PDF 총 {len(results)}개 | 모집기간 있음 {len(has)} | 모집기간 없음/미확인 {len(no)}")
print()
print("== 모집기간 있음 ==")
for s in sorted(has):
    v = results[s]
    for f in v["found"]:
        print(f"  {s}: [{f['kw']}] dates={f['dates']}")
        break
print()
print("== 모집기간 없음/미확인 ==")
for s in sorted(no):
    v = results[s]
    print(f"  {s}: {'ERROR' if v.get('error') else '기간 없음'} (chars={v.get('chars')})")

# save full detail for further use
with open(r"C:\Users\USER\camnemi-crm\backend\_period_scan.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
