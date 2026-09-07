# -*- coding: utf-8 -*-
import os, re
D = r"C:/Users/USER/camnemi-crm/_curation_tmp/medcat_dentalvet"
def clean(f):
    return re.sub(r"[ \t]+"," ",open(os.path.join(D,f),encoding="utf-8").read().replace("\x00"," "))
def body(f):
    return clean(f)
for f in ["연세대학교_2027_치의예과.txt","연세대학교_2026_치의예과.txt"]:
    t=body(f); print("\n##########",f,"len",len(t))
    for kw in ["TOPIK","한국어능력","접수기간","원서접수 기간","전형일정","서류평가","인성면접","지원자격"]:
        cnt=[m.start() for m in re.finditer(re.escape(kw),t)]
        # take first occurrence beyond TOC (~idx>3000)
        cand=[x for x in cnt if x>3000]
        print(f"  {kw}: n={len(cnt)}", ("body@"+str(cand[0])) if cand else "toconly")
        if cand:
            m=cand[0]; s=max(0,m-220); print("     ...",t[s:m+260],"...")
