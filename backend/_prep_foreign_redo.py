# -*- coding: utf-8 -*-
"""Create small batches (4 each) for foreigner-only redownload of 40 junior colleges."""
import json, os

reclass = json.load(open(r"C:\Users\USER\camnemi-crm\backend\_junior_foreign_class.json", encoding="utf-8"))
redo = reclass["redownload"]
KB = json.load(open(r"C:\Users\USER\camnemi-crm\backend\verified_kb.json", encoding="utf-8"))
js = KB["junior"]["schools"]

# also include the 2 that were never downloaded (동서울대, 충북보건과학대) if not in list
missing_never = ["동서울대학교","충북보건과학대학교"]
schools = []
seen=set()
for r in redo:
    s=r["school"]
    if s in seen: continue
    seen.add(s)
    schools.append({"school":s, "file":r.get("file"), "guide_url":js.get(s,{}).get("guide_url",""), "region":js.get(s,{}).get("region","")})
for s in missing_never:
    if s not in seen:
        schools.append({"school":s, "guide_url":js.get(s,{}).get("guide_url","")})

print(f"재확보 대상(고유): {len(schools)}")
BATCH=4
batches=[schools[i:i+BATCH] for i in range(0,len(schools),BATCH)]
for i,b in enumerate(batches):
    json.dump(b, open(rf"C:\Users\USER\camnemi-crm\backend\_foreign_batch{i}.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"배치 {len(batches)}개")
for i,b in enumerate(batches): print(f"  batch{i}: {', '.join(x['school'] for x in b)}")
