# -*- coding: utf-8 -*-
"""Prepare MA (석사) curation batches — skip schools already deep in KB master,
exclude seminary/edu, skip campus duplicates."""
import os, re, json, glob

FOLDER = r"C:/Users/USER/내 드라이브/02_Crawling_Sheet/University_Project/adiga_2026_대학원_모집요강"
KB = json.load(open(r"C:\Users\USER\camnemi-crm\backend\verified_kb.json", encoding="utf-8"))
OUT = r"C:\Users\USER\camnemi-crm\backend\_curation_ma_batches.json"

EXCLUDE_WORDS = ["신학대", "교육대", "교원대", "장신대", "선학대"]
kb_master = set(KB.get("master", {}).get("schools", {}).keys())

entries = []
for fp in sorted(glob.glob(os.path.join(FOLDER, "*.pdf"))):
    fn = os.path.basename(fp)
    s = fn.replace("_대학원_모집요강", "").replace("_2026전기_일반대학원_국문", "").replace("_2026전기_일반대학원_영문", "").replace("_2026후기1차_일반대학원", "").replace("_외국인전형_일반대학원", "").replace(".pdf", "").strip()
    # clean leading codes and trailing partials like (2026)
    s = re.sub(r"^[0-9_]+", "", s)
    s = re.sub(r"\([^)]*\)", "", s).strip()
    if any(w in s for w in EXCLUDE_WORDS):
        continue
    entries.append({"name": s, "path": fp, "file": fn})

# dedupe
seen = {}
for e in entries:
    if e["name"] not in seen:
        seen[e["name"]] = e
uniq = list(seen.values())
print(f"MA PDF 총 {len(entries)}개 | 고유 {len(uniq)}개")
print("KB master 이미 등록(스킵):", [u['name'] for u in uniq if u['name'] in kb_master])
need = [u for u in uniq if u['name'] not in kb_master]
print(f"큐레이션 필요: {len(need)}개")
for u in need:
    print("  ", u['name'])

BATCH = 8
batches = [need[i:i+BATCH] for i in range(0, len(need), BATCH)]
json.dump(batches, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"\n배치 {len(batches)}개 (각 최대 {BATCH})")
