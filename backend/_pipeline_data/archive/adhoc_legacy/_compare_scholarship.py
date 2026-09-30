# -*- coding: utf-8 -*-
"""Compare Opus scholarships vs Pro scholarship_note for same schools."""
import json

opus = {d["school"]: d for d in (json.loads(l) for l in open("_opus_full.jsonl", encoding="utf-8") if l.strip())}
pro = {d.get("school", ""): d for d in (json.loads(l) for l in open("guides_llm_parsed.jsonl", encoding="utf-8") if l.strip())}

overlap = set(opus) & set(pro)
print(f"겹치는 학교: {len(overlap)}")

# both have scholarship info
both = [s for s in overlap if opus[s].get("scholarships") and pro[s].get("scholarship_note")]
print(f"양쪽 장학금 보유: {len(both)}")

# compare content richness
print("\n=== 장학금 비교 샘플 (Opus vs Pro) ===")
for s in both[:8]:
    print(f"--- {s} ---")
    print(f"  Opus: {str(opus[s].get('scholarships'))[:200]}")
    print(f"  Pro : {str(pro[s].get('scholarship_note'))[:200]}")
