#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Progressive result-file updater for daily batch runs.
Usage: python _upd_result.py <result_file> '<json_entry>'
Reads the result file (JSON list), replaces/inserts the entry for the given
school, writes back with ensure_ascii=False, indent=1. Exits 0 on success.
"""
import json, sys, os

def main():
    path = sys.argv[1]
    entry = json.loads(sys.argv[2])
    school = entry.get("school")
    if not school:
        print("ERR: entry missing school"); sys.exit(2)
    data = []
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except Exception as e:
                print(f"WARN: existing file unparsable ({e}); starting fresh")
                data = []
    if not isinstance(data, list):
        data = []
    data = [d for d in data if d.get("school") != school]
    data.append(entry)
    data.sort(key=lambda d: d.get("school", ""))
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    # verify
    with open(path, "r", encoding="utf-8") as f:
        json.load(f)
    print(f"OK: {path} now has {len(data)} entries")

if __name__ == "__main__":
    main()
