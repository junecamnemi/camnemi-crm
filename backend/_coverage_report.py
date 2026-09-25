#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Coverage report: how many KB schools (per level) are monitored vs not.
Monitored = has scrape_map entry. Discovered = has a candidate in review batch (tier A/B)."""
import json, os, re
B = r"C:\Users\wisew\camnemi-crm\backend"
LEVEL_BASE = {"ba": ["schools", None], "ma": ["master","schools"], "junior": ["junior","schools"], "lang": ["lang_programs","schools"]}
kb = json.load(open(os.path.join(B, "verified_kb.json"), encoding="utf-8"))
sm = json.load(open(os.path.join(B, "scrape_map.json"), encoding="utf-8"))
batch = json.load(open(os.path.join(B, "_guide_review_batch.json"), encoding="utf-8"))

# map level key used in scrape_map / batch to the actual school key
def norm(s): return re.sub(r"\[.*?\]", "", str(s)).replace("대학교","대학").replace("대학","").strip()

# build discovery candidate lookup (school norm -> set of levels with candidate)
disc = {}
for c in batch["candidates"]:
    disc.setdefault(norm(c["school"]), set()).add(c["level"])

monitored = {}
for s, lv in sm.items():
    if s == "_meta": continue
    for lvl in lv:
        monitored.setdefault(lvl, set()).add(norm(s))

print(f"{'LEVEL':8s} {'총 학교':>6} {'감시중':>6} {'후보있음':>7} {'미커버':>6}")
for lvl, spec in LEVEL_BASE.items():
    d = kb[spec[0]][spec[1]] if spec[1] else kb[spec[0]]
    total = len(d)
    mon = monitored.get(lvl, set())
    mon_c = sum(1 for s in d if norm(s) in mon)
    disc_c = sum(1 for s in d if norm(s) in disc and norm(s) not in mon)
    gap = total - mon_c - disc_c
    print(f"{lvl:8s} {total:>6} {mon_c:>6} {disc_c:>7} {gap:>6}")

# list uncovered (no monitor, no candidate) per level
print("\n=== 미커버(감시도 후보도 없음) 학교 ===")
for lvl, spec in LEVEL_BASE.items():
    d = kb[spec[0]][spec[1]] if spec[1] else kb[spec[0]]
    mon = monitored.get(lvl, set()); 
    miss = [s for s in d if norm(s) not in mon and norm(s) not in disc]
    if miss:
        print(f"  [{lvl}] {len(miss)}: {', '.join(sorted(miss)[:25])}")