#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Stamp the crawl outcome onto every school×level that still has no per-college rows.

A blank is not neutral: a student sheet that shows nothing for 학비 reads as "we didn't look".
This writes the measured reason instead — no invented numbers. `fee_status`:
  no_public_table  probed; the school publishes no per-학과 등록금일람표 we could reach
  no_source_url    the KB record holds no http(s) source at all
Reads _fees_v2_found.json (per-school pages/attachments evidence) + tuition_by_department.json.
"""
import os, json, datetime

B = os.path.dirname(os.path.abspath(__file__))
TBD = os.path.join(B, "tuition_by_department.json")
FOUND = os.path.join(B, "_fees_v2_found.json")
TODAY = datetime.date.today().isoformat()

doc = json.load(open(TBD, encoding="utf-8"))
found = json.load(open(FOUND, encoding="utf-8")) if os.path.exists(FOUND) else {}

stamped = {"no_public_table": 0, "no_source_url": 0, "already_had_rows": 0}
for school, levels in doc["schools"].items():
    for lv, e in levels.items():
        if not isinstance(e, dict):
            continue
        if e.get("rows"):
            stamped["already_had_rows"] += 1
            continue
        ev = found.get(f"{school}|{lv}") or {}
        seeds = ev.get("seeds") or []
        pages = ev.get("pages") or []
        atts = ev.get("attachments") or []
        if not seeds:
            e["fee_status"] = "no_source_url"
        else:
            e["fee_status"] = "no_public_table"
        e["fee_checked"] = TODAY
        e["admission_fee"] = "별도 (separate)"
        e["fee_evidence"] = {
            "seeds_tried": len(seeds),
            "pages_fetched": len(pages),
            "attachment_candidates": len(atts),
            "note": ("요강·입학처 페이지에서 학과별 등록금일람표를 찾지 못함 — "
                     "재무처/입학처 등록금 안내 페이지가 공개 목록에 없음"),
        }
        stamped[e["fee_status"]] += 1

doc["meta"]["fee_status_stamped"] = TODAY
doc["meta"]["fee_status_note"] = (
    "101 entries carry no per-department rows. Static crawl of each school's own source URLs "
    "(입학처/모집요강 pages) found no published 등록금일람표; national portals (adiga, 대학알리미) "
    "are JS-rendered and need a real browser. Values stay blank rather than estimated."
)
json.dump(doc, open(TBD, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("stamped:", stamped)
tot = sum(len(v) for v in doc["schools"].values())
rows = sum(len(e.get("rows") or []) for lvs in doc["schools"].values() for e in lvs.values() if isinstance(e, dict))
print(f"schools={len(doc['schools'])} entries={tot} rows={rows}")