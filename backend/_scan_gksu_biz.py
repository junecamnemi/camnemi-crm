# -*- coding: utf-8 -*-
"""GKS-U 2026: scan every university's 'Available Departments' xlsx for
business-related departments (경영/business/무역/trade).

Output: one line per university listing the business departments found.
"""
import os
import glob
import re
import json

import openpyxl

ROOT = r"C:\Users\USER\camnemi-crm\backend\_gksu_univinfo"

# business-related keywords (match if any appears in a cell)
KW = [
    "경영", "무역", "국제통상", "비즈니스", "business", "Business",
    "경제", "마케팅", "회계", "관광", "호텔", "국제학부",
]
KW_STRICT = ["경영", "무역", "국제통상", "비즈니스", "business", "Business", "마케팅", "회계"]


def find_dept_files(root):
    return sorted(glob.glob(os.path.join(root, "**", "*Available*Departments*.xlsx"), recursive=True))


def sheet_text(ws):
    cells = []
    for row in ws.iter_rows(values_only=True):
        for c in row:
            if c is not None:
                cells.append(str(c))
    return cells


def main():
    files = find_dept_files(ROOT)
    print(f"Available Departments 파일: {len(files)}개")
    results = {}
    for fp in files:
        rel = os.path.relpath(fp, ROOT)
        univ = rel.split(os.sep)[0]
        try:
            wb = openpyxl.load_workbook(fp, read_only=True, data_only=True)
        except Exception as e:
            print(f"  [오류] {univ}: {e}")
            continue
        biz_rows = []
        all_rows = []
        for ws in wb.worksheets:
            for row in ws.iter_rows(values_only=True):
                joined = " ".join(str(c) for c in row if c is not None)
                if not joined.strip():
                    continue
                all_rows.append(joined)
                if any(k in joined for k in KW):
                    biz_rows.append(joined.strip())
        results[univ] = {
            "file": rel,
            "has_biz": len(biz_rows) > 0,
            "biz_count": len(biz_rows),
            "samples": biz_rows[:40],
            "total_rows": len(all_rows),
        }
        print(f"\n=== {univ} ===")
        print(f"  지원가능 학과(행) 수: {len(all_rows)} | 비즈니스 관련 행: {len(biz_rows)}")
        for s in biz_rows[:12]:
            print(f"    · {s[:100]}")
    with open(r"C:\Users\USER\camnemi-crm\backend\_gksu_biz_scan.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=1)
    print("\n\n=== 요약: 비즈니스 관련 학과 보유 대학 ===")
    for u, r in sorted(results.items(), key=lambda x: -x[1]["biz_count"]):
        if r["has_biz"]:
            print(f"  {u}: {r['biz_count']}개 행")


if __name__ == "__main__":
    main()
