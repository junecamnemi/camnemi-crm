# -*- coding: utf-8 -*-
import os, re
D = r"C:/Users/USER/camnemi-crm/_curation_tmp/medcat_dentalvet"
def clean(f):
    return re.sub(r"[ \t]+"," ",open(os.path.join(D,f),encoding="utf-8").read().replace("\x00"," "))
t=clean("서울대학교_2027_수의예과.txt")
print("len",len(t),"수의예과",t.count("수의예과"))
for kw in ["TOPIK","한국어","지원자격","모집단위"]:
    cand=[m for m in re.finditer(re.escape(kw),t) if m.start()>2000]
    if cand:
        m=cand[0]; s=max(0,m.start()-150); print(f"\n[{kw}]@",m.start(),":",t[s:m.end()+150])
