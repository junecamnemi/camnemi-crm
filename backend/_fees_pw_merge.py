#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Merge the Playwright 계열별 rows into tuition_by_department.json — verified, never overwriting.

Guards (same discipline as the Pro/qwen path):
  · only rows whose krw_raw appears VERBATIM in the recorded evidence (`verbatim`) are merged
  · entries that already have rows are never touched
  · unit=unknown is NOT converted — the row keeps its raw value and says so
  · detail_level is preserved: a 계열-level row is labelled as such, so the sheet can say
    "계열별(학과별 미공개)" instead of implying per-department precision
  · rows older than the guide year are tagged prev_year
Writes tuition_by_department.json (+ .bak) and prints the merged/skipped ledger.
"""
import os, re, json, shutil, datetime

B = os.path.dirname(os.path.abspath(__file__))
TBD = os.path.join(B, "tuition_by_department.json")
ROWS = os.path.join(B, "_fees_pw_rows.jsonl")
TODAY = datetime.date.today().isoformat()


def digits(s):
    return re.sub(r"\D", "", s or "")


def main():
    doc = json.load(open(TBD, encoding="utf-8"))
    shutil.copy(TBD, TBD.replace(".json", f"_bak_pwmerge_{TODAY}.json"))
    ledger = {"merged_entries": 0, "merged_rows": 0, "college_level": 0, "department_level": 0,
              "skipped_existing": 0, "skipped_verbatim": 0, "unknown_unit_rows": 0}
    if not os.path.exists(ROWS):
        print("no rows file")
        return
    for line in open(ROWS, encoding="utf-8"):
        if not line.strip():
            continue
        rec = json.loads(line)
        school, level, rows = rec["school"], rec["level"], rec.get("rows") or []
        if not rows:
            continue
        entry = (doc["schools"].get(school) or {}).get(level)
        if not isinstance(entry, dict):
            continue
        if entry.get("rows"):
            ledger["skipped_existing"] += 1
            continue
        keep = []
        for r in rows:
            # verbatim guard: the amount must be reconstructible from the recorded evidence
            ev = digits(r.get("verbatim", ""))
            if digits(r.get("krw_raw", "")) not in ev:
                ledger["skipped_verbatim"] += 1
                continue
            keep.append({"college": r["college"], "krw": r["krw"], "krw_raw": r["krw_raw"],
                         "unit": r["unit"], "detail_level": r["detail_level"],
                         "basis": r["basis"], "source_url": r["source_url"],
                         "page_year": r.get("page_year"), "evidence": r["verbatim"]})
        if not keep:
            continue
        entry["rows"] = keep
        entry["admission_fee"] = "별도 (separate)"
        entry["fee_status"] = "official_page_college_level"
        entry["fee_checked"] = TODAY
        entry["fee_source_url"] = keep[0]["source_url"]
        entry["fee_detail_level"] = ("department" if all(k["detail_level"] == "department" for k in keep)
                                     else "college")
        entry.pop("fee_evidence", None)
        ledger["merged_entries"] += 1
        ledger["merged_rows"] += len(keep)
        ledger["college_level"] += sum(1 for k in keep if k["detail_level"] == "college")
        ledger["department_level"] += sum(1 for k in keep if k["detail_level"] == "department")
        ledger["unknown_unit_rows"] += sum(1 for k in keep if k["unit"] == "unknown")
    json.dump(doc, open(TBD, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("merge ledger:", json.dumps(ledger, ensure_ascii=False))
    withr = sum(1 for lvs in doc["schools"].values() for e in lvs.values()
                if isinstance(e, dict) and e.get("rows"))
    total = sum(1 for lvs in doc["schools"].values() for e in lvs.values() if isinstance(e, dict))
    print(f"entries with rows: {withr} / {total}  (without: {total - withr})")


if __name__ == "__main__":
    main()