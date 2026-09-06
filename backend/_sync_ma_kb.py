# -*- coding: utf-8 -*-
"""Sync MA scan (tuition/topik/ielts/scholarship/period) into verified_kb master section,
so the source KB is complete (not just consulting_db)."""
import json, re, os

KB_PATH = r"C:\Users\USER\camnemi-crm\backend\verified_kb.json"
kb = json.load(open(KB_PATH, encoding="utf-8"))
ma = kb["master"]["schools"]

# from consulting_db MA (already has merged scan data)
cdb = json.load(open(r"C:\Users\USER\camnemi-crm\backend\consulting_db.json", encoding="utf-8"))
cdb_schools = cdb["schools"]

def norm(s): return re.sub(r"\[.*?\]","",s).replace("대학교","").replace("대학","").replace(" ","")

# build lookup: cdb school -> its MA program
ma_data = {}
for n, s in cdb_schools.items():
    prog = s["programs"].get("MA")
    if prog:
        ma_data[norm(n)] = prog

updated=0
for n, v in ma.items():
    sn = norm(n)
    md = ma_data.get(sn)
    if not md: continue
    if md.get("tuition") and not v.get("tuition"):
        v["tuition"] = md["tuition"]; updated+=1
    if md.get("tuition_max") and not v.get("tuition_max"):
        v["tuition_max"] = md["tuition_max"]; updated+=1
    if md.get("topik") and not v.get("topik_req"):
        v["topik_req"] = md["topik"]; updated+=1
    if md.get("ielts") and not v.get("ielts_req"):
        v["ielts_req"] = md["ielts"]; updated+=1
    if md.get("toefl") and not v.get("toefl_req"):
        v["toefl_req"] = md["toefl"]; updated+=1
    if md.get("period") and not v.get("period"):
        v["period"] = md["period"]; updated+=1
    if md.get("scholarship") and not v.get("scholarships"):
        v["scholarships"] = md["scholarship"]; updated+=1
    if md.get("scholarship_topik6") and not v.get("scholarship_topik6_verified"):
        v["scholarship_topik6_verified"] = md["scholarship_topik6"]; updated+=1
    if md.get("popular_majors"):
        v["popular_majors"] = md["popular_majors"]

json.dump(kb, open(KB_PATH,"w",encoding="utf-8"), ensure_ascii=False, indent=2)
n_tuit=sum(1 for v in ma.values() if v.get("tuition"))
n_topik=sum(1 for v in ma.values() if v.get("topik_req"))
n_ielts=sum(1 for v in ma.values() if v.get("ielts_req"))
n_period=sum(1 for v in ma.values() if v.get("period"))
n_sch=sum(1 for v in ma.values() if v.get("scholarships"))
n_topik6=sum(1 for v in ma.values() if v.get("scholarship_topik6_verified"))
print(f"MA 동기화: {updated} 필드 갱신")
print(f"  수업료 {n_tuit} | TOPIK {n_topik} | IELTS {n_ielts} | 기간 {n_period} | 장학 {n_sch} | TOPIK6 {n_topik6}")
