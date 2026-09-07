#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Parse scholarships into enroll (입학장학금) and existing (재학장학금) for all PDF schools."""
import re
import json

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
            data = json.loads(content[start:i + 1])
            break

# PDF schools
SCHOOLS = [
    "중앙대학교","인하대학교","숙명여자대학교","가천대학교","광운대학교","한양대학교","한경국립대학교",
    "단국대학교","계명대학교","전북대학교","목원대학교","배재대학교","우송대학교","을지대학교",
    "인제대학교","선문대학교","한동대학교","고신대학교","동신대학교","중원대학교","창신대학교",
    "제주국제대학교","한일장신대학교","평택대학교","한국외국어대학교","세종대학교","건국대학교","한림대학교"
]

def fmt_tiers(tiers, max_n=3):
    if not tiers:
        return ""
    parts = []
    for t in tiers[:max_n]:
        st = t.get("score_type", "")
        sc = t.get("score", "")
        amt = t.get("amount", "")
        cond = f"{st} {sc}".strip()
        parts.append(f"{cond}→{amt}" if cond else f"{amt}")
    s = " / ".join(parts)
    if len(tiers) > max_n:
        s += f" (외 {len(tiers)-max_n}단계)"
    return s

result = {}
for u in data:
    nm = u.get("n")
    if nm not in SCHOOLS:
        continue
    # match 한양대 ERICA -> main 한양대 may not exist; check
    sched = u.get("scholarships") or []
    enroll = []
    existing = []
    for s in sched:
        if s.get("type") == "enroll":
            enroll.append(f"{s.get('name','')}: {fmt_tiers(s.get('tiers') or [])}")
        elif s.get("type") == "existing":
            existing.append(f"{s.get('name','')}: {fmt_tiers(s.get('tiers') or [])}")
    result[nm] = {
        "enroll": enroll[:3],
        "existing": existing[:3],
    }

# Save
with open(r"C:\Users\USER\camnemi-crm\backend\_scholarship_parsed.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

for nm in SCHOOLS:
    r = result.get(nm)
    if not r:
        print(f"■ {nm}: (data 없음)")
        continue
    print(f"\n■ {nm}")
    print("  [입학장학금]")
    for e in r["enroll"]:
        print(f"    · {e[:120]}")
    print("  [재학장학금]")
    for e in r["existing"]:
        print(f"    · {e[:120]}")
