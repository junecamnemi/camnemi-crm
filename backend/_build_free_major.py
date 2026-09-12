# -*- coding: utf-8 -*-
"""Rebuild free_major_programs with refined category detection:
- free_major: 자유전공/자율전공/무전공/미전공/글로벌자유전공/전공자율/자유학부
- intl_stem: 국제이공/글로벌(IT|공학|과학|테크)/국제(공학|이공)
- intl: 국제학부/글로벌학부/국제융합학부/글로벌융합학부(경영·인문)
- convergence: 융합학부/융합전공
- broad: 광역/계열모집/단일계열"""
import json, re

KB_PATH = r"C:\Users\USER\camnemi-crm\backend\verified_kb.json"
kb = json.load(open(KB_PATH, encoding="utf-8"))

def classify(unit):
    u = unit
    cats=set()
    if re.search(r"(자유전공|자율전공|(?<![사])무전공|전공자율|자유학부|글로벌자유전공)", u) or u.strip() in ("무전공","자유전공","자율전공"): cats.add("free_major")
    if re.search(r"(국제이공|글로벌\s*(IT|공학|과학|테크|SW|소프트)|국제\s*(공학|이공|과학))", u, re.I): cats.add("intl_stem")
    if re.search(r"(국제학부|글로벌학부|국제융합학부|글로벌융합학부|국제학과)", u): cats.add("intl")
    if "융합" in u: cats.add("convergence")
    if re.search(r"(광역|계열모집|단일계열)", u): cats.add("broad")
    return sorted(cats)

def split_units(majors):
    if isinstance(majors, list): items=[str(m) for m in majors]
    else: items=re.split(r"[/\n·]", str(majors))
    return [i.strip().strip("'\"") for i in items if i.strip()]

schools_out={}
for n, v in kb["schools"].items():
    majors = v.get("majors") or v.get("majors_sample") or []
    units=[]
    for it in split_units(majors):
        cats = classify(it)
        if cats: units.append({"name": it[:80], "category": cats})
    if not units: continue
    schools_out[n] = {
        "name": n,
        "loc": v.get("region") or v.get("loc") or "",
        "topik_req": v.get("topik_req"),
        "ielts_req": v.get("ielts_req"),
        "english_track": bool(re.search(r"영어|English|100%|IELTS|트랙", str(majors))),
        "units": units,
    }

kb["free_major_programs"] = {
    "note": "자유전공·자율전공·무전공·국제이공학부·글로벌자유전공·국제/글로벌학부·광역/융합학부 — 전공 미정 선발 후 전공 선택 가능한 모집단위. 상담 시 '전공 아직 못 정한 학생', '국제이공/영어트랙' 질문에 활용. english_track=True면 영어 지원 가능. category: free_major(자유전공) / intl_stem(국제이공·글로벌IT·공학) / intl(국제·글로벌학부) / convergence(융합) / broad(광역).",
    "updated": "2026-09-10",
    "schools": schools_out,
}
json.dump(kb, open(KB_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

from collections import Counter
c=Counter()
for s in schools_out.values():
    for u in s["units"]:
        for cat in u["category"]: c[cat]+=1
print(f"free_major_programs: {len(schools_out)} schools")
print("category counts:", dict(c))
print()
print("=== intl_stem (국제이공·글로벌IT) ===")
for n,s in schools_out.items():
    for u in s["units"]:
        if "intl_stem" in u["category"]: print(f"  {n}: {u['name']}")
print()
print("=== free_major 샘플 ===")
cnt=0
for n,s in schools_out.items():
    for u in s["units"]:
        if "free_major" in u["category"]:
            print(f"  {n}: {u['name']}"); cnt+=1
    if cnt>20: break
