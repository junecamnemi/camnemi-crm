#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Classify the entries still missing per-department tuition — WHY each one is unanalysed.

Buckets (decide the next action per bucket, do not re-parse blindly):
  A no_local_guide   — KB has no guide path, or the PDF is not in the local library
  B guide_no_table   — guide exists, 등록금 digest has no tuition-table amounts → fees-site crawl
  C guide_has_table  — guide exists AND carries amounts → Pro+qwen can fill it right now
  D not_ba_ma_junior — entry whose level we do not source (skip)

Writes backend/_tuition_gap_report.json and prints the scoped work list.
"""
import os, re, json, sys, importlib.util

B = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("tpf", os.path.join(B, "_tuition_pro_fill.py"))
tpf = importlib.util.module_from_spec(spec)
sys.argv = ["x"]
try:
    spec.loader.exec_module(tpf)
except SystemExit:
    pass


def main():
    tbd = json.load(open(os.path.join(B, "tuition_by_department.json"), encoding="utf-8"))["schools"]
    idx = tpf.load_kb()
    pend = [(n, lvl) for n, lv in tbd.items() for lvl, e in lv.items() if not e.get("rows")]
    buckets = {"A_no_local_guide": [], "B_guide_no_table": [], "C_guide_has_table": []}
    detail = []
    for name, lvl in pend:
        v = idx.get((name, lvl), {})
        sec, path = tpf.guide_section(v, name, lvl)
        if not sec:
            buckets["A_no_local_guide"].append([name, lvl, os.path.basename(path or "") or None])
            detail.append({"school": name, "level": lvl, "bucket": "A_no_local_guide",
                           "guide": os.path.basename(path or "") or None})
            continue
        # a tuition table shows several distinct amounts >= 300,000 clustered together
        amts = [int(x.replace(",", "")) for x in re.findall(r"\d{1,3}(?:,\d{3}){1,3}", sec)]
        amts = [a for a in amts if 300_000 <= a <= 15_000_000]
        uniq = len(set(amts))
        has_tbl = uniq >= 3
        b = "C_guide_has_table" if has_tbl else "B_guide_no_table"
        buckets[b].append([name, lvl, uniq])
        detail.append({"school": name, "level": lvl, "bucket": b, "distinct_amounts": uniq,
                       "guide": os.path.basename(path or "")})
    rep = {"total_pending": len(pend),
           "counts": {k: len(v) for k, v in buckets.items()},
           "level_counts": {}, "buckets": buckets}
    for name, lvl in pend:
        rep["level_counts"][lvl] = rep["level_counts"].get(lvl, 0) + 1
    json.dump({"report": rep, "detail": detail}, open(os.path.join(B, "_tuition_gap_report.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("pending:", len(pend), "| levels:", rep["level_counts"])
    for k, v in buckets.items():
        print(f"\n== {k}: {len(v)}")
        for row in v[:12]:
            print("   ", row)
    print("\nWROTE _tuition_gap_report.json")


if __name__ == "__main__":
    main()