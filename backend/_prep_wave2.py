# -*- coding: utf-8 -*-
"""Prepare wave-2 batches: 2026 BA guides whose school is NOT in KB and NOT already
curated via 2027 (no 2027 guide exists for them). Exclude seminary/edu."""
import os, re, json, glob

FOLDER = r"C:/Users/USER/내 드라이브/02_Crawling_Sheet/University_Project/adiga_2026_외국인_모집요강/외국인"
KB = json.load(open(r"C:\Users\USER\camnemi-crm\backend\verified_kb.json", encoding="utf-8"))
OUT = r"C:\Users\USER\camnemi-crm\backend\_curation_2026_batches.json"

# Schools already in KB (78 BA) — skip
kb_ba = set(KB.get("schools", {}).keys())
# Also skip ones with a 2027 PDF (curated or will-be)
g2027 = set()
for fp in glob.glob(r"C:/Users/USER/내 드라이브/02_Crawling_Sheet/University_Project/adiga_2027_외국인_모집요강/외국인/*.pdf"):
    fn = os.path.basename(fp)
    s = re.sub(r"^0000\d+_", "", fn)
    s = re.sub(r"_2027_외국인.*", "", s)
    s = re.sub(r"\[.*?\]", "", s).strip()
    g2027.add(s)

EXCLUDE_WORDS = ["신학대", "교육대", "교원대", "장신대", "선학대", "승가", "성서대"]

seen = {}
for fp in sorted(glob.glob(os.path.join(FOLDER, "*.pdf"))):
    fn = os.path.basename(fp)
    s = re.sub(r"^0000\d+_", "", fn)
    s = re.sub(r"_2026_외국인.*", "", s)
    s = re.sub(r"\[.*?\]", "", s).strip()
    if not s or any(w in s for w in EXCLUDE_WORDS):
        continue
    if s in kb_ba or s in g2027:
        continue
    if s not in seen:
        seen[s] = {"name": s, "path": fp, "file": fn}

need = list(seen.values())
print(f"웨이브2 대상: {len(need)}개")
for u in sorted(need, key=lambda x: x['name']):
    print("  ", u['name'])

BATCH = 9
batches = [need[i:i+BATCH] for i in range(0, len(need), BATCH)]
json.dump(batches, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"\n배치 {len(batches)}개")
