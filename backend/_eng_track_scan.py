#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extract English-track majors from every 2027 foreigner guide PDF.
English track = majors listed under 영어트랙 / English Track / 영어전형 sections,
or majors with English-taught program (영어강의)."""
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
        results[school] = {"error": str(e)}
        continue

    # Strategy: find section headers indicating English track, then capture majors after
    # Patterns for English track indicators
    eng_headers = []
    lines = full.split("\n")
    for i, line in enumerate(lines):
        l = line.strip()
        if re.search(r"영어\s*트랙|영어트랙|English\s*Track|영어\s*전형|영어전형|영어강의|English\s*-?taught|영어\s*강의", l) or "ENG" in l.upper() and "트랙" in l:
            ctx = " ".join(x.strip() for x in lines[i:i+3])
            eng_headers.append({"line": l, "ctx": ctx[:120], "idx": i})

    # Also detect '영어' as a track column in 모집단위 tables
    # Look for majors that appear near '영어트랙' or 'English' column
    eng_majors = []
    for h in eng_headers:
        idx = h["idx"]
        # capture 5-15 lines after the header until a non-major boundary
        for j in range(idx+1, min(idx+20, len(lines))):
            lj = lines[j].strip()
            if not lj:
                continue
            # stop if we hit another section header
            if re.search(r"제출서류|지원자격|전형일정|전형료|합격자|모집인원|기타|문의|참고", lj) and len(lj) < 30:
                break
            # major-like line: contains Korean + optional English dept
            if re.search(r"[가-힣]{2,}(학과|학부|전공|대학|과)$", lj) or "(" in lj or ")" in lj:
                if lj not in eng_majors:
                    eng_majors.append(lj)

    results[school] = {
        "file": fn,
        "eng_headers": eng_headers[:5],
        "eng_majors": eng_majors[:20],
    }

# Save
with open(r"C:\Users\USER\camnemi-crm\backend\_eng_track_majors.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

# Print summary: schools with english track
print("== 영어트랙 감지된 학교 ==")
for s, v in sorted(results.items()):
    if v.get("eng_headers"):
        print(f"\n■ {s} ({len(v['eng_majors'])} 학과 추출)")
        for m in v["eng_majors"][:8]:
            print(f"   · {m[:80]}")
print("\n\n== 영어트랙 미감지 ==")
for s, v in sorted(results.items()):
    if not v.get("eng_headers") and not v.get("error"):
        print(f"   - {s}")
