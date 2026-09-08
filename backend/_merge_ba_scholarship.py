# -*- coding: utf-8 -*-
"""Merge _scholarship_categorized.json into consulting_db BA + verified_kb BA scholarships."""
import json, re

DB = r"C:\Users\USER\camnemi-crm\backend\consulting_db.json"
KB_PATH = r"C:\Users\USER\camnemi-crm\backend\verified_kb.json"
CAT = json.load(open(r"C:\Users\USER\camnemi-crm\backend\_scholarship_categorized.json", encoding="utf-8"))

def norm(s): return re.sub(r"\[.*?\]","",s).replace("대학교","").replace("대학","").replace(" ","")
# build norm->orig lookup for CAT
cat_norm = {norm(k): k for k in CAT}

# consulting DB: apply to BA programs missing scholarship
db = json.load(open(DB, encoding="utf-8"))
c_updated=0
for name, s in db["schools"].items():
    prog = s["programs"].get("BA")
    if not prog or prog.get("scholarship"): continue
    sn = norm(name)
    if sn in cat_norm:
        prog["scholarship"] = CAT[cat_norm[sn]]
        c_updated+=1
json.dump(db, open(DB,"w",encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"consulting BA 장학금 병합: {c_updated}")

# verified_kb: apply to BA schools missing scholarships
kb = json.load(open(KB_PATH, encoding="utf-8"))
k_updated=0
for name, v in kb["schools"].items():
    if v.get("scholarships") or v.get("scholarships_categorized"): continue
    sn = norm(name)
    if sn in cat_norm:
        v["scholarships_categorized"] = CAT[cat_norm[sn]]
        k_updated+=1
json.dump(kb, open(KB_PATH,"w",encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"verified_kb BA 장학금 병합: {k_updated}")

# recount
db2=json.load(open(DB,encoding="utf-8"))
ba=[(s['programs']['BA'],k) for k,s in db2['schools'].items() if 'BA' in s['programs']]
sch=sum(1 for e,k in ba if e.get('scholarship'))
print(f"consulting BA 장학금 최종: {sch}/{len(ba)}")
