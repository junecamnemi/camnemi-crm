# -*- coding: utf-8 -*-
import os, re
D = r"C:/Users/USER/camnemi-crm/_curation_tmp/medcat_dentalvet"
def clean(f):
    return re.sub(r"[ \t]+"," ",open(os.path.join(D,f),encoding="utf-8").read().replace("\x00"," "))
for f in ["제주대학교_2026_수의예과.txt","제주대학교_2027_수의예과.txt"]:
    t=clean(f)
    print(f"\n########## {f} len {len(t)}  count 수의예과={t.count('수의예과')} 의예과={t.count('의예과')} 간호학과={t.count('간호학과')}")
    for k in ["수의예과"]:
        for i,m in enumerate(re.finditer(re.escape(k),t)):
            s=max(0,m.start()-1200); e=min(len(t),m.end()+400)
            print(f"\n--- {k}#{i} @{m.start()}\n{t[s:e]}")
