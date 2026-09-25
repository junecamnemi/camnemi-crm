# -*- coding: utf-8 -*-
"""Survey all guide PDFs: path, size, name — to find duplicates & non-foreigner guides."""
import os, hashlib, json

UP = r"C:\Users\wisew\내 드라이브\02_Crawling_Sheet\University_Project"

# all PDFs under UP (recursive)
pdfs = []
for root, dirs, files in os.walk(UP):
    for f in files:
        if f.lower().endswith(".pdf"):
            p = os.path.join(root, f)
            try:
                sz = os.path.getsize(p)
            except OSError:
                continue
            pdfs.append({"path": p, "name": f, "size": sz})

print("총 PDF:", len(pdfs))

# group by (name, size) -> duplicates
from collections import defaultdict
by_key = defaultdict(list)
for e in pdfs:
    by_key[(e["name"], e["size"])].append(e)

dups = {k: v for k, v in by_key.items() if len(v) > 1}
print("(이름+용량) 중복 그룹:", len(dups))
for k, v in list(dups.items())[:20]:
    print(f"  [{k[0]} | {k[1]}B] x{len(v)}")
    for e in v:
        print(f"     {e['path']}")

# save full manifest
json.dump(pdfs, open(r"C:\Users\wisew\camnemi-crm\backend\_pdf_manifest.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("\n매니페스트 저장: _pdf_manifest.json")
