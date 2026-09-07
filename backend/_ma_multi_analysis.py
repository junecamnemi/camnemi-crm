#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Multi-condition master's analysis from _ma_rich.json: region, tuition, rank, major filter."""
import json, re
from collections import defaultdict

with open(r"C:\Users\USER\camnemi-crm\backend\_ma_rich.json", encoding="utf-8") as f:
    schools = json.load(f)

# ---- 1. by region ----
print("=" * 60)
print("1. 지역별 석사 학교 & 등록금")
print("=" * 60)
by_region = defaultdict(list)
for s in schools:
    by_region[s["loc"]].append(s)
for reg in ["서울특별시", "경기도", "인천광역시", "부산광역시", "대구광역시", "대전광역시", "광주광역시", "울산광역시"]:
    if reg in by_region:
        items = by_region[reg]
        tup = [s for s in items if s["tuition_min"]]
        if tup:
            low = min(s["tuition_min"] for s in tup)
            high = max(s["tuition_min"] for s in tup)
            print(f"  {reg}: {len(items)}개교, 등록금 {low:,}~{high:,}")
        else:
            print(f"  {reg}: {len(items)}개교")

# other regions
print("\n  기타 지역:")
for reg, items in sorted(by_region.items()):
    if reg not in ["서울특별시", "경기도", "인천광역시", "부산광역시", "대구광역시", "대전광역시", "광주광역시", "울산광역시"]:
        tup = [s for s in items if s["tuition_min"]]
        rng = f", {min(s['tuition_min'] for s in tup):,}~{max(s['tuition_min'] for s in tup):,}" if tup else ""
        print(f"  {reg}: {len(items)}개교{rng}")

# ---- 2. by tuition ----
print("\n" + "=" * 60)
print("2. 석사 등록금 (학기당)")
print("=" * 60)
with_t = sorted([s for s in schools if s["tuition_min"]], key=lambda s: s["tuition_min"])
print(f"\n  [저렴한 10개] (국립대 위주)")
for s in with_t[:10]:
    print(f"    {s['name']:<14} {s['loc']:<8} {s['tuition_min']:,}")
print(f"\n  [비싼 10개]")
for s in with_t[-10:]:
    print(f"    {s['name']:<14} {s['loc']:<8} {s['tuition_min']:,}")

# ---- 3. ranked schools ----
print("\n" + "=" * 60)
print("3. 랭크 있는 석사 학교")
print("=" * 60)
ranked = [s for s in schools if s["rank"] not in (None, "-", "")]
def rk(s):
    try:
        return int(re.sub(r"[^0-9]", "", str(s["rank"])))
    except:
        return 999
ranked.sort(key=rk)
for s in ranked:
    tu = f"{s['tuition_min']:,}" if s["tuition_min"] else "?"
    print(f"    #{s['rank']:<3} {s['name']:<12} {s['loc']:<8} 등록금 {tu}")

# ---- 4. major filter ----
print("\n" + "=" * 60)
print("4. 전공별 필터 (데이터/컴퓨터/경영)")
print("=" * 60)
KEYWORDS = {
    "데이터/통계": ["데이터", "통계", "빅데이터"],
    "컴퓨터/AI/SW": ["컴퓨터", "소프트웨어", "인공지능", "AI", "정보통신"],
    "경영/경제": ["경영", "경제", "금융", "무역"],
}
for label, kws in KEYWORDS.items():
    print(f"\n  [{label}]")
    def rk_key(x):
        try:
            return int(re.sub(r"[^0-9]", "", str(x["rank"]))) if x["rank"] not in (None, "-", "") else 999
        except:
            return 999
    for s in sorted(schools, key=rk_key):
        matched = [m for m in s["majors"] if any(k in m for k in kws)]
        if matched:
            tu = f"{s['tuition_min']:,}" if s["tuition_min"] else "?"
            print(f"    {s['name']} ({s['loc']}) 등록금 {tu} | {matched[0]} 외 {len(matched)-1}개")
