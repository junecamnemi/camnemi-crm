# -*- coding: utf-8 -*-
"""Merge lang tuition into consulting_db 어학연수 + verified_kb lang_programs."""
import json, re

DB = r"C:\Users\USER\camnemi-crm\backend\consulting_db.json"
KB_PATH = r"C:\Users\USER\camnemi-crm\backend\verified_kb.json"
results = json.load(open(r"C:\Users\USER\camnemi-crm\backend\_langtui_all.json", encoding="utf-8"))

def norm(s):
    s = re.sub(r"\[.*?\]","",s)
    s = s.replace("대학교","").replace("전문대학","").replace("전문대","")
    while s.endswith(("대학","대")) and len(s)>1:
        s = s[:-1] if s.endswith("대") else s[:-2]
    return s.replace(" ","")

# consulting
db = json.load(open(DB, encoding="utf-8"))
c_upd=0
for school, info in results.items():
    t = info["tuition"]
    sn = norm(school)
    for nk, s in db["schools"].items():
        if norm(nk)==sn:
            prog = s["programs"].get("어학연수")
            if prog and not prog.get("tuition"):
                prog["tuition"]=t
                prog["tuition_note"]=info.get("note","")
                c_upd+=1
            break
json.dump(db, open(DB,"w",encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"consulting 어학 수업료 병합: {c_upd}")

# verified_kb lang_programs
kb = json.load(open(KB_PATH, encoding="utf-8"))
lp = kb["lang_programs"]["schools"]
k_upd=0
for school, info in results.items():
    t = info["tuition"]
    sn = norm(school)
    for nk, v in lp.items():
        if norm(nk)==sn and not v.get("tuition_range"):
            v["tuition_range"]=t
            v["tuition_note"]=info.get("note","")
            k_upd+=1
            break
json.dump(kb, open(KB_PATH,"w",encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"verified_kb 어학 수업료 병합: {k_upd}")
