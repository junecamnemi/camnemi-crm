#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Precise extraction of application periods for the 15 schools where regex failed,
plus year disambiguation for the mixed/unknown schools."""
import os
import re
import json
import pymupdf

DIR = r"C:/Users/USER/내 드라이브/02_Crawling_Sheet/University_Project/adiga_2027_외국인_모집요강/외국인"

# Load prior scan
with open(r"C:\Users\USER\camnemi-crm\backend\_deep_verify.json", encoding="utf-8") as f:
    prior = json.load(f)

# Focus schools needing period extraction or year check
focus = [s for s, v in prior.items() if not v.get("period") or v.get("year") in ("?", "2027(혼재)", "2027(추정)", "2026")]

DATE_PAT = re.compile(
    r"(?:20\d{2}\s*[.\-/년]\s*)?\d{1,2}\s*[.\-/월]\s*\d{1,2}"
    r"(?:\s*[\(（]\s*[월화수목금토일]\s*[\)）])?"
    r"(?:\s*[~∼\-–]\s*(?:20\d{2}\s*[.\-/년]\s*)?\d{1,2}\s*[.\-/월]\s*\d{1,2}"
    r"(?:\s*[\(（]\s*[월화수목금토일]\s*[\)）])?)?"
)

for fn in sorted(os.listdir(DIR)):
    if not fn.lower().endswith(".pdf"):
        continue
    m = re.match(r"^\d+_(.+?)(?:\[.*?\])?_20\d+_외국인\.pdf$", fn)
    school = m.group(1) if m else fn.replace(".pdf", "")
    if school not in focus:
        continue
    try:
        doc = pymupdf.open(os.path.join(DIR, fn))
        pages = [p.get_text() for p in doc]
        doc.close()
    except Exception as e:
        print(school, "ERR", e)
        continue
    full = "\n".join(pages)

    # Year: search the WHOLE doc for 학년도 markers, count occurrences
    n2027 = len(re.findall(r"2027\s*학년도", full))
    n2026 = len(re.findall(r"2026\s*학년도", full))
    # also 2027/2026 followed by 전기/후기/1학기 etc
    n2027b = len(re.findall(r"2027\s*[년]*\s*[전후]?[기]?\s*\(?\s*[0-9]월", full))
    n2026b = len(re.findall(r"2026\s*[년]*\s*[전후]?[기]?\s*\(?\s*[0-9]월", full))
    year = "2027" if (n2027 + n2027b) > (n2026 + n2026b) else ("2026" if (n2026 + n2026b) > 0 else "?")

    # Period: search for the FIRST real 원서접수 row with an actual date range
    lines = full.split("\n")
    period = None
    for i, line in enumerate(lines):
        if not re.search(r"원서\s*접수|접수\s*기간|모집\s*일정|전형\s*일정|입학\s*지원서|인터넷\s*접수|접수\s*일정|온라인\s*접수", line):
            continue
        ctx = " ".join(x.strip() for x in lines[i:i+5])
        dates = DATE_PAT.findall(ctx)
        real = []
        for d in dates:
            d = d.strip()
            if re.match(r"^\d{1,2}\s*-\s*\d{1,2}$", d):
                continue
            if re.match(r"^\d{1,2}\s*\.\s*\d{1,2}$", d) and not any(x in d for x in ["~", "–", "∼", "-"]):
                continue
            if re.search(r"20\d{2}", d) or any(x in d for x in ["~", "–", "∼"]):
                real.append(d)
        if real:
            period = real[:4]
            ctx_snip = ctx[:160]
            break
    print(f"{school}: year={year} (2027x{n2027+n2027b}, 2026x{n2026+n2026b}) | period={period}")
    if period:
        print(f"    ctx: {ctx_snip}")
