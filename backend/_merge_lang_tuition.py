# -*- coding: utf-8 -*-
"""Merge newly found lang tuition (신라대, 한국항공대) into KB lang_programs + consulting_db."""
import json, re

KB_PATH = r"C:\Users\USER\camnemi-crm\backend\verified_kb.json"
DB = r"C:\Users\USER\camnemi-crm\backend\consulting_db.json"
gap = json.load(open(r"C:\Users\USER\camnemi-crm\backend\_lang_tuition_gap.json", encoding="utf-8"))

def norm(s): return re.sub(r"\[.*?\]","",s).replace("대학교","").replace("대학","").replace(" ","")

# update KB
kb = json.load(open(KB_PATH, encoding="utf-8"))
lp = kb["lang_programs"]["schools"]
for k, t in gap.items():
    sn = norm(k)
    for name, v in lp.items():
        if norm(name) == sn and not v.get("tuition_range"):
            v["tuition_range"] = t
            break
json.dump(kb, open(KB_PATH,"w",encoding="utf-8"), ensure_ascii=False, indent=2)

# update consulting
db = json.load(open(DB, encoding="utf-8"))
for k, t in gap.items():
    sn = norm(k)
    for name, s in db["schools"].items():
        prog = s["programs"].get("어학연수")
        if prog and norm(name)==sn and not prog.get("tuition"):
            prog["tuition"] = t
            break
json.dump(db, open(DB,"w",encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"어학 수업료 병합: {len(gap)}개 (KB + consulting)")
