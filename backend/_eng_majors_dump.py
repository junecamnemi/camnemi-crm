#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""For each verified school, dump the 모집단위 section lines that contain English-track markers
(ENG, 영어트랙, ◉, 영어, English) so we can list the exact English-track majors."""
import os
import re
import pymupdf
import json

DIR = r"C:/Users/USER/내 드라이브/02_Crawling_Sheet/University_Project/adiga_2027_외국인_모집요강/외국인"

pdf_files = {}
for fn in os.listdir(DIR):
    m = re.match(r"^\d+_(.+?)(?:\[.*?\])?_20\d+_외국인\.pdf$", fn)
    if m:
        pdf_files.setdefault(m.group(1), fn)

FOCUS = ["인하대학교","숙명여자대학교","가천대학교","계명대학교","단국대학교","목원대학교",
         "배재대학교","우송대학교","을지대학교","인제대학교","한서대학교","중앙대학교","경남대학교","경동대학교"]

for school in FOCUS:
    fn = pdf_files.get(school)
    if not fn:
        continue
    doc = pymupdf.open(os.path.join(DIR, fn))
    full = "\n".join(p.get_text() for p in doc)
    doc.close()
    lines = full.split("\n")

    # Collect major-like lines that carry an English-track marker
    hits = []
    for i, line in enumerate(lines):
        l = line.strip()
        if len(l) > 100 or not l:
            continue
        # has a major name
        is_major = re.search(r"[가-힣]{2,}(학과|학부|전공|대학)", l) or ("(" in l and ")" in l)
        has_eng = re.search(r"ENG|영어트랙|영어\(|\(영어|◉|English|영어", l)
        if is_major and has_eng:
            hits.append(l)

    print(f"\n===== {school} — 영어트랙 학과 후보 {len(hits)}개 =====")
    for h in hits[:15]:
        print(f"   {h[:80]}")
