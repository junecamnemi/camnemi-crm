#!/usr/bin/env python3
"""Batch merge: usage: python merge_multi.py <result_file> '<json_array_of_entries>'
Reads file once, upserts all entries (by 'school'), writes once."""
import json, sys, os

def main():
    path = sys.argv[1]
    entries = json.loads(sys.argv[2])
    data = []
    if os.path.exists(path) and os.path.getsize(path) > 0:
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print("WARN parse fail", e)
            data = []
    if not isinstance(data, list):
        data = []
    keys = {e.get("school") for e in entries}
    data = [e for e in data if e.get("school") not in keys]
    data.extend(entries)
    data.sort(key=lambda e: e.get("school", ""))
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    with open(path, "r", encoding="utf-8") as f:
        json.load(f)
    print(f"OK {path}: {len(data)} entries")

if __name__ == "__main__":
    main()
