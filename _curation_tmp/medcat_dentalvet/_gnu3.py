# -*- coding: utf-8 -*-
import os, re
D = r"C:/Users/USER/camnemi-crm/_curation_tmp/medcat_dentalvet"
def clean(f):
    return re.sub(r"[ \t]+"," ",open(os.path.join(D,f),encoding="utf-8").read().replace("\x00"," "))
t=clean("경상국립대학교_2026_수의예과.txt")
m=re.search("모집 단위 및 인원",t)
# find the section body (after the TOC occurrence). Take all occurrences
for i,mm in enumerate(re.finditer("4\\.\s*모집 단위 및 인원|모집단위 및 인원|모집 단위 및 인원",t)):
    s=mm.start(); print(f"### occ {i} @{s}")
# print big chunk starting from the body occurrence of "모집 단위 및 인원" that is page5 content (likely last occurrence)
occ=[mm.start() for mm in re.finditer("모집 단위 및 인원",t)]
print("positions",occ)
p=occ[-1]
print(t[p:p+4000])
