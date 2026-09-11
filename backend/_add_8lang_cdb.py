#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mirror the 8 new lang schools from verified_kb.lang_programs into consulting_db.schools.
Direct apply (preserves enriched fields like popular_majors — no blind rebuild)."""
import json, os, shutil

B = r"C:\Users\USER\camnemi-crm\backend"
KB = os.path.join(B, "verified_kb.json")
CDB = os.path.join(B, "consulting_db.json")
shutil.copy(CDB, os.path.join(B, "consulting_db_bak_addlang_2026-09-11.json"))

NEW = ["국립금오공과대학교","나사렛대학교","부산대","서울시립대","서울신학대","서일대학교","총신대","한성대학교"]

kb = json.load(open(KB, encoding="utf-8"))
cdb = json.load(open(CDB, encoding="utf-8"))
sch = cdb["schools"]
lp = kb["lang_programs"]["schools"]

added, updated = [], []
for k in NEW:
    v = lp[k]
    lang = {
        "tuition": v.get("tuition_range"),
        "structure": v.get("structure"),
        "d4_eligible": v.get("d4_eligible"),
        "dorm": v.get("dorm"),
        "period": v.get("period"),
        "guide_pdf": v.get("guide_pdf"),
    }
    if k in sch:
        entry = sch[k]
        entry.setdefault("programs", {})["어학연수"] = lang
        if not entry.get("region"):
            entry["region"] = v.get("region")
        updated.append(k)
    else:
        sch[k] = {"name": k, "region": v.get("region"), "rank": None,
                  "programs": {"어학연수": lang}}
        added.append(k)

json.dump(cdb, open(CDB, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("신규:", added)
print("기존키에 보강:", updated)
print("consulting_db 총 학교:", len(sch))
print("어학연수 보유:", sum(1 for v in sch.values() if '어학연수' in v.get('programs',{})))
