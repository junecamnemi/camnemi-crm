#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate batch input files from _daily_pending.json for the daily 2027 re-check."""
import json, os, datetime

BASE = r"C:/Users/USER/camnemi-crm/backend"
D = datetime.date.today().strftime("%Y%m%d")

pend = json.load(open(os.path.join(BASE, "_daily_pending.json"), encoding="utf-8"))
dirs = {"BA": "_ba_batches", "MA": "_ma_batches", "lang": "_lang_batches"}

for track, key in [("BA", "BA"), ("MA", "MA"), ("lang", "lang")]:
    lst = pend[track]
    outdir = os.path.join(BASE, dirs[key])
    os.makedirs(outdir, exist_ok=True)
    # batches of 12
    n = 12
    batches = [lst[i:i+n] for i in range(0, len(lst), n)]
    written = []
    for idx, b in enumerate(batches, 1):
        fn = os.path.join(outdir, f"{key}_daily_{D}_{idx:02d}.json")
        with open(fn, "w", encoding="utf-8") as f:
            json.dump(b, f, ensure_ascii=False, indent=1)
        written.append((fn, len(b)))
    print(f"[{track}] {len(lst)} schools -> {len(batches)} batches:")
    for fn, c in written:
        print(f"   {os.path.basename(fn)}: {c}")
