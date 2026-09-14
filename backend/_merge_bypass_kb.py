# -*- coding: utf-8 -*-
"""Merge BOTH structured bypass files into KB lang_bypass (handles both key formats)."""
import json, re

KB = r"C:\Users\USER\camnemi-crm\backend\verified_kb.json"
SRC = [r"C:\Users\USER\camnemi-crm\backend\_bypass_structured.json",
       r"C:\Users\USER\camnemi-crm\backend\_bypass_mis_structured.json"]
# preserve hand-curated 경운대
KYW = None
kb = json.load(open(KB, encoding="utf-8"))
KYW = kb["schools"].get("경운대학교", {}).get("lang_bypass")

LEVELS = {"BA","MA","junior"}
def is_struct(v):
    p = v.get("paths") if isinstance(v,dict) else None
    return isinstance(p,list) and p and all(isinstance(x,dict) and "type" in x for x in p)

def norm(s):
    s = re.sub(r"\[.*?\]|\(.*?\)","",str(s)); s = re.sub(r"^\d+_","",s)
    for suf in ["대학원대학교","대학교","대학원","대학","전문대학","전문대"]:
        if s.endswith(suf): s=s[:-len(suf)]; break
    if s.endswith("대") and len(s)>1: s=s[:-1]
    return s.replace(" ","").replace("_","")

pairs=[]
for fp in SRC:
    try: d=json.load(open(fp,encoding="utf-8"))
    except Exception: continue
    for k,v in d.items():
        if not isinstance(v,dict): continue
        if k in LEVELS:
            for sub,sv in v.items():
                if is_struct(sv): pairs.append((k,sub,sv))
            continue
        m1=re.match(r"^(BA|MA|junior):(.+)$",k)
        m2=re.match(r"^(.+)\|(BA|MA|junior)$",k)
        if m1 and is_struct(v): pairs.append((m1.group(1),m1.group(2),v))
        elif m2 and is_struct(v): pairs.append((m2.group(2),m2.group(1),v))

ded={}
for lvl,school,v in pairs:
    key=(lvl,norm(school))
    if key not in ded or len(v["paths"])>len(ded[key][2]["paths"]):
        ded[key]=(lvl,school,v)
print(f"pairs {len(pairs)} → dedupe {len(ded)}")

SEC={"BA":"schools","MA":"master","junior":"junior"}
added=0; miss=[]
for (lvl,sn),(_,school,v) in ded.items():
    sec=kb[SEC[lvl]]; schools=sec.get("schools",sec)
    tgt=next((n for n in schools if norm(n)==sn), None)
    if not tgt:
        for n in schools:
            nn=norm(n)
            if len(sn)>=3 and (nn.startswith(sn) or sn.startswith(nn)): tgt=n; break
    if not tgt: miss.append(f"{lvl}:{school}"); continue
    if not v["paths"]: continue          # skip empty
    schools[tgt]["lang_bypass"]={"source":"외국인 모집요강 추출 (pro model)","paths":v["paths"],
                                 **({"notes":v["notes"]} if v.get("notes") else {})}
    added+=1

if KYW: kb["schools"]["경운대학교"]["lang_bypass"]=KYW   # restore curated

json.dump(kb, open(KB,"w",encoding="utf-8"), ensure_ascii=False, indent=2)
t=0
for sec,key in [("BA","schools"),("MA","master"),("junior","junior")]:
    sch=kb[key]["schools"] if "schools" in kb[key] else kb[key]
    c=sum(1 for x in sch.values() if x.get("lang_bypass")); t+=c
    print(f"  {sec}: {c}/{len(sch)}")
print(f"총 lang_bypass: {t} | 병합 {added} | 매칭실패 {len(miss)}")
