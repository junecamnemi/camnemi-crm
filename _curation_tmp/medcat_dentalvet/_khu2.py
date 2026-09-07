# -*- coding: utf-8 -*-
import os, re
D = r"C:/Users/USER/camnemi-crm/_curation_tmp/medcat_dentalvet"
def clean(f):
    return re.sub(r"[ \t]+"," ",open(os.path.join(D,f),encoding="utf-8").read().replace("\x00"," "))
t = clean("경희대학교_2027_치의예과.txt")
for kw in ["의과대학","한의과대학","치과대학","약학과","의예과","한의예과","치의예과","서울캠퍼스 개설학부","모집단위에","미개설","개설하지","모집하지"]:
    print("###",kw, "count", t.count(kw))
