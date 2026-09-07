# -*- coding: utf-8 -*-
"""Upsert school entries into per-track daily result files (progressive writes)."""
import json, io, sys, os

FILES = {
    "BA": r"C:/Users/USER/camnemi-crm/backend/_ba_batches/BA_daily_20260905_result.json",
    "MA": r"C:/Users/USER/camnemi-crm/backend/_ma_batches/MA_daily_20260905_result.json",
    "lang": r"C:/Users/USER/camnemi-crm/backend/_lang_batches/lang_daily_20260905_result.json",
}

def upsert(track, entries):
    path = FILES[track]
    data = []
    if os.path.exists(path):
        with io.open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    by_school = {e["school"]: e for e in data}
    for e in entries:
        by_school[e["school"]] = e
    out = list(by_school.values())
    out.sort(key=lambda x: x["school"])
    with io.open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    # verify
    with io.open(path, "r", encoding="utf-8") as f:
        json.load(f)
    print(f"[{track}] upserted {len(entries)} -> {path} (total {len(out)})")

if __name__ == "__main__":
    track = sys.argv[1]
    entries = json.load(open(sys.argv[2], "r", encoding="utf-8"))
    upsert(track, entries)
