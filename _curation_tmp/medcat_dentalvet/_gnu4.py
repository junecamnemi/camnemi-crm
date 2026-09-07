# -*- coding: utf-8 -*-
import os, re
D = r"C:/Users/USER/camnemi-crm/_curation_tmp/medcat_dentalvet"
def clean(f):
    return re.sub(r"[ \t]+"," ",open(os.path.join(D,f),encoding="utf-8").read().replace("\x00"," "))
t=clean("경상국립대학교_2026_수의예과.txt")
print("수의예과 positions:",[m.start() for m in re.finditer("수의예과",t)])
print("수의학과 positions:",[m.start() for m in re.finditer("수의학과",t)])
# find 모집단위 및 인원 body (page5). look for big table with many 인원 values
for i,m in enumerate(re.finditer("인원",t)):
    pass
idx=[m.start() for m in re.finditer("인원",t)]
print("인원 positions count", len(idx))
# The page5 '4. 모집 단위 및 인원' table will contain many unit names and a count. Let's find header "모집 단위 및 인원" as a section within body - search for pattern with page marker
for m in re.finditer(r"- 5 -|모집단위  및  인원|모집 단위 및 인원", t):
    s=max(0,m.start()-200); print("HEAD",m.start(), t[s:m.start()+100].replace("\n"," | ")[-120:])
