#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Merge one result entry into a per-track daily result file (read-merge-write)."""
import json, sys, io, os

def main():
    path, school, status, url, title, note = sys.argv[1:7]
    entry = {"school": school, "status": status, "url": url, "title": title, "note": note}
    data = []
    if os.path.exists(path) and os.path.getsize(path) > 0:
        with io.open(path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except Exception:
                data = []
    if not isinstance(data, list):
        data = []
    data = [e for e in data if e.get('school') != school]
    data.append(entry)
    with io.open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    # verify
    with io.open(path, 'r', encoding='utf-8') as f:
        json.load(f)
    print("OK %s -> %s (%d entries)" % (school, os.path.basename(path), len(data)))

if __name__ == '__main__':
    main()
