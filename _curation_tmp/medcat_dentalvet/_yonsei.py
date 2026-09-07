# -*- coding: utf-8 -*-
import os, re
D = r"C:/Users/USER/camnemi-crm/_curation_tmp/medcat_dentalvet"
def clean(f):
    return re.sub(r"[ \t]+"," ",open(os.path.join(D,f),encoding="utf-8").read().replace("\x00"," "))
def find_first(f, pats, w):
    t=clean(f); print("\n##########",f)
    for p in pats:
        for m in re.finditer(p,t):
            s=max(0,m.start()-w); e=min(len(t),m.end()+w)
            print(f"  [{p}] @{m.start()}: {t[s:e]}\n"); break

# YONSEI - language req, schedule
find_first("연세대학교_2027_치의예과.txt", [r"TOPIK|한국어능력|언어능력|공인영어|접수기간|원서접수"], 150)
find_first("연세대학교_2026_치의예과.txt", [r"TOPIK|한국어능력|언어능력|접수기간|원서접수"], 150)
