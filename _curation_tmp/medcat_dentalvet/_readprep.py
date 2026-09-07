# -*- coding: utf-8 -*-
import os, re
D = r"C:/Users/USER/camnemi-crm/_curation_tmp/medcat_dentalvet"
def clean(f):
    t = open(os.path.join(D,f),encoding="utf-8").read().replace("\u0001"," ").replace("\x00"," ")
    return re.sub(r"[ \t]+"," ",t)
out = []
for f in ["대전대학교_2027_한의예과.txt"]:
    out.append(f"######## {f} ########\n"+clean(f))
open(os.path.join(D,"_READ_djeon.txt"),"w",encoding="utf-8").write("\n".join(out))
print("written", os.path.join(D,"_READ_djeon.txt"))
