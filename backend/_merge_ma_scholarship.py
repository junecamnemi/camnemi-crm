# -*- coding: utf-8 -*-
"""Merge MA scholarship scan into consulting_db + verified_kb master MA programs."""
import json, re

DB = r"C:\Users\USER\camnemi-crm\backend\consulting_db.json"
KB_PATH = r"C:\Users\USER\camnemi-crm\backend\verified_kb.json"
SCAN = json.load(open(r"C:\Users\USER\camnemi-crm\backend\_ma_scholarship_scan.json", encoding="utf-8"))

def norm(s): return re.sub(r"\[.*?\]","",s).replace("대학교","").replace("대학","").replace("대학원","").replace(" ","")

# normalize scan keys (가톨릭대일반대학원 -> 가톨릭대)
def scan_norm(s):
    return re.sub(r"일반대학원|특수대학원|산업대학원|\.pdf","",s).replace("대학교","").replace("대학","").replace(" ","")
scan_by_norm = {scan_norm(s): v for s,v in SCAN.items()}

# update consulting DB
db = json.load(open(DB, encoding="utf-8"))
updated=0
for name, s in db["schools"].items():
    prog = s["programs"].get("MA")
    if not prog or prog.get("scholarship"): continue
    sn = norm(name)
    # try direct, then scan_norm match
    if sn in scan_by_norm:
        prog["scholarship"] = scan_by_norm[sn]; updated+=1
    else:
        # fuzzy: match any scan key contained in school name or vice versa
        for sk, sv in scan_by_norm.items():
            if sk in sn or sn in sk:
                prog["scholarship"] = sv; updated+=1
                break
json.dump(db, open(DB,"w",encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"consulting_db MA 장학금 병합: {updated}개")

# also update verified_kb master
kb = json.load(open(KB_PATH, encoding="utf-8"))
kb_updated=0
for name, v in kb["master"]["schools"].items():
    if v.get("scholarships"): continue
    sn = norm(name)
    if sn in scan_by_norm:
        v["scholarships"] = scan_by_norm[sn]; kb_updated+=1
    else:
        for sk, sv in scan_by_norm.items():
            if sk in sn or sn in sk:
                v["scholarships"] = sv; kb_updated+=1
                break
json.dump(kb, open(KB_PATH,"w",encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"verified_kb master 장학금 병합: {kb_updated}개")
