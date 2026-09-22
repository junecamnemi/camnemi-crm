# -*- coding: utf-8 -*-
"""Compare Opus vs Pro parsing for the same schools — flag discrepancies."""
import json

opus = {d["school"]: d for d in (json.loads(l) for l in open("_opus_full.jsonl", encoding="utf-8") if l.strip())}
pro = {d.get("school", ""): d for d in (json.loads(l) for l in open("guides_llm_parsed.jsonl", encoding="utf-8") if l.strip())}

overlap = set(opus) & set(pro)
print(f"겹치는 학교: {len(overlap)}")

def norm(v):
    if v is None: return ""
    s = str(v).strip().lower()
    return s

def compare_field(school, field):
    o = norm(opus[school].get(field))
    p = norm(pro[school].get(field))
    if o and p and o != p:
        return True
    return False

# count discrepancies per field
fields = ["topik_req", "ielts_req", "toefl_req", "tuition_semester", "period"]
print("\n=== 필드별 불일치 (Opus vs Pro) ===")
for f in fields:
    n = sum(1 for s in overlap if compare_field(s, f))
    print(f"  {f}: {n}/{len(overlap)} 불일치")

# show examples of topik/ielts discrepancies
print("\n=== TOPIK/IELTS 불일치 예시 ===")
shown = 0
for s in overlap:
    if compare_field(s, "topik_req") or compare_field(s, "ielts_req"):
        print(f"  {s}: Opus(topik={opus[s].get('topik_req')}, ielts={opus[s].get('ielts_req')}) vs Pro(topik={pro[s].get('topik_req')}, ielts={pro[s].get('ielts_req')})")
        shown += 1
        if shown >= 15: break
