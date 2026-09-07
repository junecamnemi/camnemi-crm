# -*- coding: utf-8 -*-
"""Clean wave-2 batches: strip leading numeric prefixes in school names."""
import json, re

PATH = r"C:\Users\USER\camnemi-crm\backend\_curation_2026_batches.json"
batches = json.load(open(PATH, encoding="utf-8"))

for b in batches:
    for e in b:
        e["name"] = re.sub(r"^\d+_", "", e["name"]).strip()

json.dump(batches, open(PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
# print batch schools
for i, b in enumerate(batches):
    print(f"batch {i} ({len(b)}):", [e['name'] for e in b])
