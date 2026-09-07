# -*- coding: utf-8 -*-
"""Prepare curation batches for 2027 BA guides (priority wave 1)."""
import os, re, json, glob

FOLDER = r"C:/Users/USER/내 드라이브/02_Crawling_Sheet/University_Project/adiga_2027_외국인_모집요강/외국인"
OUT = r"C:\Users\USER\camnemi-crm\backend\_curation_2027_ba.json"

files = sorted(glob.glob(os.path.join(FOLDER, "*.pdf")))
# exclude 재외국민 or non-foreigner by filename pattern? folder is 외국인 already
schools = []
for fp in files:
    fn = os.path.basename(fp)
    s = re.sub(r"^0000\d+_", "", fn)
    s = re.sub(r"_2027_외국인.*", "", s)
    s = s.strip()
    schools.append({"name": s, "path": fp, "file": fn})

# dedupe by name (prefer file without [분교]/[제2캠퍼스] if duplicate? keep all distinct campuses)
seen = {}
for sc in schools:
    key = sc["name"]
    if key not in seen:
        seen[key] = sc
uniq = list(seen.values())
print(f"2027 BA PDF 총 {len(files)}개 | 고유 학교 {len(uniq)}개")

# batch of ~8 per group
BATCH = 8
batches = [uniq[i:i+BATCH] for i in range(0, len(uniq), BATCH)]
print(f"배치 {len(batches)}개")
for i, b in enumerate(batches):
    print(f"  batch {i}: {len(b)}개 — {[x['name'] for x in b]}")

json.dump(batches, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
