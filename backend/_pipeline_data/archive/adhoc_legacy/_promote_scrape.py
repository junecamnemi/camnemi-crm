#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Promote verified guide URLs into scrape_map.json (review-approved Tier A)."""
import json, os, datetime

B = r"C:\Users\wisew\camnemi-crm\backend"
ver = json.load(open(os.path.join(B, "_scrape_verified.json"), encoding="utf-8"))
sm = json.load(open(os.path.join(B, "scrape_map.json"), encoding="utf-8"))
today = datetime.date.today().isoformat()

added = 0
for school, lv in ver.items():
    for level, info in lv.items():
        if info.get("ok") and info.get("url"):
            sm.setdefault(school, {})[level] = {"url": info["url"],
                                                "verified": today,
                                                "note": f"{info['note']}",
                                                "tier": "A"}
            added += 1
json.dump(sm, open(os.path.join(B, "scrape_map.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
n_map = sum(len(v) for k, v in sm.items() if k != "_meta")
print(f"scrape_map에 확정: {added}건 | 총 매핑 {n_map}")
# show
for lvl in ["ba", "ma", "junior", "lang"]:
    c = sum(1 for s, lv in sm.items() if s != "_meta" and lvl in lv)
    print(f"  [{lvl}] {c}개")