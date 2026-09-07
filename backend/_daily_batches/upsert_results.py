#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Upsert per-track results into shared daily result JSON lists.
Usage: python upsert_results.py <payload_file>
payload_file: JSON object {"BA": [...], "MA": [...], "lang": [...]} (only tracks present are written)
Each entry: {"school":..., "status":..., "url":..., "title":..., "note":...}
Entries replace existing entries with the same school name (in place); new ones append.
"""
import json, sys, os

BASE = os.path.dirname(os.path.abspath(__file__))
RESULT_FILES = {
    "BA": os.path.join(BASE, "..", "_ba_batches", "BA_daily_20260905_result.json"),
    "MA": os.path.join(BASE, "..", "_ma_batches", "MA_daily_20260905_result.json"),
    "lang": os.path.join(BASE, "..", "_lang_batches", "lang_daily_20260905_result.json"),
}

def upsert(path, entries):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    idx = {e.get("school"): i for i, e in enumerate(data)}
    for e in entries:
        s = e.get("school")
        if s in idx:
            data[idx[s]] = e
        else:
            idx[s] = len(data)
            data.append(e)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    with open(path, encoding="utf-8") as f:
        json.load(f)  # verify parse
    print("OK %s -> %d entries" % (os.path.basename(path), len(data)))

if __name__ == "__main__":
    payload = json.load(open(sys.argv[1], encoding="utf-8"))
    for track, entries in payload.items():
        if entries:
            upsert(RESULT_FILES[track], entries)
