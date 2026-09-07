# -*- coding: utf-8 -*-
import os, re
D = r"C:/Users/USER/camnemi-crm/_curation_tmp/medcat_dentalvet"
def clean(f):
    return re.sub(r"[ \t]+"," ",open(os.path.join(D,f),encoding="utf-8").read().replace("\x00"," "))
def window(f, kw, idx, before, after):
    t=clean(f)
    ms=[m for m in re.finditer(re.escape(kw),t)]
    m=ms[idx]; s=max(0,m.start()-before); e=min(len(t),m.end()+after)
    print(f"\n##### {f} {kw} #{idx} @{m.start()}\n{t[s:e]}")
# SNU 모집단위 list contexts (occurrence 0 likely the college list)
window("서울대학교_2026_수의예과.txt","수의예과",0,1500,900)
