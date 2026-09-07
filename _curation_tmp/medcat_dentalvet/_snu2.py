# -*- coding: utf-8 -*-
import os, re
D = r"C:/Users/USER/camnemi-crm/_curation_tmp/medcat_dentalvet"
def clean(f):
    return re.sub(r"[ \t]+"," ",open(os.path.join(D,f),encoding="utf-8").read().replace("\x00"," "))
def scan(f, kws, w):
    t=clean(f); print("\n##########",f,"len",len(t))
    for kw in kws:
        cand=[m for m in re.finditer(re.escape(kw),t) if m.start()>2000]
        if not cand: print("   no-body",kw); continue
        m=cand[0]; s=max(0,m.start()-w); e=min(len(t),m.end()+w)
        print(f"\n  [{kw}] @{m.start()}:\n  {t[s:e]}")
for f in ["서울대학교_2026_수의예과.txt"]:
    scan(f, ["TOPIK","지원자격","전형방법","서류평가","면접","원서접수"], 150)
