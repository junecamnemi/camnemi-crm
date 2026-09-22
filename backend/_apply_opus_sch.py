# -*- coding: utf-8 -*-
"""Apply Opus scholarship results into verified_kb as scholarships_categorized.
For each school in _opus_sch_sample.jsonl, set scholarships_categorized from
Opus's structured scholarships array (name/condition/benefit)."""
import json, os

BASE = r"C:\Users\USER\camnemi-crm\backend"
KB = os.path.join(BASE, "verified_kb.json")
SAMPLE = os.path.join(BASE, "_opus_sch_sample.jsonl")

kb = json.load(open(KB, encoding="utf-8"))
recs = [json.loads(l) for l in open(SAMPLE, encoding="utf-8") if l.strip()]

def find_section(school, program):
    sec_map = {"ba": ("schools", None), "ma": ("master", "schools"),
               "junior": ("junior", "schools")}
    sec, sub = sec_map.get(program, ("schools", None))
    try:
        d = kb[sec][sub] if sub else kb[sec]
    except Exception:
        return None, None
    for k in d:
        if school in k or k in school:
            return sec, k
    return None, None

updated = 0
for r in recs:
    if not r.get("opus_scholarships"):
        continue
    sec, key = find_section(r["school"], r.get("program", "ba"))
    if not key:
        print(f"  {r['school']}: KB 매칭 실패")
        continue
    if sec == "schools":
        d = kb["schools"][key]
    else:
        d = kb[sec]["schools"][key]
    # build categorized scholarships
    cats = []
    for s in r["opus_scholarships"]:
        cats.append({"name": s.get("name", ""), "condition": s.get("condition", ""),
                     "benefit": s.get("benefit", ""), "type": "enroll", "category": "academic"})
    d["scholarships_categorized"] = cats
    d["scholarship_source"] = "opus"
    updated += 1
    print(f"  {r['school']} -> {sec}/{key} 장학금 {len(cats)}개")

json.dump(kb, open(KB, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"KB 장학금 업데이트: {updated}교")
