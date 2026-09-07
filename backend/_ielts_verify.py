#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FINAL accuracy pass:
1. Verify IELTS 5.5 acceptance directly from each 2027 foreigner PDF (the actual requirement text).
2. Confirm year for every school in our shortlist.
3. Produce a verified master table."""
import os
import re
import json
import pymupdf

DIR = r"C:/Users/USER/내 드라이브/02_Crawling_Sheet/University_Project/adiga_2027_외국인_모집요강/외국인"

# The shortlist we care about (IELTS 5.5 + DS majors + foreigner track, 2027 candidates)
# from the verified analysis
SHORTLIST = [
    "연세대학교","고려대학교","중앙대학교","인하대학교","가천대학교","가톨릭관동대학교",
    "경남대학교","경동대학교","계명대학교","국립경국대학교","국립창원대학교","단국대학교",
    "덕성여자대학교","목원대학교","배재대학교","서울여자대학교","숙명여자대학교","영남대학교",
    "우송대학교","을지대학교","인제대학교","제주대학교","청주대학교","평택대학교","한서대학교",
    "건양대학교",
]

# Schools whose actual PDF we have
pdf_files = {}
for fn in os.listdir(DIR):
    m = re.match(r"^\d+_(.+?)(?:\[.*?\])?_20\d+_외국인\.pdf$", fn)
    if m:
        pdf_files.setdefault(m.group(1), fn)

IELTS_PAT = re.compile(
    r"IELTS\s*(?:\(|\[)?\s*(\d+(?:\.\d+)?)\s*(?:이상|점 이상|이상의|~|~이상)?",
    re.IGNORECASE
)

results = {}
for school in SHORTLIST:
    fn = pdf_files.get(school)
    if not fn:
        results[school] = {"error": "PDF 없음"}
        continue
    try:
        doc = pymupdf.open(os.path.join(DIR, fn))
        full = "\n".join(p.get_text() for p in doc)
        doc.close()
    except Exception as e:
        results[school] = {"error": str(e)}
        continue

    # Find all IELTS mentions with context
    ielts_mentions = []
    for mm in IELTS_PAT.finditer(full):
        score = mm.group(1)
        ctx = full[max(0, mm.start()-60): mm.start()+60].replace("\n", " ")
        ielts_mentions.append({"score": score, "ctx": ctx[:110]})
    # Also check TOPIK min
    topik_mentions = []
    for mm in re.finditer(r"TOPIK(?:\s*\(?(?:PBT|IBT)?\)?)?\s*(\d{1})급\s*이상", full):
        topik_mentions.append({"level": mm.group(1), "ctx": full[max(0, mm.start()-40): mm.start()+40].replace("\n", " ")[:90]})

    # Determine the admission language requirement section (지원자격)
    # Find the requirement block
    req_block = ""
    idx = full.find("지원자격")
    if idx == -1:
        idx = full.find("지원 자격")
    if idx != -1:
        req_block = full[idx: idx+1200].replace("\n", " ")[:900]

    results[school] = {
        "file": fn,
        "ielts_mentions": ielts_mentions[:5],
        "topik_mentions": topik_mentions[:5],
        "req_block": req_block,
    }

# Print summary: does any IELTS mention accept 5.5 (i.e., mention of 5.5 as min, or range including 5.5)?
print("== IELTS 5.5 수용 여부 (요강 내 IELTS 문구) ==")
for s in SHORTLIST:
    r = results.get(s, {})
    if r.get("error"):
        print(f"  {s}: {r['error']}")
        continue
    ms = r["ielts_mentions"]
    # check if any mention has score <= 5.5 (i.e. 5.5 or lower as requirement)
    accept55 = any(float(m["score"]) <= 5.5 for m in ms)
    print(f"  {s}: accept5.5={accept55} | mentions={[m['score'] for m in ms[:3]]}")
    if ms:
        print(f"      ex: {ms[0]['ctx']}")

with open(r"C:\Users\USER\camnemi-crm\backend\_ielts_verify.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
