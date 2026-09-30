#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Emit the tuition work lists as JSON targets, using OCR-aware text resolution.

  _tuition_targets_C.json   guide (after OCR fallback) carries a real tuition table → feed to Pro
  _tuition_targets_B.json   guide readable but no table → fees-site 일람표 crawl
  _tuition_targets_A1.json  no PDF anywhere → fetch the guide

Run under the venv that has rapidocr:  C:\\Users\\wisew\\pdf-venv\\Scripts\\python.exe
"""
import os, re, json, sys, importlib.util

B = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, B)
spec = importlib.util.spec_from_file_location("tpf", os.path.join(B, "_tuition_pro_fill.py"))
tpf = importlib.util.module_from_spec(spec)
sys.argv = ["x"]
try:
    spec.loader.exec_module(tpf)
except SystemExit:
    pass

tbd = json.load(open(os.path.join(B, "tuition_by_department.json"), encoding="utf-8"))["schools"]
idx = tpf.load_kb()
pend = [(n, lvl) for n, lv in tbd.items() for lvl, e in lv.items() if not e.get("rows")]
C, Bk, A1 = [], [], []
for name, lvl in pend:
    v = idx.get((name, lvl), {})
    sec, path = tpf.guide_section(v, name, lvl)
    if not sec:
        A1.append({"school": name, "level": lvl, "guide": os.path.basename(path or "") or None})
        continue
    amts = [int(x.replace(",", "")) for x in re.findall(r"\d{1,3}(?:,\d{3}){1,3}", sec)]
    uniq = len({a for a in amts if 300_000 <= a <= 15_000_000})
    rec = {"school": name, "level": lvl, "distinct_amounts": uniq}
    (C if uniq >= 3 else Bk).append(rec)
for fn, data in (("_tuition_targets_C.json", C), ("_tuition_targets_B.json", Bk), ("_tuition_targets_A1.json", A1)):
    json.dump(data, open(os.path.join(B, fn), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"pending {len(pend)} → C(extractable) {len(C)} | B(crawl) {len(Bk)} | A1(no file) {len(A1)}")
print("C by level:", {l: sum(1 for x in C if x['level'] == l) for l in ('BA', 'MA', '전문학사')})