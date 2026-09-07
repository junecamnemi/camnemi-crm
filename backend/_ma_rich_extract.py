#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Comprehensive master's (석사) analysis: region, rank(rk), tuition, language req, majors."""
import re, json
from collections import defaultdict

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

def get_ielts_min(req):
    """extract min IELTS from req structure or note"""
    vals = []
    def walk(x):
        if isinstance(x, dict):
            for v in x.values():
                walk(v)
        elif isinstance(x, str):
            m = re.findall(r"IELTS\s*(\d+\.?\d*)", x)
            vals.extend(float(v) for v in m)
        elif isinstance(x, list):
            for v in x:
                walk(v)
    walk(req)
    return min(vals) if vals else None

def get_topik_min(req):
    vals = []
    def walk(x):
        if isinstance(x, dict):
            for v in x.values():
                walk(v)
        elif isinstance(x, str):
            m = re.findall(r"TOPIK\s*(\d+)", x)
            vals.extend(int(v) for v in m)
        elif isinstance(x, list):
            for v in x:
                walk(v)
    walk(req)
    return min(vals) if vals else None

# collect all MA schools with rich info
ma = []
for u in data:
    nm = u.get("n", "")
    ma_majors = u.get("majors_ma") or []
    tu_ma = (u.get("tuition") or {}).get("ma") or {}
    if not (ma_majors or tu_ma):
        continue
    req = u.get("req") or {}
    # req may have per-level structure
    ielts_min = get_ielts_min(req)
    topik_min = get_topik_min(req)
    ma.append({
        "name": nm,
        "loc": u.get("loc", ""),
        "rank": u.get("rk", "-"),
        "majors": [m.get("kr", "") for m in ma_majors] if isinstance(ma_majors, list) else [],
        "tuition_min": tu_ma.get("min"),
        "tuition_max": tu_ma.get("max"),
        "tuition_fields": tu_ma.get("fields"),
        "ielts_min": ielts_min,
        "topik_min": topik_min,
    })

# Filter: need MA majors (not just tuition)
with_majors = [s for s in ma if s["majors"]]
print(f"석사 데이터: 총 {len(ma)}, 전공 있는 {len(with_majors)}개")

# Save rich MA data
with open(r"C:\Users\USER\camnemi-crm\backend\_ma_rich.json", "w", encoding="utf-8") as f:
    json.dump(with_majors, f, ensure_ascii=False, indent=2)

# Ranked schools
ranked = [s for s in with_majors if s["rank"] not in (None, "-", "")]
def rk_key(s):
    try:
        return int(re.sub(r"[^0-9]", "", str(s["rank"])))
    except:
        return 999
ranked.sort(key=rk_key)
print(f"\n=== 랭크 있는 석사 학교 ({len(ranked)}개) ===")
for s in ranked[:30]:
    print(f"  {s['name']:<16} rk={s['rank']:<4} {s['loc']:<8} 전공{s['n_majors'] if False else len(s['majors']):>3}개 IELTS={s['ielts_min']} TOPIK={s['topik_min']} 등록금={s['tuition_min']}")
