# -*- coding: utf-8 -*-
"""Merge tuition findings from gap-fill agents into consulting_db + verified_kb.
Input: backend/_gap_fill_results.json = {school: {level, tuition(min/max or amount), source_url, note}}
"""
import json, re, os

RESULTS = r"C:\Users\USER\camnemi-crm\backend\_gap_fill_results.json"
DB = r"C:\Users\USER\camnemi-crm\backend\consulting_db.json"
KB_PATH = r"C:\Users\USER\camnemi-crm\backend\verified_kb.json"

if not os.path.exists(RESULTS):
    print("결과 파일 없음"); raise SystemExit

results = json.load(open(RESULTS, encoding="utf-8"))
def norm(s): return re.sub(r"\[.*?\]","",s).replace("대학교","").replace("대학","").replace("전문대","").replace(" ","")

# norm lookups
db = json.load(open(DB, encoding="utf-8"))
db_by_norm = {norm(k): k for k in db["schools"]}
kb = json.load(open(KB_PATH, encoding="utf-8"))

c_upd = k_upd = 0
for school, info in results.items():
    lv = info.get("level")
    t = info.get("tuition")
    if not t or not lv: continue
    sn = norm(school)
    if sn not in db_by_norm: 
        # fuzzy
        match=None
        for nk in db_by_norm:
            if sn in nk or nk in sn: match=nk; break
        if not match: 
            print(f"  ✗ 매칭 실패: {school}")
            continue
        sn = match
    orig = db_by_norm[sn]
    s = db["schools"][orig]
    prog_map = {"BA":"BA","MA":"MA","어학":"어학연수","전문학사":"전문학사"}
    key = prog_map.get(lv)
    if not key: continue
    prog = s["programs"].get(key)
    if prog and not prog.get("tuition"):
        prog["tuition"] = t
        if info.get("tuition_max"): prog["tuition_max"]=info["tuition_max"]
        if info.get("source_url"): prog["tuition_src"]=info["source_url"]
        c_upd+=1
    # verified_kb
    if lv=="BA" and orig in kb["schools"] and not kb["schools"][orig].get("tuition_semester"):
        kb["schools"][orig]["tuition_semester"]=t; k_upd+=1
    elif lv=="MA" and orig in kb["master"]["schools"] and not kb["master"]["schools"][orig].get("tuition"):
        kb["master"]["schools"][orig]["tuition"]=t; k_upd+=1

json.dump(db, open(DB,"w",encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(kb, open(KB_PATH,"w",encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"병합: consulting {c_upd} | verified_kb {k_upd}")
