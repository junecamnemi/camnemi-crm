#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Categorize every scholarship in data.js into: 입학(enroll)/재학(existing) × 성적(academic)/어학(language)/기타.
Writes _scholarship_categorized.json + adds a 'category' to each scholarship for KB/PDF output."""
import json, re, os

DATA_FILE = r"C:\Users\USER\camnemi-crm\data.js"
OUT = r"C:\Users\USER\camnemi-crm\backend\_scholarship_categorized.json"

with open(DATA_FILE, encoding="utf-8") as f:
    content = f.read()
start = content.find("[")
depth = 0
for i in range(start, len(content)):
    if content[i] == "[":
        depth += 1
    elif content[i] == "]":
        depth -= 1
        if depth == 0:
            data = json.loads(content[start : i + 1])
            break

# keyword rules
ACADEMIC_KW = ["성적", "학점", "GPA", "우수", "성적우수", "수석", "최우수"]
LANG_KW = ["TOPIK", "IELTS", "TOEFL", "어학", "영어", "한국어", "TEPS", "TOEIC", "언어"]
ENROLL_KW = ["입학", "신입", "신입학", "편입"]
EXISTING_KW = ["재학", "성적우수장학", "재학생"]

def categorize(name, tiers, typ):
    """Return (type, category) where category ∈ academic/language/both/general."""
    hay = name
    for t in (tiers or []):
        hay += " " + str(t.get("score_type", "")) + " " + str(t.get("score", ""))
    hay += " " + (typ or "")

    is_acad = any(k in hay for k in ACADEMIC_KW)
    is_lang = any(k in hay for k in LANG_KW)

    if is_acad and is_lang:
        cat = "both"
    elif is_acad:
        cat = "academic"
    elif is_lang:
        cat = "language"
    else:
        cat = "general"

    # type: enroll vs existing
    if typ in ("enroll", "existing"):
        t = typ
    elif any(k in name for k in ENROLL_KW):
        t = "enroll"
    elif any(k in name for k in EXISTING_KW):
        t = "existing"
    else:
        t = typ or "general"
    return t, cat

result = {}
summary = {"enroll": {"academic": 0, "language": 0, "both": 0, "general": 0},
           "existing": {"academic": 0, "language": 0, "both": 0, "general": 0}}

for u in data:
    nm = u.get("n", "")
    schs = []
    for s in (u.get("scholarships") or []):
        t, cat = categorize(s.get("name", ""), s.get("tiers"), s.get("type"))
        entry = dict(s)
        entry["type"] = t
        entry["category"] = cat
        schs.append(entry)
        if t in summary and cat in summary[t]:
            summary[t][cat] += 1
    if schs:
        result[nm] = schs

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("=== 장학금 분류 요약 ===")
for t, cats in summary.items():
    total = sum(cats.values())
    print(f"[{t}] 총 {total}개")
    for c, n in cats.items():
        print(f"   {c}: {n}")
print(f"\n분류된 학교 수: {len(result)}")
print(f"저장: {OUT}")
