#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the 일자리 매뉴얼: merge employment paths + render a branded PDF (navy/gold, Camnemi)."""
import json, os
B = r"C:\Users\wisew\camnemi-crm\backend"
job = json.load(open(os.path.join(B,"job_manual_kr.json"), encoding="utf-8"))
vkb = json.load(open(os.path.join(B,"visa_kb_kr.json"), encoding="utf-8"))

# --- augment employment paths from change_matrix + income ---
cm = vkb.get("change_matrix", {})
inc = vkb.get("income_requirements", {})
paths = { (p.get("from"),p.get("to")): p for p in job.get("employment_paths",[]) }
def add(frm, to, cond, income, note=""):
    if (frm,to) not in paths:
        job.setdefault("employment_paths",[]).append({"from":frm,"to":to,"condition":cond,"income":income,"note":note})

d2 = cm.get("D-2", {}).get("can_change_to", []) if isinstance(cm.get("D-2"),dict) else []
for x in d2:
    t = x.get("to","") if isinstance(x,dict) else str(x)
    if "E-7" in t or "D-10" in t or "F-2" in t or "F-5" in t:
        add("D-2 유학", t, x.get("condition","") if isinstance(x,dict) else "", x.get("income","") if isinstance(x,dict) else "")
e9 = cm.get("E-9", {}).get("can_change_to", []) if isinstance(cm.get("E-9"),dict) else []
for x in e9:
    add("E-9", x.get("to","") if isinstance(x,dict) else str(x), x.get("condition","") if isinstance(x,dict) else "", x.get("income","") if isinstance(x,dict) else "")
add("D-2 유학","E-7 (특정활동)","졸업+취업 확정 시 바로 변경",
    inc.get("E-7-1_전문인력",{}).get("연봉","") if isinstance(inc.get("E-7-1_전문인력"),dict) else "")
add("D-2 유학","D-10 (구직)","졸업 후 미취업 (최대 2년)", "재정능력 증빙")
add("D-4 어학연수","D-2 (유학)","국내에서 학위과정 입학 → 개강 전 변경","")
add("E-9","E-7-4 (숙련기능인력)","5년 이상 근무(4년+KIIP3)","연 2,600만원↑")

json.dump(job, open(os.path.join(B,"job_manual_kr.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
print("취업경로:", len(job.get("employment_paths",[])))
for p in job["employment_paths"]: print("  ", p.get("from"),"→",p.get("to"))
