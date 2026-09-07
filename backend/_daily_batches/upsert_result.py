#!/usr/bin/env python3
"""Upsert one result entry into a per-track daily result JSON file (read-merge-write)."""
import json, sys, os

def main():
    track = sys.argv[1]            # ba | ma | lang
    school = sys.argv[2]
    status = sys.argv[3]
    url = sys.argv[4]
    title = sys.argv[5]
    note = sys.argv[6]

    base = r"C:/Users/USER/camnemi-crm/backend"
    path = os.path.join(base, "_%s_batches" % track, "%s_daily_20260905_result.json" % track.upper())

    data = []
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    if not isinstance(data, list):
        data = []

    entry = {"school": school, "status": status, "url": url, "title": title, "note": note}
    data = [e for e in data if e.get("school") != school]
    data.append(entry)
    data.sort(key=lambda e: e.get("school", ""))

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)

    # verify
    with open(path, "r", encoding="utf-8") as f:
        json.load(f)
    print("OK %s %s -> %d entries" % (track, school, len(data)))

if __name__ == "__main__":
    main()
