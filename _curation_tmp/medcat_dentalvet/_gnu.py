# -*- coding: utf-8 -*-
import os, re
D = r"C:/Users/USER/camnemi-crm/_curation_tmp/medcat_dentalvet"
def clean(f):
    return re.sub(r"[ \t]+"," ",open(os.path.join(D,f),encoding="utf-8").read().replace("\x00"," "))
def windows(f, kw, idxs, before, after):
    t=clean(f)
    print(f"\n########## {f} kw={kw} len={len(t)}")
    ms=[m for m in re.finditer(re.escape(kw),t)]
    for i in idxs:
        if i>=len(ms): print(f"  #{i} not present"); continue
        m=ms[i]; s=max(0,m.start()-before); e=min(len(t),m.end()+after)
        print(f"  --- #{i} @{m.start()}:\n  {t[s:e]}")

# 경상국립 - recruitment context
windows("경상국립대학교_2026_수의예과.txt","수의예과",[0],700,500)
windows("경상국립대학교_2026_수의예과.txt","외국인",[2],300,300)
