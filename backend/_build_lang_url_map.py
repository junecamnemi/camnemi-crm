#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build a consolidated language-school (어학당) URL map: 4-year univs (master lang_src)
+ junior colleges (KB lang_src). Also flags anomalous junior lang tuition."""
import json, os, csv

BASE = r"C:\Users\USER\camnemi-crm\backend"
OUT_CSV = os.path.join(BASE, "language_school_urls.csv")
OUT_JSON = os.path.join(BASE, "language_school_urls.json")

# 4-year from master
with open(os.path.join(BASE, "_guide_2027_master.json"), encoding="utf-8") as f:
    master = json.load(f)

# junior from KB
with open(os.path.join(BASE, "verified_kb.json"), encoding="utf-8") as f:
    kb = json.load(f)
junior = kb.get("junior", {}).get("schools", {})

rows = []
seen = set()

# 4-year univs
for r in master:
    url = r.get("lang_src") or ""
    nm = r.get("school", "")
    if url and nm not in seen:
        seen.add(nm)
        rows.append({
            "school": nm, "type": "4-year", "region": r.get("region", ""),
            "lang_url": url, "status": r.get("lang_status", ""),
        })

# junior colleges
for nm, s in junior.items():
    url = s.get("lang_src") or ""
    if url and nm not in seen:
        seen.add(nm)
        rows.append({
            "school": nm, "type": "junior", "region": s.get("region", ""),
            "lang_url": url, "status": "2026",
        })

# sort
rows.sort(key=lambda x: (x["type"], x["school"]))

# write CSV
with open(OUT_CSV, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["school", "type", "region", "lang_url", "status"])
    w.writeheader()
    w.writerows(rows)

# write JSON
with open(OUT_JSON, "w", encoding="utf-8") as f:
    json.dump(rows, f, ensure_ascii=False, indent=2)

n4 = sum(1 for r in rows if r["type"] == "4-year")
nj = sum(1 for r in rows if r["type"] == "junior")
print(f"언어학교 URL 통합 완료: 4년제 {n4}개 + 전문대학 {nj}개 = {len(rows)}개")
print(f"CSV: {OUT_CSV}")
print(f"JSON: {OUT_JSON}")

# flag anomalous junior lang tuition (likely per-hour or corrupted)
print("\n=== 비정상 전문대학 어학 등록금 (확인 필요) ===")
for nm, s in junior.items():
    t = s.get("tuition_semester", "") or ""
    if t and ("2,024" in t or "1,200" in t or "2,024원" in t):
        print(f"  ⚠️ {nm}: {t}")
