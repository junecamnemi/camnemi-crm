# -*- coding: utf-8 -*-
"""Build curation batch list: 2027 BA guides, excluding:
  - seminary/theology schools (신학대) — user rule (not recommended)
  - education univs (교육대) — no foreigner track
  - duplicate campuses of same school (keep 본교)
  - schools ALREADY deep-curated in KB (43 entries with guide_analyzed)
"""
import os, re, json, glob

FOLDER = r"C:/Users/USER/내 드라이브/02_Crawling_Sheet/University_Project/adiga_2027_외국인_모집요강/외국인"
KB = json.load(open(r"C:\Users\USER\camnemi-crm\backend\verified_kb.json", encoding="utf-8"))
OUT = r"C:\Users\USER\camnemi-crm\backend\_curation_2027_batches.json"

EXCLUDE_WORDS = ["신학대", "교육대", "교원대", "장신대", "선학대"]
# campuses to keep (본교); skip 제2/3/4캠퍼스 + 분교 where 본교 exists separately
SKIP_CAMPUS = re.compile(r"\[(제\d캠퍼스|분교|제3캠퍼스)\]")

files = sorted(glob.glob(os.path.join(FOLDER, "*.pdf")))
kb_ba = set(KB.get("schools", {}).keys())

entries = []
for fp in files:
    fn = os.path.basename(fp)
    raw = re.sub(r"^0000\d+_", "", fn)
    name_full = re.sub(r"_2027_외국인.*", "", raw).strip()
    name_plain = re.sub(r"\[.*?\]", "", name_full).strip()
    if any(w in name_plain for w in EXCLUDE_WORDS):
        continue
    if SKIP_CAMPUS.search(name_full):
        continue
    # also skip if 본교 of this school already counted
    entries.append({"name_full": name_full, "name_plain": name_plain, "path": fp, "file": fn})

# dedupe by name_plain
seen = {}
for e in entries:
    if e["name_plain"] not in seen:
        seen[e["name_plain"]] = e
uniq = list(seen.values())
print(f"필터 후 고유 학교: {len(uniq)}개")
print("KB에 이미 있는(스킵):", [u['name_plain'] for u in uniq if u['name_plain'] in kb_ba])
need = [u for u in uniq if u['name_plain'] not in kb_ba]
print(f"큐레이션 필요: {len(need)}개")
for u in need:
    print("  ", u['name_plain'])

BATCH = 9
batches = [need[i:i+BATCH] for i in range(0, len(need), BATCH)]
json.dump(batches, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"\n배치 {len(batches)}개 (각 {BATCH}개)")
