# -*- coding: utf-8 -*-
"""Merge MA tuition from 4 per-batch files into consulting_db MA + verified_kb master."""
import json, re, os, glob

DB = r"C:\Users\USER\camnemi-crm\backend\consulting_db.json"
KB_PATH = r"C:\Users\USER\camnemi-crm\backend\verified_kb.json"

# load all batch files
results = {}
for fp in glob.glob(r"C:\Users\USER\camnemi-crm\backend\_ma_tuition_batch*.json"):
    data = json.load(open(fp, encoding="utf-8"))
    for k, v in data.items():
        results[k] = v  # last wins, but each school only in one batch

def norm(s): return re.sub(r"\[.*?\]","",s).replace("대학교","").replace("대학","").replace(" ","")

db = json.load(open(DB, encoding="utf-8"))
c_upd=0
for school, info in results.items():
    t = info.get("tuition")
    if not t: continue
    sn = norm(school)
    match=None
    for nk,s in db["schools"].items():
        if norm(nk)==sn or sn in norm(nk) or norm(nk) in sn:
            match=nk; break
    if not match:
        print(f"  ✗ 매칭실패 MA: {school}")
        continue
    prog = db["schools"][match]["programs"].get("MA")
    if prog and not prog.get("tuition"):
        prog["tuition"]=t
        if info.get("tuition_max"): prog["tuition_max"]=info["tuition_max"]
        prog["tuition_note"]=info.get("note","")
        c_upd+=1
json.dump(db, open(DB,"w",encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"consulting MA 수업료 병합: {c_upd}")

# verified_kb master
kb=json.load(open(KB_PATH,encoding="utf-8"))
k_upd=0
for school, info in results.items():
    t=info.get("tuition")
    if not t: continue
    sn=norm(school)
    for nk,v in kb["master"]["schools"].items():
        if norm(nk)==sn or sn in norm(nk) or norm(nk) in sn:
            if not v.get("tuition"):
                v["tuition"]=t; k_upd+=1
            break
json.dump(kb, open(KB_PATH,"w",encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"verified_kb MA 수업료 병합: {k_upd}")
