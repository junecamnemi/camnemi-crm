#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Precisely extract English-track majors from each verified 2027 foreigner guide.
Looks for the admission-unit table rows tagged with 영어트랙/영어/ENG, and for
schools with explicit English-track programs, lists the tracked majors."""
import os
import re
import json
import pymupdf

DIR = r"C:/Users/USER/내 드라이브/02_Crawling_Sheet/University_Project/adiga_2027_외국인_모집요강/외국인"

pdf_files = {}
for fn in os.listdir(DIR):
    m = re.match(r"^\d+_(.+?)(?:\[.*?\])?_20\d+_외국인\.pdf$", fn)
    if m:
        pdf_files.setdefault(m.group(1), fn)

# Focus: 2027 verified schools (those with english track from our analysis)
FOCUS = ["중앙대학교","인하대학교","숙명여자대학교","가천대학교","경남대학교","경동대학교",
         "계명대학교","단국대학교","목원대학교","배재대학교","우송대학교","을지대학교","인제대학교",
         "한서대학교","평택대학교","건양대학교","연세대학교","고려대학교","성균관대학교","경희대학교",
         "광운대학교","한양대학교","서울대학교"]

out = {}
for school in FOCUS:
    fn = pdf_files.get(school)
    if not fn:
        out[school] = {"error": "PDF 없음"}
        continue
    try:
        doc = pymupdf.open(os.path.join(DIR, fn))
        full = "\n".join(p.get_text() for p in doc)
        doc.close()
    except Exception as e:
        out[school] = {"error": str(e)}
        continue

    lines = full.split("\n")
    eng_majors = []
    eng_ctx = []

    # Pass 1: find lines containing '영어트랙' or '영어 트랙' or 'ENG' track markers
    for i, line in enumerate(lines):
        l = line.strip()
        if re.search(r"영어\s*트랙", l) and len(l) < 60:
            # This line is a header; majors may be on next lines or same line
            ctx = " ".join(x.strip() for x in lines[i:i+6])
            eng_ctx.append(ctx[:150])

    # Pass 2: find table rows where a major is tagged as English track.
    # Look for '영어' adjacent to a major name, or majors in an English-track column
    for i, line in enumerate(lines):
        l = line.strip()
        if not l:
            continue
        # major name pattern: Korean text ending in 학과/학부/전공, possibly with (ENG)/(영어)
        if re.search(r"[가-힣][가-힣 ]{1,20}(학과|학부|전공|대학)", l) or "(" in l:
            # check same line or adjacent for 영어/ENG
            adj = " ".join(x.strip() for x in lines[max(0,i-1):i+2])
            if re.search(r"영어|ENG|English", adj):
                if l not in eng_majors and len(l) < 100:
                    eng_majors.append(l)

    out[school] = {
        "eng_ctx": eng_ctx[:3],
        "eng_majors": eng_majors[:20],
    }

# Save
with open(r"C:\Users\USER\camnemi-crm\backend\_eng_track_precise.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

for s in FOCUS:
    v = out.get(s, {})
    if v.get("error"):
        print(f"{s}: {v['error']}")
        continue
    print(f"\n■ {s} — 영어트랙 학과 {len(v['eng_majors'])}개")
    for m in v["eng_majors"]:
        print(f"   · {m[:70]}")
