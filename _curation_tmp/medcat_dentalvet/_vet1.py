# -*- coding: utf-8 -*-
import os, re
D = r"C:/Users/USER/camnemi-crm/_curation_tmp/medcat_dentalvet"
def clean(f):
    return re.sub(r"[ \t]+"," ",open(os.path.join(D,f),encoding="utf-8").read().replace("\x00"," "))
def occ(f, kw, w, maxn=20):
    t=clean(f); out=[f"===== {f} / kw {kw} ====="]
    c=0
    for m in re.finditer(re.escape(kw),t):
        s=max(0,m.start()-w); e=min(len(t),m.end()+w)
        out.append(f"--- @{m.start()}:\n...{t[s:e]}...")
        c+=1
        if c>=maxn: break
    if c==0: out.append("(none)")
    return "\n".join(out)

buf=[]
for f, kws in [
    ("서울대학교_2026_수의예과.txt", ["수의예과","수의학과","지원할 수 없","선발하지","지원불가","모집하지"]),
    ("서울대학교_2027_수의예과.txt", ["수의예과","수의학과","지원할 수 없","선발하지","지원불가","모집하지"]),
    ("제주대학교_2026_수의예과.txt", ["수의예과","수의학과","지원할 수 없","지원불가","모집하지","미모집","선발하지"]),
]:
    for k in kws: buf.append(occ(f,k, w=650))
open(os.path.join(D,"_READ_vet_snu_jeju.txt"),"w",encoding="utf-8").write("\n\n".join(buf))
print("written")
