#!/usr/bin/env python3
"""Merge entries into per-track daily result file.
Usage: python merge_progress.py <track_file> <entries_json_file>
Replaces any entry whose 'school' matches; appends others. Reads the target
file fresh at write time to avoid clobbering concurrent subagent writes.
"""
import json, sys, os

track_file = sys.argv[1]
entries_file = sys.argv[2]

with open(entries_file, encoding='utf-8') as f:
    new_entries = json.load(f)

if os.path.exists(track_file):
    with open(track_file, encoding='utf-8') as f:
        try:
            cur = json.load(f)
        except json.JSONDecodeError:
            cur = []
else:
    cur = []

by_school = {e['school']: e for e in cur}
for e in new_entries:
    by_school[e['school']] = e

merged = list(by_school.values())
with open(track_file, 'w', encoding='utf-8') as f:
    json.dump(merged, f, ensure_ascii=False, indent=1)

# verify
with open(track_file, encoding='utf-8') as f:
    check = json.load(f)
print(f"OK {track_file}: {len(check)} entries -> {[e['school'] for e in check]}")
