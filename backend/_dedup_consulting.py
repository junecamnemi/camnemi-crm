# -*- coding: utf-8 -*-
"""Deduplicate consulting_db. Fixed norm strips trailing 대/대학/대학교/전문대."""
import json, re

DB = r"C:\Users\USER\camnemi-crm\backend\consulting_db.json"
db = json.load(open(DB, encoding="utf-8"))
schools = db["schools"]

def norm(s):
    s = re.sub(r"\[.*?\]","",s)
    s = s.replace("대학교","").replace("전문대학","").replace("전문대","")
    # strip trailing 대/대학
    while s.endswith(("대학","대","학")) and len(s)>1:
        s = s[:-1] if s.endswith(("대","학")) else s[:-2]
    return s.replace(" ","")

def filled(d): return sum(1 for v in (d or {}).values() if v)

groups = {}
for name in list(schools.keys()):
    groups.setdefault(norm(name), []).append(name)

merged = []
for nk, names in groups.items():
    if len(names) <= 1: continue
    canonical = next((n for n in names if '대학교' in n), None) or sorted(names, key=len)[-1]
    others = [n for n in names if n != canonical]
    keep_prog = schools[canonical]["programs"]
    for dup in others:
        dp = schools[dup]["programs"]
        for lv in dp:
            if lv not in keep_prog:
                keep_prog[lv] = dp[lv]
            else:
                if filled(dp[lv]) > filled(keep_prog[lv]):
                    for f,val in keep_prog[lv].items():
                        if val and not dp[lv].get(f): dp[lv][f]=val
                    keep_prog[lv]=dp[lv]
                else:
                    for f,val in dp[lv].items():
                        if val and not keep_prog[lv].get(f): keep_prog[lv][f]=val
        for f in ["region","rank"]:
            if not schools[canonical].get(f) and schools[dup].get(f):
                schools[canonical][f]=schools[dup][f]
        merged.append((dup, canonical))

new_schools = {n:s for n,s in schools.items() if n not in [m[0] for m in merged]}
db["schools"] = new_schools
json.dump(db, open(DB,"w",encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"중복 통합 {len(merged)}개 → 총 {len(new_schools)} 학교")
for d,k in merged: print(f"  {d} → {k}")
