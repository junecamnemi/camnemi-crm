#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extract ALL master's (석사) data from data.js: majors, tuition, cert. Then categorize."""
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

# Collect schools with MA data
ma_list = []
for u in data:
    nm = u.get("n", "")
    ma_majors = u.get("majors_ma") or []
    tu_ma = (u.get("tuition") or {}).get("ma") or {}
    cert = u.get("cert") or {}
    if ma_majors or tu_ma:
        # extract tuition min/max
        tmin = tu_ma.get("min") if tu_ma else None
        tmax = tu_ma.get("max") if tu_ma else None
        ma_list.append({
            "name": nm,
            "rank": u.get("rank", "-"),
            "region": u.get("region", ""),
            "n_majors": len(ma_majors) if isinstance(ma_majors, list) else 0,
            "tuition_min": tmin,
            "tuition_max": tmax,
            "cert_lang": cert.get("language", False),
            "foreign_pct": cert.get("foreign_pct", ""),
        })

print(f"총 {len(ma_list)}개 학교에 석사 데이터 존재")
print(f"석사 전공 수: {sum(s['n_majors'] for s in ma_list)}")
print(f"등록금(최소) 있는 학교: {sum(1 for s in ma_list if s['tuition_min'])}")
print(f"등록금(최대) 있는 학교: {sum(1 for s in ma_list if s['tuition_max'])}")

# Save to JSON for further analysis
with open(r"C:\Users\USER\camnemi-crm\backend\_ma_raw.json", "w", encoding="utf-8") as f:
    json.dump(ma_list, f, ensure_ascii=False, indent=2)
print("\n저장 완료: backend/_ma_raw.json")

# Show top schools by rank with MA data
ranked = [s for s in ma_list if str(s["rank"]).startswith("#")]
ranked.sort(key=lambda s: int(s["rank"].replace("#", "")))
print("\n=== 랭크 있는 학교 (석사) ===")
for s in ranked[:25]:
    print(f"  {s['name']} [#{s['rank']}] ({s['region']}) - 전공 {s['n_majors']}개, 등록금 {s['tuition_min']}~{s['tuition_max']}")
