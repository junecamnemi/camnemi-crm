# -*- coding: utf-8 -*-
"""Count 2026 BA guides whose school is NOT yet in KB (candidates for wave 2 curation)."""
import os, re, json, glob

FOLDER = r"C:/Users/USER/내 드라이브/02_Crawling_Sheet/University_Project/adiga_2026_외국인_모집요강/외국인"
KB = json.load(open(r"C:\Users\USER\camnemi-crm\backend\verified_kb.json", encoding="utf-8"))
kb_ba = set(KB.get("schools", {}).keys())

EXCLUDE_WORDS = ["신학대", "교육대", "교원대", "장신대", "선학대"]

files = []
for fp in sorted(glob.glob(os.path.join(FOLDER, "*.pdf"))):
    fn = os.path.basename(fp)
    s = re.sub(r"^0000\d+_", "", fn)
    s = re.sub(r"_2026_외국인.*", "", s)
    s = re.sub(r"\[.*?\]", "", s).strip()
    if not s or any(w in s for w in EXCLUDE_WORDS):
        continue
    files.append({"name": s, "file": fn, "path": fp})

uniq = {}
for f in files:
    if f["name"] not in uniq:
        uniq[f["name"]] = f
all_2026 = list(uniq.values())
need = [u for u in all_2026 if u["name"] not in kb_ba]
print(f"2026 BA 고유 학교: {len(all_2026)} | KB 미보유(웨이브2 후보): {len(need)}")
for u in need:
    print("  ", u["name"])
