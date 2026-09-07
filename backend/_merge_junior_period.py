# -*- coding: utf-8 -*-
"""Merge valid junior periods into consulting_db; invalid/old ones dropped."""
import json, re

DB = r"C:\Users\USER\camnemi-crm\backend\consulting_db.json"
SCAN = json.load(open(r"C:\Users\USER\camnemi-crm\backend\_junior_period_scan.json", encoding="utf-8"))
db = json.load(open(DB, encoding="utf-8"))
schools = db["schools"]

def norm(s): return re.sub(r"\[.*?\]","",s).replace("대학교","").replace("대학","").replace(" ","")

def is_valid(p):
    # must contain 2025/2026/2027 and look like a real application window
    if not re.search(r"202[5-7]", p): return False
    if re.search(r"20(1[0-9]|2[0-4])", p): return False  # old year
    return True

merged=0
for school, p in SCAN.items():
    if not is_valid(p): continue
    sn = norm(school)
    for k,s in schools.items():
        if norm(k)==sn:
            prog=s["programs"].get("전문학사")
            if prog and not prog.get("period"):
                prog["period"]=p; merged+=1
            break

json.dump(db, open(DB,"w",encoding="utf-8"), ensure_ascii=False, indent=1)
n=sum(1 for s in schools.values() if s["programs"].get("전문학사",{}).get("period"))
print(f"전문학사 유효 지원시기 병합 {merged} → 총 {n}개")
