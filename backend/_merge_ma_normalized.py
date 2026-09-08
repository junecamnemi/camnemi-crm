# -*- coding: utf-8 -*-
"""Merge normalized MA tuition (21 schools) into consulting_db MA + verified_kb master."""
import json, re

DB = r"C:\Users\USER\camnemi-crm\backend\consulting_db.json"
KB_PATH = r"C:\Users\USER\camnemi-crm\backend\verified_kb.json"
results = json.load(open(r"C:\Users\USER\camnemi-crm\backend\_ma_tuition_all.json", encoding="utf-8"))

def norm(s):
    s = re.sub(r"\[.*?\]","",s)
    s = s.replace("대학교","").replace("전문대학","").replace("전문대","")
    while s.endswith(("대학","대","학")) and len(s)>1:
        s = s[:-1] if s.endswith(("대","학")) else s[:-2]
    return s.replace(" ","")

# verify norm works
print("norm(중부대)=",norm("중부대"),"| norm(중부대학교)=",norm("중부대학교"))

db = json.load(open(DB, encoding="utf-8"))
c_upd=0
for school, info in results.items():
    t = info.get("tuition")
    if t is None: continue
    sn = norm(school)
    match=None
    for nk in db["schools"]:
        if norm(nk)==sn:
            match=nk; break
    if not match:
        print(f"  ✗ 매칭실패: {school}")
        continue
    prog = db["schools"][match]["programs"].get("MA")
    if prog:
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
    if t is None: continue
    sn=norm(school)
    for nk,v in kb["master"]["schools"].items():
        if norm(nk)==sn:
            v["tuition"]=t; k_upd+=1
            break
json.dump(kb, open(KB_PATH,"w",encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"verified_kb MA 수업료 병합: {k_upd}")
