# -*- coding: utf-8 -*-
"""Scan all GKS-U University Information xlsx files: list universities,
find business/pharmacy/cosmetic majors, count total majors."""
import glob
import os
import re
import json

import openpyxl

BASE = r"C:\Users\USER\camnemi-crm\backend\_gksu_univinfo"

BIZ_KW = ["business", "management", "economics", "trade", "commerce", "finance",
          "accounting", "marketing", "hospitality", "tourism", "international studies"]
PHARM_KW = ["pharmacy", "pharmaceutical", "pharmacology"]
COS_KW = ["cosmetic", "beauty", "esthetics", "makeup"]

def scan_xlsx(path):
    try:
        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    except Exception as e:
        return None, f"ERR {e}"
    majors = []
    for ws in wb.worksheets:
        for row in ws.iter_rows(values_only=True):
            for cell in row:
                if isinstance(cell, str):
                    s = cell.strip()
                    if s and len(s) > 2:
                        majors.append(s)
    return majors, None

results = []
for folder in sorted(glob.glob(os.path.join(BASE, "*"))):
    if not os.path.isdir(folder):
        continue
    name = os.path.basename(folder)
    xlsx = glob.glob(os.path.join(folder, "*.xlsx"))
    if not xlsx:
        continue
    majors, err = scan_xlsx(xlsx[0])
    if err or not majors:
        continue
    # dedupe, keep unique
    uniq = []
    for m in majors:
        if m not in uniq:
            uniq.append(m)
    low = " ".join(uniq).lower()
    biz = [m for m in uniq if any(k in m.lower() for k in BIZ_KW)]
    pharm = [m for m in uniq if any(k in m.lower() for k in PHARM_KW)]
    cos = [m for m in uniq if any(k in m.lower() for k in COS_KW)]
    results.append({
        "school": name,
        "total_majors": len(uniq),
        "biz": biz,
        "pharm": pharm,
        "cos": cos,
    })

json.dump(results, open(r"C:\Users\USER\camnemi-crm\backend\_gksu_summary.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

print(f"=== {len(results)} GKS-U universities scanned ===")
for r in results:
    print(f"{r['school']}: {r['total_majors']} majors | biz:{len(r['biz'])} pharm:{len(r['pharm'])} cos:{len(r['cos'])}")
