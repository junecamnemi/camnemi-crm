# -*- coding: utf-8 -*-
"""Normalize MA tuition batch files (batch1 used min/max/fields directly) into
standard {school: {school, level:MA, tuition:{min,max}, ...}} then merge."""
import json, re, glob, os

# normalize and merge all batches
all_results = {}
for fp in glob.glob(r"C:\Users\USER\camnemi-crm\backend\_ma_tuition_batch*.json"):
    data = json.load(open(fp, encoding="utf-8"))
    for school, raw in data.items():
        if not isinstance(raw, dict): continue
        if raw.get("tuition") is not None and isinstance(raw.get("tuition"), (dict,int)):
            # already standard
            entry = {"school": school, "level": "MA", "tuition": raw["tuition"],
                     "tuition_max": raw.get("tuition_max"), "source_url": raw.get("source_url",""),
                     "note": raw.get("note","")}
        elif "min" in raw or "max" in raw:
            mn, mx = raw.get("min"), raw.get("max")
            t = mx if (mn is None or mx is None) else {"min": mn, "max": mx}
            entry = {"school": school, "level": "MA", "tuition": t, "tuition_max": mx,
                     "source_url": raw.get("source_url",""), "note": raw.get("note","")}
        else:
            continue
        all_results[school] = entry

json.dump(all_results, open(r"C:\Users\USER\camnemi-crm\backend\_ma_tuition_all.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"정규화 완료: {len(all_results)}개 MA 항목")
for s,e in all_results.items():
    print(f"  {s}: {e['tuition']}")
