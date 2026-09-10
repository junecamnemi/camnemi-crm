# -*- coding: utf-8 -*-
"""Add newly-scanned MA schools (58) to verified_kb master section.
Fields: name, region(from data.js), majors, lang_req, foreign_guide flag, guide_pdf."""
import json, re

KB_PATH = r"C:\Users\USER\camnemi-crm\backend\verified_kb.json"
scan = json.load(open(r"C:\Users\USER\camnemi-crm\backend\_ma_new_scan.json", encoding="utf-8"))
BASE = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project\adiga_2026_대학원_모집요강"

# region from data.js
content=open(r"C:\Users\USER\camnemi-crm\data.js",encoding="utf-8").read()
s=content.find("[");d=0
for i in range(s,len(content)):
    if content[i]=="[":d+=1
    elif content[i]=="]":
        d-=1
        if d==0: data=json.loads(content[s:i+1]);break
def norm(s):
    s=re.sub(r"\[.*?\]","",s).replace("대학교","").replace("대학원","").replace("대학","").replace(" ","")
    while s.endswith(("대학","대")) and len(s)>1: s=s[:-1]
    return s.replace(" ","")
loc={}
for u in data:
    n=u.get("n","")
    loc[norm(n)] = u.get("loc") or u.get("website","")
def get_loc(school):
    sn=norm(school)
    # direct
    if sn in loc: return loc[sn]
    for n,l in loc.items():
        if sn in n or n in sn: return l
    return None

kb=json.load(open(KB_PATH,encoding="utf-8"))
ma=kb["master"]["schools"]
ma_norm={norm(n) for n in ma}

added=0
for school,v in scan.items():
    if "error" in v: continue
    sn=norm(school)
    if sn in ma_norm: continue
    # clean school name to proper form
    entry={
        "name": school,
        "region": get_loc(school) or "",
        "lang_req": v.get("lang"),
        "majors": v.get("majors") or [],
        "tuition": v.get("tuition"),
        "period": v.get("period"),
        "guide_pdf": f"{BASE}/{v['file']}",
        "guide_status": "2026",
        "has_foreigner_guide": v.get("has_foreigner",False),
        "note": "2026 대학원 모집요강 스캔으로 추가 (외국인 전형 " + ("포함" if v.get("has_foreigner") else "미확인") + ")",
    }
    ma[school]=entry
    added+=1

kb["master"]["schools"]=ma
json.dump(kb,open(KB_PATH,"w",encoding="utf-8"),ensure_ascii=False,indent=2)
print(f"MA KB 추가: {added}개 (총 {len(ma)}개)")
