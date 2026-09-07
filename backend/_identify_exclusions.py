#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Identify schools to EXCLUDE from analysis:
1. 신학대/교육대 (theological colleges, education universities)
2. Student count < 2000 (from data.js stu field)
Outputs a report + exclusion list."""
import re, json

with open(r"C:\Users\USER\camnemi-crm\data.js", encoding="utf-8") as f:
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

# patterns for theological/education colleges
THEO_PAT = re.compile(
    r"(신학대|장신대|성서대|침례신학|감리교신학|루터대|총신대|성결대|한국교원|교육대|신학)"
)
# Catholic univs are comprehensive universities - keep them, only exclude if explicitly 신학대
CATHOLIC_KEEP = ["가톨릭대학교", "대구가톨릭대학교", "부산가톨릭대학교", "가톨릭꽃동네대학교"]

theo_edu = []
small = []
for u in data:
    n = u.get("n", "")
    if n in CATHOLIC_KEEP:
        continue
    if THEO_PAT.search(n):
        theo_edu.append((n, u.get("type", ""), u.get("stu")))

    stu = u.get("stu")
    if stu is not None and stu < 2000:
        small.append((n, u.get("type", ""), stu))

print(f"=== 신학대/교육대 제외 후보: {len(theo_edu)}개 ===")
for n, t, s in theo_edu:
    print(f"  {n} [{t}] 학생수={s}")

print(f"\n=== 학생수 2000명 미만 제외 후보: {len(small)}개 ===")
for n, t, s in small:
    print(f"  {n} [{t}] 학생수={s}")

# save report
import os
out = {
    "theo_edu": [{"name": n, "type": t, "stu": s} for n, t, s in theo_edu],
    "small": [{"name": n, "type": t, "stu": s} for n, t, s in small],
}
with open(r"C:\Users\USER\camnemi-crm\backend\_exclusion_report.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
print(f"\n저장: backend/_exclusion_report.json")
