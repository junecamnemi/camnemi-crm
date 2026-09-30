# -*- coding: utf-8 -*-
"""Build discovery targets (school, level, page_url) for the slots that still need a
current 2027 guide PDF, using the watchlist rows (better page URLs than scrape_map)."""
import json, os, collections

HERE = os.path.dirname(os.path.abspath(__file__))
w = json.load(open(os.path.join(HERE, "_pipeline_data", "reports", "_2027_watchlist.json"),
                   encoding="utf-8"))
res = json.load(open(os.path.join(HERE, "_pipeline_data", "reports", "_redl_results.json"),
                     encoding="utf-8"))
failed = {(r["school"], r["level"]) for r in res if r["result"] != "ok"}

want = [
    ("동국대학교", "ba"), ("수원대학교", "ba"), ("신경주대학교", "ba"), ("차의과학대학교", "ba"),
    ("부산경상대학교", "junior"), ("극동대학교", "ma"),
    ("경북대학교", "ba"), ("고신대학교", "ba"), ("국립공주대학교", "ba"),
    ("신구대학교", "junior"), ("연세대학교", "lang"), ("우송대학교", "ba"),
    ("이화여자대학교", "lang"), ("장안대학교", "junior"),
]

by = collections.defaultdict(list)
for r in w["rows"]:
    if isinstance(r, dict) and r.get("school"):
        by[r["school"]].append(r)

targets, missing = [], []
for school, lv in want:
    row = next((r for r in by.get(school, []) if r.get("level") == lv), None)
    if row is None:
        row = next((r for r in by.get(school, [])), None)
    if row and row.get("page_url"):
        targets.append({"school": school, "level": lv, "url": row["page_url"],
                        "status": row.get("status"), "src": row.get("url_source")})
    else:
        missing.append((school, lv))

out = os.path.join(HERE, "_pipeline_data", "reports", "_redl_discover_targets.json")
json.dump(targets, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"discovery targets: {len(targets)}   (no page_url: {missing})")
for t in targets:
    print(f"  {t['school']} [{t['level']}] ({t['status']}) {t['url'][:110]}")