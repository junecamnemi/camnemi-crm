# -*- coding: utf-8 -*-
import os, re
D = r"C:/Users/USER/camnemi-crm/_curation_tmp/medcat_dentalvet"
def clean(f):
    return re.sub(r"[ \t]+"," ",open(os.path.join(D,f),encoding="utf-8").read().replace("\x00"," "))
t=clean("경상국립대학교_2026_수의예과.txt")
pages=[(m.start(),m.group(1)) for m in re.finditer(r"- (\d+) -\s*$",t)]
pages2=[(m.start(),m.group(1)) for m in re.finditer(r"- (\d+) -",t)]
# print unique around markers that are page top (heading) not bottom
print("markers count",len(pages2))
# show first 15 markers positions
for p in pages2[:20]: print(p, t[p:p+40].replace("\n"," "))
