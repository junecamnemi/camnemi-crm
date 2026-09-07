# -*- coding: utf-8 -*-
import os, re
D = r"C:/Users/USER/camnemi-crm/_curation_tmp/medcat_dentalvet"

def clean(f):
    t = open(os.path.join(D, f), encoding="utf-8").read()
    t = t.replace("\u0001", " ").replace("\x00"," ")
    t = re.sub(r"[ \t]+"," ", t)
    return t

def dump_occ(f, kw, w=650, maxn=40):
    t = clean(f)
    print("#"*110); print("FILE",f,"kw",kw)
    n=0
    for m in re.finditer(re.escape(kw), t):
        s=max(0,m.start()-w); e=min(len(t),m.end()+w)
        print(f"--- [{kw}@{m.start()}] ...{t[s:e]}...")
        n+=1
        if n>=maxn: break

dump_occ("대전대학교_2027_한의예과.txt", "외국인", w=500)
