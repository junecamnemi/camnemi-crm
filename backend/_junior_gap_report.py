#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check whether the daily 2027 check + adiga scrape covers junior colleges.
Reports the current gap precisely (for the user's question)."""
import json, os, csv

BASE = r"C:\Users\USER\camnemi-crm\backend"

# 1. master report — does it include junior?
with open(os.path.join(BASE, "_guide_2027_master.json"), encoding="utf-8") as f:
    master = json.load(f)
types = {}
for r in master:
    t = r.get("type", "?")
    types[t] = types.get(t, 0) + 1
print("=== 1. _guide_2027_master.json ===")
print(f"  총 {len(master)}개 | 유형: {types}")

# 2. adiga scrape — does it include junior?
with open(r"C:/Users/USER/내 드라이브/02_Crawling_Sheet/University_Project/adiga_2027_외국인_모집요강/universities_2027.json", encoding="utf-8") as f:
    unis = json.load(f)
junior_names = ["전문대", "대학"]  # heuristic
junior_count = sum(1 for u in unis if "전문" in str(u))
print("\n=== 2. adiga 2027 스크레이퍼 대학 목록 ===")
print(f"  총 {len(unis)}개 | 전문대학 포함: {junior_count}개")

# 3. verified_kb junior section
with open(os.path.join(BASE, "verified_kb.json"), encoding="utf-8") as f:
    kb = json.load(f)
junior_kb = kb.get("junior", {}).get("schools", {})
print("\n=== 3. verified_kb.json (전문대학 KB) ===")
print(f"  전문대학 {len(junior_kb)}개")

# 4. how many junior have a guide status?
guide_map = kb.get("guide", {})
junior_with_guide = sum(1 for n in junior_kb if n in guide_map)
print(f"  가이드 맵에 있는 전문대학: {junior_with_guide}개")
if junior_with_guide:
    st = {}
    for n in junior_kb:
        if n in guide_map:
            s = guide_map[n].get("status", "?")
            st[s] = st.get(s, 0) + 1
    print(f"  상태 분포: {st}")
else:
    print("  → 전문대학은 가이드 수집 대상이 아님 (4년제만)")

print("\n=== 결론 ===")
print(f"현재 일일 2027 가이드 수집(크론)은 4년제 {len(master)}개만 대상.")
print(f"전문대학 {len(junior_kb)}개는 2027 가이드 수집에서 빠져있음.")
