# -*- coding: utf-8 -*-
import os, re
D = r"C:/Users/USER/camnemi-crm/_curation_tmp/medcat_dentalvet"

def clean(f):
    t = open(os.path.join(D, f), encoding="utf-8").read()
    t = t.replace("\u0001", " ")
    t = t.replace("\x00"," ")
    t = re.sub(r"[ \t]+", " ", t)
    return t

def show(f, n=3, w=700):
    t = clean(f)
    print("#"*100)
    print("FILE", f, "len", len(t))
    print("외국인 count:", t.count("외국인"), "| 재외국민 count:", t.count("재외국민"), "| 국적구분:", set(re.findall(r"재외국민|외국인", t)) )
    # print frequency of 모집단위/모집 인원 table markers
    for kw in ["모집하지않음","모집하지 않음","지원불가","불가","제외","선발하지","선발하지않음","미선발","외국인전용","정원외","학과장 사전승인"]:
        c = t.count(kw)
        if c: print(f"   marker {kw}: {c}")

for f in ["대전대학교_2027_한의예과.txt","서울대학교_2026_수의예과.txt","제주대학교_2026_수의예과.txt","경상국립대학교_2026_수의예과.txt","경희대학교_2027_치의예과.txt","건국대학교_2026_수의예과.txt","연세대학교_2027_치의예과.txt"]:
    show(f)
