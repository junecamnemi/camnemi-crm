#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Analyze master's tuition: low/high, by region, by field."""
import json

with open(r"C:\Users\USER\camnemi-crm\backend\_ma_raw.json", encoding="utf-8") as f:
    ma = json.load(f)

with_tuition = [s for s in ma if s["tuition_min"]]
print(f"석사 등록금(최소) 있는 학교: {len(with_tuition)}개")

with_tuition.sort(key=lambda s: s["tuition_min"])
print("\n=== 석사 등록금 낮은 순 (학기당, 원) ===")
for s in with_tuition[:25]:
    tmax = f"{s['tuition_max']:,}" if s["tuition_max"] else "-"
    print(f"  {s['name']:<18} {s['tuition_min']:>12,} ~ {tmax}")

print("\n=== 석사 등록금 높은 순 ===")
for s in with_tuition[-12:]:
    tmax = f"{s['tuition_max']:,}" if s["tuition_max"] else "-"
    print(f"  {s['name']:<18} {s['tuition_min']:>12,} ~ {tmax}")

# By region
print("\n=== 지역별 석사 등록금 평균 ===")
from collections import defaultdict
region_tuition = defaultdict(list)
for s in with_tuition:
    region_tuition[s["region"]].append(s["tuition_min"])
for reg, vals in sorted(region_tuition.items(), key=lambda kv: sum(kv[1])/len(kv[1])):
    avg = sum(vals) / len(vals)
    print(f"  {reg}: 평균 {avg:,.0f} ({len(vals)}개교, 최저 {min(vals):,})")

# Schools with many MA majors (broad programs)
print("\n=== 석사 전공 많은 학교 (전공 수 상위 15) ===")
by_major = sorted(ma, key=lambda s: s["n_majors"], reverse=True)
for s in by_major[:15]:
    print(f"  {s['name']}: {s['n_majors']}개 전공, 등록금 {s['tuition_min'] or '-'}")
