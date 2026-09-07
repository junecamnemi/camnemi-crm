# -*- coding: utf-8 -*-
import os, re
D = r"C:/Users/USER/camnemi-crm/_curation_tmp/medcat_dentalvet"
def clean(f):
    return re.sub(r"[ \t]+"," ",open(os.path.join(D,f),encoding="utf-8").read().replace("\x00"," "))
def dump_occ(f, kw, w, maxn):
    t=clean(f)
    print("#"*115); print("FILE",f,"kw",kw,"len",len(t))
    c=0
    for m in re.finditer(re.escape(kw),t):
        s=max(0,m.start()-w); e=min(len(t),m.end()+w)
        print(f"--- @{m.start()}: ...{t[s:e]}...")
        c+=1
        if c>=maxn: break
    if c==0: print("   (no occurrence)")
# 경희 : both majors
dump_occ("경희대학교_2027_치의예과.txt","한의예과", w=500, maxn=25)
