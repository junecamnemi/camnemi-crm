# -*- coding: utf-8 -*-
import os, re
D = r"C:/Users/USER/camnemi-crm/_curation_tmp/medcat_dentalvet"
def clean(f):
    return re.sub(r"[ \t]+"," ",open(os.path.join(D,f),encoding="utf-8").read().replace("\x00"," "))
t=clean("건국대학교_2026_수의예과.txt")
print("len",len(t))
for i,m in enumerate(re.finditer("수의예과",t)):
    s=max(0,m.start()-2600); e=min(len(t),m.end()+200)
    print(f"\n===== 수의예과#{i} @{m.start()}\n{t[s:e]}")
    if i>=2: break
