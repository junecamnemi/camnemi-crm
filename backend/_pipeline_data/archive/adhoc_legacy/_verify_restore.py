# -*- coding: utf-8 -*-
"""Verify every file the dedupe archived is back in the active library."""
import json, os
G = r"G:/공유 드라이브/Hermes/Camnemi/02_Crawling_Sheet/University_Project/guides"
plan = json.load(open("_pipeline_data/reports/_library_dedupe_plan.json", encoding="utf-8"))
# the 2 I deliberately restored during the dedupe + the 58 undone = 59 planned
missing, extra_restored = [], []
n = 0
for e in plan["plan"]:
    if e["action"] not in ("archive_dup", "archive_junk"):
        continue
    nm = e["archive"][0]
    lv, yr = e["group"][2], e["group"][3]
    n += 1
    if not os.path.exists(os.path.join(G, lv, yr, nm)):
        if nm in ("동의대학교_MA_2027.pdf", "극동대학교_ma.pdf"):
            extra_restored.append((lv, yr, nm))
        else:
            missing.append((lv, yr, nm))
print(f"planned archive entries: {n}")
print(f"missing from active library: {len(missing)}")
for m in missing:
    print("   !", m)
print(f"restored earlier during the same run (expected): {len(extra_restored)}")
for m in extra_restored:
    print("   ok", m)
print(f"\nactive 2027 files: ba {len(os.listdir(os.path.join(G,'ba','2027')))} "
      f"ma {len(os.listdir(os.path.join(G,'ma','2027')))} "
      f"junior {len(os.listdir(os.path.join(G,'junior','2027')))} "
      f"lang {len(os.listdir(os.path.join(G,'lang','2027')))}")
left = []
for sub in ("_dupes", "_junk"):
    b = os.path.join(G, "_archive", sub)
    for root, _, files in os.walk(b):
        if os.path.basename(root) != "_bin":
            left += [os.path.join(root, f) for f in files]
print("guide files still archived from the dedupe (must be 0):", len(left))