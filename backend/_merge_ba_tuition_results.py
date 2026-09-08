# -*- coding: utf-8 -*-
"""Merge BA tuition results into consulting_db BA programs + verified_kb BA schools.
Reads the consolidated _ba_tuition_results.json (no concurrency)."""
import json, re

DB = r"C:\Users\USER\camnemi-crm\backend\consulting_db.json"
KB_PATH = r"C:\Users\USER\camnemi-crm\backend\verified_kb.json"
RES = json.load(open(r"C:\Users\USER\camnemi-crm\backend\_ba_tuition_results.json", encoding="utf-8"))

def norm(s): return re.sub(r"\[.*?\]","",s).replace("대학교","").replace("대학","").replace(" ","")

db = json.load(open(DB, encoding="utf-8"))
c_upd=0
for school, info in RES.items():
    t = info.get("tuition")
    if not t: continue  # skip 대전가톨릭 (None)
    # match consulting school
    sn = norm(school)
    match=None
    for nk,s in db["schools"].items():
        if norm(nk)==sn or sn in norm(nk) or norm(nk) in sn:
            match=nk; break
    if not match:
        print(f"  ✗ 매칭실패: {school}")
        continue
    prog = db["schools"][match]["programs"].get("BA")
    if prog and not prog.get("tuition"):
        prog["tuition"]=t
        if info.get("tuition_max"): prog["tuition_max"]=info["tuition_max"]
        prog["tuition_note"]=info.get("note","")
        c_upd+=1
json.dump(db, open(DB,"w",encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"consulting BA 수업료 병합: {c_upd}")

# verified_kb
kb=json.load(open(KB_PATH,encoding="utf-8"))
k_upd=0
for school, info in RES.items():
    t=info.get("tuition")
    if not t: continue
    sn=norm(school)
    for nk,v in kb["schools"].items():
        if norm(nk)==sn or sn in norm(nk) or norm(nk) in sn:
            if not v.get("tuition_semester"):
                v["tuition_semester"]=t; k_upd+=1
            break
json.dump(kb, open(KB_PATH,"w",encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"verified_kb BA 수업료 병합: {k_upd}")
