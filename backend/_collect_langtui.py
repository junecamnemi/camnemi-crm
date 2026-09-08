# -*- coding: utf-8 -*-
"""Normalize + merge lang tuition results (batch 0,1,3) into KB lang_programs + consulting."""
import json, re, os, glob

def norm(s):
    s = re.sub(r"\[.*?\]","",s)
    s = s.replace("대학교","").replace("전문대학","").replace("전문대","")
    while s.endswith(("대학","대")) and len(s)>1:
        s = s[:-1] if s.endswith("대") else s[:-2]
    return s.replace(" ","")

# collect all results (handle list or dict form)
results = {}
for fp in glob.glob(r"C:\Users\USER\camnemi-crm\backend\_langtui_result*.json"):
    data = json.load(open(fp, encoding="utf-8"))
    items = data.items() if isinstance(data, dict) else [(x.get("school"), x) for x in data if isinstance(x,dict)]
    for k, v in items:
        results[k] = v
print(f"총 어학 수업료 결과: {len(results)}개")
for k,v in results.items():
    if v.get("tuition"): print(f"  ✓ {k}: {v['tuition']}")
    else: print(f"  ✗ {k}: 미확보")
