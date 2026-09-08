# -*- coding: utf-8 -*-
"""Normalize + merge lang tuition results into consulting_db + verified_kb.
Handles field variants: tuition / tuition_per_term / tuition_range, dict or list forms."""
import json, re, glob

def norm(s):
    s = re.sub(r"\[.*?\]","",s)
    s = s.replace("대학교","").replace("전문대학","").replace("전문대","")
    while s.endswith(("대학","대")) and len(s)>1:
        s = s[:-1] if s.endswith("대") else s[:-2]
    return s.replace(" ","")

def get_tuition(x):
    for k in ["tuition","tuition_range","tuition_per_term"]:
        v = x.get(k)
        if v: return v
    return None

# collect
results = {}
for fp in glob.glob(r"C:\Users\USER\camnemi-crm\backend\_langtui_result*.json"):
    data = json.load(open(fp, encoding="utf-8"))
    if isinstance(data, dict):
        entries = data.values()  # dict keyed by school -> school dict
    else:
        entries = data
    for x in entries:
        if isinstance(x, dict):
            school = x.get("school") or x.get("name")
            if not school: continue
            t = get_tuition(x)
            if t:
                results[school] = {"school":school, "tuition":t,
                                   "note":x.get("note") or x.get("tuition_note",""),
                                   "source":x.get("source_url") or x.get("source",""),
                                   "status":x.get("status","")}

json.dump(results, open(r"C:\Users\USER\camnemi-crm\backend\_langtui_all.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"확보된 어학 수업료: {len(results)}개")
for k,v in results.items():
    print(f"  ✓ {k}: {v['tuition']}")
