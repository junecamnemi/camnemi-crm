#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extract exact English-track majors from all 2027 foreigner PDFs, more thoroughly.
Handles: (ENG) tag, 영어트랙 section tables, English-track major lists."""
import os
import re
import json
import pymupdf

DIR = r"C:/Users/USER/내 드라이브/02_Crawling_Sheet/University_Project/adiga_2027_외국인_모집요강/외국인"

results = {}
for fn in sorted(os.listdir(DIR)):
    if not fn.lower().endswith(".pdf"):
        continue
    m = re.match(r"^\d+_(.+?)(?:\[.*?\])?_20\d+_외국인\.pdf$", fn)
    school = m.group(1) if m else fn.replace(".pdf", "")
    try:
        doc = pymupdf.open(os.path.join(DIR, fn))
        full = "\n".join(p.get_text() for p in doc)
        doc.close()
    except Exception as e:
        continue

    lines = full.split("\n")
    eng_majors = set()
    eng_ctx = []

    # 1) Find "영어트랙" / "English Track" section and capture majors listed near it
    for i, line in enumerate(lines):
        l = line.strip()
        if re.search(r"영어트랙|English\s*Track|영어\s*트랙", l) and len(l) < 80:
            eng_ctx.append(" ".join(x.strip() for x in lines[max(0,i-2):i+15])[:200])

    # 2) Majors explicitly tagged (ENG) or (영어)
    for i, line in enumerate(lines):
        l = line.strip()
        if len(l) > 90 or not l:
            continue
        # tagged with (ENG) / (영어) / 영어전용 etc, and looks like a major
        if re.search(r"\(ENG\)|\(영어\)|\(English\)", l):
            # clean the major name
            nm = re.sub(r"\s*\(ENG\)|\s*\(영어\)|\s*\(English\)", "", l).strip()
            if re.search(r"[가-힣]{2,}", nm):
                eng_majors.add(nm)
        # major lines inside a 영어트랙 block
        elif re.search(r"영어트랙", l):
            # nearby major-like lines (next 8 lines)
            for j in range(i+1, min(i+8, len(lines))):
                lj = lines[j].strip()
                if len(lj) > 90 or not lj:
                    continue
                if re.search(r"[가-힣]{2,}(학과|학부|전공|대학)", lj) and not re.search(r"제출|서류|지원|장학|등록금|전형|합격|모집인원", lj):
                    eng_majors.add(lj)

    # 3) Deduplicate and filter obvious non-majors
    cleaned = []
    for nm in eng_majors:
        if re.search(r"[가-힣]{2,}(학과|학부|전공|대학)", nm) and len(nm) < 40:
            if nm not in cleaned:
                cleaned.append(nm)

    results[school] = {
        "eng_ctx": eng_ctx[:2],
        "majors": cleaned[:25],
    }

with open(r"C:\Users\USER\camnemi-crm\backend\_eng_all.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

# Print schools with eng majors
for s in sorted(results):
    v = results[s]
    if v["majors"]:
        print(f"\n■ {s} — {len(v['majors'])}개")
        for mm in v["majors"]:
            print(f"   · {mm}")
