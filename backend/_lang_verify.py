#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extract the actual language requirement (어학능력) for each shortlisted school,
including English-track acceptance, and flag schools whose DS majors require higher TOPIK."""
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

SHORTLIST = [
    "연세대학교","고려대학교","중앙대학교","인하대학교","가천대학교","가톨릭관동대학교",
    "경남대학교","경동대학교","계명대학교","국립경국대학교","국립창원대학교","단국대학교",
    "덕성여자대학교","목원대학교","배재대학교","서울여자대학교","숙명여자대학교","영남대학교",
    "우송대학교","을지대학교","인제대학교","제주대학교","청주대학교","평택대학교","한서대학교",
    "건양대학교",
]

out = {}
for school in SHORTLIST:
    fn = pdf_files.get(school)
    if not fn:
        out[school] = {"error": "PDF 없음"}
        continue
    doc = pymupdf.open(os.path.join(DIR, fn))
    full = "\n".join(p.get_text() for p in doc)
    doc.close()

    # Find 어학능력 / 언어능력 section content (not TOC). Search whole doc for the block.
    blocks = []
    for kw in ["어학 능력", "어학능력", "언어능력", "언어 능력"]:
        for mm in re.finditer(kw, full):
            start = mm.start()
            seg = full[start:start+700].replace("\n", " ")
            seg = re.sub(r"\s+", " ", seg)
            # skip TOC-like (contains '·····')
            if "·····" in seg or "···" in seg:
                continue
            blocks.append(seg[:600])
            break  # first real occurrence
        if blocks:
            break

    # IELTS min
    ielts = re.findall(r"IELTS\s*(?:[(\[])?\s*(\d+(?:\.\d+)?)", full, re.IGNORECASE)
    topik_req = re.findall(r"TOPIK(?:\s*\(?(?:PBT|IBT)\)?)?\s*(\d)급\s*이상", full)
    # DS major TOPIK 4 requirement (데이터, 컴퓨터, AI, 소프트웨어, 통계 + 4급)
    ds_topik4 = re.findall(r"([가-힣A-Za-z· ]{0,30}(?:데이터|컴퓨터|AI|인공지능|소프트웨어|통계)[가-힣A-Za-z· ]{0,20}):?\s*한국어능력시험\(?TOPIK\)?\s*(\d)급", full)

    out[school] = {
        "ielts_vals": sorted(set(ielts))[:5],
        "topik_levels": sorted(set(topik_req))[:5],
        "ds_topik4": ds_topik4[:3],
        "lang_block": blocks[0] if blocks else "",
    }

# Print
print("== 언어요건 정밀 확인 ==")
for s in SHORTLIST:
    r = out.get(s, {})
    if r.get("error"):
        print(f"  {s}: {r['error']}")
        continue
    ielts_ok55 = any(float(v) <= 5.5 for v in r["ielts_vals"]) if r["ielts_vals"] else False
    has_eng_track = bool(r["lang_block"]) and ("영어트랙" in r["lang_block"] or "영어" in r["lang_block"])
    print(f"  {s}: IELTS값={r['ielts_vals']} TOPIK급={r['topik_levels']} eng트랙={has_eng_track} ds_topik4={r['ds_topik4']}")
    if not r["ielts_vals"] and r["lang_block"]:
        print(f"      lang: {r['lang_block'][:180]}")

with open(r"C:\Users\USER\camnemi-crm\backend\_lang_verify.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
