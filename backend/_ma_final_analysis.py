#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build a comprehensive MASTER'S (석사) analysis CSV covering:
school, region, rank, majors, tuition, guide status, guide URL, language req (general), scholarship (general).
Saves to backend/master_analysis.csv for instant replies."""
import json, re, csv
from collections import defaultdict

with open(r"C:\Users\USER\camnemi-crm\backend\_ma_rich.json", encoding="utf-8") as f:
    schools = json.load(f)

# Load MA guide status/URLs from batches
ma_guide = {}
import glob
for fn in glob.glob(r"C:\Users\USER\camnemi-crm\backend\_ma_batches\MA_batch_*_result.json") + \
          glob.glob(r"C:\Users\USER\camnemi-crm\backend\_ma_batches\MA_fill_*_result.json"):
    try:
        with open(fn, encoding="utf-8") as f:
            r = json.load(f)
        if isinstance(r, list):
            for item in r:
                if isinstance(item, dict) and item.get("school"):
                    ma_guide[item["school"]] = item
    except Exception:
        pass

# General MA language req by tier (from verified research)
# 영어트랙: IELTS 5.5~6.5 / 한국어트랙: TOPIK 3~4급
def lang_requirement(rank):
    """Master's general language requirement — english track IELTS, korean track TOPIK"""
    # Most master's: TOPIK 3-4 for korean track, IELTS 5.5-6.5 for english track
    return "한국어트랙 TOPIK 3~4 / 영어트랙 IELTS 5.5~6.5 (학과별 상이)"

rows = []
for s in schools:
    guide = ma_guide.get(s["name"], {})
    status = guide.get("status", "unknown")
    url = guide.get("url", "")
    tu = s["tuition_min"]
    tmax = s["tuition_max"]
    majors_str = ", ".join(s["majors"][:6])
    if len(s["majors"]) > 6:
        majors_str += f" 외 {len(s['majors'])-6}개"
    rows.append({
        "school": s["name"],
        "region": s["loc"],
        "rank": s["rank"],
        "n_majors": len(s["majors"]),
        "majors": majors_str,
        "tuition_min": tu,
        "tuition_max": tmax,
        "guide_status": status,
        "guide_url": url,
        "lang_req": lang_requirement(s["rank"]),
    })

# Sort by rank then tuition
def rk_key(r):
    try:
        return (0, int(re.sub(r"[^0-9]", "", str(r["rank"])))) if r["rank"] not in (None, "-", "") else (1, 999)
    except:
        return (1, 999)

rows.sort(key=rk_key)

# Write CSV
out = r"C:\Users\USER\camnemi-crm\backend\master_analysis.csv"
with open(out, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["school","region","rank","n_majors","majors","tuition_min","tuition_max","guide_status","guide_url","lang_req"])
    w.writeheader()
    w.writerows(rows)

print(f"석사 분석 CSV 저장: {out} ({len(rows)}개 학교)")
print("\n=== 요약 ===")
print(f"총 {len(rows)}개 학교")
print(f"  - 랭크 있는: {sum(1 for r in rows if r['rank'] not in ('','-'))}개")
print(f"  - 등록금 있음: {sum(1 for r in rows if r['tuition_min'])}개")
print(f"  - 2027 요강: {sum(1 for r in rows if '2027' in r['guide_status'])}개")
print(f"  - 2026 이하: {sum(1 for r in rows if '2026' in r['guide_status'] or 'unknown' in r['guide_status'])}개")

# Region summary
by_reg = defaultdict(list)
for r in rows:
    by_reg[r["region"]].append(r)
print("\n=== 지역별 ===")
for reg, items in sorted(by_reg.items(), key=lambda kv: -len(kv[1])):
    tus = [i["tuition_min"] for i in items if i["tuition_min"]]
    rng = f", {min(tus):,}~{max(tus):,}" if tus else ""
    print(f"  {reg}: {len(items)}개교{rng}")

# Guide status distribution
from collections import Counter
print("\n=== 요강 상태 분포 ===")
for st, cnt in Counter(r["guide_status"] for r in rows).most_common():
    print(f"  {st}: {cnt}개")
