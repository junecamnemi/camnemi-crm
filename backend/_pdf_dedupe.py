# -*- coding: utf-8 -*-
"""Dedupe guide PDFs: same (name+size) -> keep one, delete the rest.
Keeps the file in the 'canonical' adiga folder; deletes duplicates in _ownsite_daily / real / etc.
Foreigner HTML files are NOT touched (they are the guide itself)."""
import os
from collections import defaultdict

UP = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project"

# canonical priority: adiga_* folders first, then _ownsite_daily, then real
def priority(path):
    p = path.replace("\\", "/")
    if "/adiga_" in p: return 0
    if "/real/" in p: return 1
    if "/_ownsite_daily/" in p: return 2
    return 3

# collect all PDFs
pdfs = []
for root, dirs, files in os.walk(UP):
    # skip 재외국민 (already deleted) and non-PDF
    for f in files:
        if f.lower().endswith(".pdf"):
            p = os.path.join(root, f)
            try: sz = os.path.getsize(p)
            except OSError: continue
            pdfs.append({"path": p, "name": f, "size": sz, "prio": priority(p)})

by_key = defaultdict(list)
for e in pdfs:
    by_key[(e["name"], e["size"])].append(e)

to_delete = []
for key, group in by_key.items():
    if len(group) <= 1: continue
    group.sort(key=lambda x: x["prio"])
    keep = group[0]
    for e in group[1:]:
        to_delete.append(e["path"])

print(f"총 PDF: {len(pdfs)} | 중복그룹: {sum(1 for g in by_key.values() if len(g)>1)} | 삭제대상: {len(to_delete)}")
for p in to_delete:
    print("  DEL:", p)

# execute
for p in to_delete:
    try:
        os.remove(p)
        print("  removed:", os.path.basename(p))
    except OSError as e:
        print("  FAIL:", p, e)

print(f"\n완료: {len(to_delete)}개 삭제")
