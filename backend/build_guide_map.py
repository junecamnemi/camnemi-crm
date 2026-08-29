#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the `guide` reference map in verified_kb.json.

For each school: {status: '2027'|'2026', ref_url, title, note}.
- status '2027'  -> 2027 admission guide published (ref_url = the guide to share)
- status '2026'  -> 2027 guide NOT published yet; ref_url points to the latest
                    2026 guide so consulting can still reference something concrete.

Reads _guide_2027_master.json (the per-school 3-track status report). The daily
cron calls this after refreshing the master so the reference links/status stay
in sync with newly published 2027 guides.
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
KB_PATH = os.path.join(BASE, "verified_kb.json")
MASTER_PATH = os.path.join(BASE, "_guide_2027_master.json")

OK_2027 = {"2027_adiga", "2027_own"}

# Guide-master school name -> verified_kb school name (when they differ).
# NOTE: 한양대학교 (Seoul main) and 한양대학교(ERICA) are DIFFERENT schools with
# separate admission guides — do NOT merge them.
NAME_ALIAS = {
    "연세대학교(미래)": "연세대학교",
}

# Schools that exist in the KB but have their OWN separate adiga 2027 guide PDF
# on disk (not tracked as a distinct row in the guide master). status/ref follow
# the on-disk PDF presence.
EXTRA_2027 = {
    "한양대학교(ERICA)": "adiga_2027 (downloaded) — ERICA campus foreign guide",
}


def build_guide_map(kb=None, master=None):
    if kb is None:
        kb = json.load(open(KB_PATH, encoding="utf-8"))
    if master is None:
        master = json.load(open(MASTER_PATH, encoding="utf-8"))

    guide = {}
    for item in master:
        school = item.get("school", "")
        if not school:
            continue
        is2027 = item.get("ba_status") in OK_2027
        ref = item.get("ba_src") or item.get("ba_url") or ""
        if is2027:
            note = "2027 admission guide"
            if item.get("ba_status") == "2027_adiga":
                note += " (adiga PDF)"
        else:
            note = "2027 guide NOT published yet — use 2026 guide"
            if not ref:
                note = "2027 guide NOT published yet"
        # also store under the KB alias name so lookups by KB name resolve
        for key in {school, NAME_ALIAS.get(school, school)}:
            guide[key] = {
                "status": "2027" if is2027 else "2026",
                "ref_url": ref,
                "title": (item.get("ba_title") or "")[:100],
                "note": note,
            }

    # separate-campus schools with their own 2027 guide on disk
    for school, note in EXTRA_2027.items():
        guide[school] = {
            "status": "2027",
            "ref_url": note,
            "title": note,
            "note": note,
        }

    kb["guide"] = guide
    json.dump(kb, open(KB_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return guide


def main():
    guide = build_guide_map()
    n2027 = sum(1 for v in guide.values() if v["status"] == "2027")
    n2026 = sum(1 for v in guide.values() if v["status"] == "2026")
    print(f"[guide] map: {len(guide)} schools | 2027 published: {n2027} | 2026-only: {n2026}")


if __name__ == "__main__":
    main()
