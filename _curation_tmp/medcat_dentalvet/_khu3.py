# -*- coding: utf-8 -*-
import os, re
D = r"C:/Users/USER/camnemi-crm/_curation_tmp/medcat_dentalvet"
def clean(f):
    return re.sub(r"[ \t]+"," ",open(os.path.join(D,f),encoding="utf-8").read().replace("\x00"," "))
t = clean("경희대학교_2027_치의예과.txt")
for kw in ["의과대학","한의과대학","치과대학","의예과","한의예과","치의예과","약학과"]:
    for m in re.finditer(re.escape(kw),t):
        s=max(0,m.start()-300); e=min(len(t),m.end()+300)
        print(f"### {kw} @{m.start()}:\n    ...{t[s:e]}...\n")
