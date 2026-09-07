# -*- coding: utf-8 -*-
"""Scan 2027 adiga foreigner guides for pharmacy (약학) departments and their
language requirements. Finds which pharmacy programs accept English (IELTS/TOEFL)."""
import glob
import os
import re
import json

import pymupdf

FOLDER = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project\adiga_2027_외국인_모집요강\외국인"


def main():
    results = []
    files = sorted(glob.glob(os.path.join(FOLDER, "*.pdf")))
    for fp in files:
        fname = os.path.basename(fp)
        school = re.sub(r"^0000\d+_", "", fname)
        school = re.sub(r"_\d{4}_외국인.*", "", school)
        try:
            doc = pymupdf.open(fp)
        except Exception:
            continue
        found = []
        for i in range(len(doc)):
            t = doc[i].get_text()
            if "약학" not in t:
                continue
            # look for pharmacy dept names and nearby language requirements
            for m in re.finditer(r"약학[과학부대]*|첨단약과학과|제약[과학부]", t):
                s = max(0, m.start() - 120)
                e = min(len(t), m.start() + 260)
                ctx = t[s:e].replace("\n", " ")
                found.append((i + 1, ctx[:380]))
        if found:
            results.append({"school": school, "file": fname, "hits": found})
    # output summary
    print(f"=== 약학 언급 학교: {len(results)}곳 ===")
    for r in results:
        print(f"\n■ {r['school']}")
        seen = set()
        for page, ctx in r["hits"]:
            key = ctx[:60]
            if key in seen:
                continue
            seen.add(key)
            has_eng = any(k in ctx for k in ["IELTS", "TOEFL", "TEPS", "TOEIC", "English"])
            has_topik = "TOPIK" in ctx
            print(f"  [p{page}] {'ENG!' if has_eng and not has_topik else ''} {ctx[:150]}")
    json.dump(results, open(r"C:\Users\USER\camnemi-crm\backend\_pharmacy_scan.json",
                            "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
