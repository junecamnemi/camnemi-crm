#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Merge tuition_by_department.json's per-department tuition INTO verified_kb.json (the SOT).

Why: sync_kb_to_postgres.py (the loader) rebuilds cat.tuition from verified_kb.json ONLY.
tuition_by_department.json was built as a SEPARATE artifact; its richer junior (전문학사)
rows (424 across 99 schools) were never folded back into verified_kb (which holds only
95 fields across 48 schools), so a loader --reset dropped junior tuition 440 -> 283.

Canonical flow (skill: tuition-per-department-sourcing.md):
    tuition_by_department.json  ->  verified_kb.json (SOT)  ->  sync_kb_to_postgres.py  ->  cat.tuition

Scope: junior (전문학사) only for now. verified_kb is ALREADY richer for ba/ma
(2,485/812 rows vs the artifact's 1,858/691), so merging ba/ma adds nothing.

Loader reads: junior.<name>.tuition_semester_by_dept.fields  {college: krw}.

Rules:
  - skip any row whose college name says "입학금포함" (amount includes the fee; the
    operator rule is 입학금 = 별도, 수업료 only). The one such row (경인여대 인문계열
    1학기) has a "(2학기 이후)" counterpart that IS pure tuition, so nothing is lost.
  - union, artifact wins on an exact key collision (do not delete verified_kb's keys).

Usage:
    python backend/_merge_tuition_into_kb.py [--dry]
"""
import json
import re
import shutil
import sys
from datetime import datetime

BACKEND = "C:/Users/wisew/camnemi-crm/backend"
KB = f"{BACKEND}/verified_kb.json"
ART = f"{BACKEND}/tuition_by_department.json"


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def main():
    dry = "--dry" in sys.argv
    kb = load(KB)
    art = load(ART)

    jun = kb["junior"]["schools"]
    schools = art["schools"]

    additions = 0          # new keys added to verified_kb
    schools_touched = 0
    skipped_admission_fee = 0
    unmatched = []

    for name, v in schools.items():
        if not isinstance(v, dict) or "전문학사" not in v:
            continue
        lv = v["전문학사"]
        rows = lv.get("rows") or []
        if not rows:
            continue
        if name not in jun:
            unmatched.append(name)
            continue

        entry = jun[name]
        tsbd = entry.get("tuition_semester_by_dept")
        if not isinstance(tsbd, dict):
            tsbd = {}
        fields = tsbd.get("fields")
        if not isinstance(fields, dict):
            fields = {}

        touched = False
        for r in rows:
            col = (r.get("college") or "").strip()
            krw = r.get("krw")
            if not col or not isinstance(krw, (int, float)) or krw <= 0:
                continue
            if "입학금포함" in col:
                skipped_admission_fee += 1
                continue
            krw = int(krw)
            if fields.get(col) != krw:
                fields[col] = krw
                additions += 1
                touched = True

        if not touched:
            continue
        tsbd["fields"] = fields
        tsbd["note"] = "tuition_by_department merge"
        tsbd["updated"] = "2026-09-30 (merge)"
        entry["tuition_semester_by_dept"] = tsbd
        schools_touched += 1

    print(f"junior schools with rows in artifact: "
          f"{sum(1 for n,v in schools.items() if isinstance(v,dict) and '전문학사' in v and (v['전문학사'].get('rows') or []))}")
    print(f"schools touched (fields added/changed): {schools_touched}")
    print(f"new/changed field entries: {additions}")
    print(f"rows skipped (입학금포함): {skipped_admission_fee}")
    if unmatched:
        print(f"UNMATCHED schools: {unmatched}")

    if dry:
        print("\n[DRY] verified_kb.json NOT modified")
        return

    shutil.copy(KB, KB + f".bak_merge_{datetime.now():%Y%m%d_%H%M%S}")
    kb["junior"]["schools"] = jun
    with open(KB, "w", encoding="utf-8") as f:
        json.dump(kb, f, ensure_ascii=False, indent=2)
    print("\nverified_kb.json written.")


if __name__ == "__main__":
    main()
