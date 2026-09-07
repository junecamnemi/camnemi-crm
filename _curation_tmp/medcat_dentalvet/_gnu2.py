# -*- coding: utf-8 -*-
import os, re
D = r"C:/Users/USER/camnemi-crm/_curation_tmp/medcat_dentalvet"
def clean(f):
    return re.sub(r"[ \t]+"," ",open(os.path.join(D,f),encoding="utf-8").read().replace("\x00"," "))
t=clean("경상국립대학교_2026_수의예과.txt")
for kw in ["2370","수의예과","수의학과","모집 단위 및 인원","정원"]:
    print("kw",kw,"count",t.count(kw))
# dump region around '2370' occurrences
for i,m in enumerate(re.finditer("2370",t)):
    s=max(0,m.start()-900); e=min(len(t),m.end()+600)
    print(f"\n=====2370#{i} @{m.start()}\n{t[s:e]}")
