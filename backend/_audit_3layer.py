# -*- coding: utf-8 -*-
"""Comprehensive 3-layer sync audit: verified_kb / consulting_db / data.js
coverage + mismatches before rebuild."""
import json, re

def norm(x):
    x = re.sub(r"\[.*?\]|\(.*?\)","",str(x))
    for suf in ["대학원대학교","대학교","대학원","대학","전문대학","전문대"]:
        if x.endswith(suf): x=x[:-len(suf)]; break
    if x.endswith("대") and len(x)>1: x=x[:-1]
    return x.replace(" ","")

def cov(schools, level_fields):
    n=len(schools); res={}
    for fn, getter in level_fields.items():
        c=sum(1 for s in schools if getter(s))
        res[fn]=f"{c}({100*c//n if n else 0}%)"
    return n, res

# ---- verified_kb ----
kb=json.load(open(r"C:\Users\USER\camnemi-crm\backend\verified_kb.json",encoding="utf-8"))
print("========== verified_kb (원본) ==========")
for sec,key,node in [("BA","schools","schools"),("MA","master","master"),("junior","junior","junior")]:
    sch = kb[key]
    if isinstance(sch, dict) and "schools" in sch and isinstance(sch["schools"], dict):
        sch = sch["schools"]
    if not isinstance(sch, dict): 
        print(f"[{sec}] 구조 비정상: {type(sch).__name__}"); continue
    def gt(f):
        return lambda s: bool(s.get(f))
    print(f"[{sec}] n={len(sch)} "
          f"tuition={sum(1 for s in sch.values() if s.get('tuition_semester') or s.get('tuition') or s.get('tuition_min'))}"
          f" by_dept={sum(1 for s in sch.values() if s.get('tuition_semester_by_dept'))}"
          f" sch={sum(1 for s in sch.values() if s.get('scholarships_categorized') or s.get('scholarship_curated') or s.get('scholarships'))}"
          f" period={sum(1 for s in sch.values() if s.get('period'))}"
          f" lang_bypass={sum(1 for s in sch.values() if s.get('lang_bypass'))}")

# ---- consulting_db ----
db=json.load(open(r"C:\Users\USER\camnemi-crm\backend\consulting_db.json",encoding="utf-8"))
print("\n========== consulting_db (상담) ==========")
for lvl in ["BA","MA","전문학사","어학연수"]:
    cnt=0; t=0; by=0; sc=0; pe=0
    for n,s in db["schools"].items():
        p=s.get("programs",{}).get(lvl)
        if not p: continue
        cnt+=1
        if p.get("tuition"): t+=1
        if isinstance(p.get("tuition"),dict) and p["tuition"].get("fields"): by+=1
        if p.get("scholarship"): sc+=1
        if p.get("period"): pe+=1
    print(f"[{lvl}] n={cnt} tuition={t} by_dept={by} sch={sc} period={pe}")
print(f"총 학교: {len(db['schools'])}")

# ---- data.js ----
content=open(r"C:\Users\USER\camnemi-crm\data.js",encoding="utf-8").read()
s=content.find("[");d=0
for i in range(s,len(content)):
    if content[i]=="[":d+=1
    elif content[i]=="]":
        d-=1
        if d==0: end=i; break
data=json.loads(content[s:end+1])
print("\n========== data.js (사이트) ==========")
for typ in ["univ","junior"]:
    arr=[u for u in data if u.get("type")==typ]
    t=0; by=0; sc=0; pe=0
    for u in arr:
        if u.get("tuition"): t+=1
        if isinstance(u.get("tuition"),dict) and isinstance(u["tuition"].get("ba"),dict) and u["tuition"]["ba"].get("fields"): by+=1
        if u.get("scholarships"): sc+=1
        if u.get("period"): pe+=1
    print(f"[{typ}] n={len(arr)} tuition={t} by_dept={by} sch={sc} period={pe}")
print(f"총 엔트리: {len(data)}")
