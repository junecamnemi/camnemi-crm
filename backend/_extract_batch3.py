# -*- coding: utf-8 -*-
import json, os, sys
import pymupdf

base = r"C:\Users\USER\camnemi-crm\backend"
with open(os.path.join(base, "_curation_2027_batches.json"), "r", encoding="utf-8") as f:
    batches = json.load(f)

batch = batches[3]
outdir = os.path.join(base, "_batch3_txt")
os.makedirs(outdir, exist_ok=True)

for entry in batch:
    p = entry["path"]
    if not os.path.exists(p):
        print("MISSING:", entry["name_plain"], "->", p)
        continue
    doc = pymupdf.open(p)
    parts = []
    for i, page in enumerate(doc):
        parts.append(f"\n===== PAGE {i+1} =====\n" + page.get_text())
    text = "".join(parts)
    safe = entry["name_plain"].replace("/", "_").replace("\\", "_").replace("[", "_").replace("]", "_")
    out = os.path.join(outdir, safe + ".txt")
    with open(out, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"{entry['name_plain']}: pages={len(doc)} chars={len(text)} -> {out}")
    doc.close()
