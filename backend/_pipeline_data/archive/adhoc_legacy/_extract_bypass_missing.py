# -*- coding: utf-8 -*-
"""Re-extract bypass info for schools that currently LACK lang_bypass.
Broader patterns + multi-keyword windows + explicit '지원자격' section capture."""
import os, re, json
import pymupdf

BASE = r"C:\Users\wisew\내 드라이브\02_Crawling_Sheet\University_Project"
KB = r"C:\Users\wisew\camnemi-crm\backend\verified_kb.json"
FOLDERS = {
    "BA": [os.path.join(BASE,"adiga_2027_외국인_모집요강","외국인"),
           os.path.join(BASE,"adiga_2026_외국인_모집요강","외국인")],
    "MA": [os.path.join(BASE,"adiga_2026_대학원_모집요강")],
    "junior": [os.path.join(BASE,"adiga_2026_전문대학_모집요강")],
}
kb = json.load(open(KB, encoding="utf-8"))

def norm(x):
    x = re.sub(r"\[.*?\]|\(.*?\)","",str(x))
    for suf in ["대학원대학교","대학교","대학원","대학","전문대학","전문대"]:
        if x.endswith(suf): x=x[:-len(suf)]; break
    if x.endswith("대") and len(x)>1: x=x[:-1]
    return x.replace(" ","")

# missing schools per level
missing = {}
for sec,key in [("BA","schools"),("MA","master"),("junior","junior")]:
    sch = kb[key]["schools"] if "schools" in kb[key] else kb[key]
    missing[sec] = {norm(n) for n,v in sch.items() if not v.get("lang_bypass")}
print("미보유:", {k:len(v) for k,v in missing.items()})

# broad patterns
PATS = {
 "selftest": r"(자체|본교|본원|교내)[^\n]{0,15}(한국어|어학)[^\n]{0,15}(시험|평가|교육과정|연수)|한국어\s*능력\s*시험[^\n]{0,15}(합격|취득)|HC-TOPIK|자체\s*TOPIK",
 "recommend": r"추천",
 "sejong": r"세종학당|SKA",
 "kiip": r"KIIP|사회통합|사전평가",
 "langcourse": r"(한국어|어학)[^\n]{0,10}(교육원|학당|연수|과정)[^\n]{0,20}(수료|이수)|어학당",
 "eng": r"영어|IELTS|TOEFL|TOEIC|TEPS|영어트랙|영어강의",
 "waiver": r"면제|대체|완화|별도\s*기준|예외|인정",
 "interview": r"면접|구술",
}
KEYLINE = r"(지원자격|응시자격|어학|언어|자격|요건|전형)"

out = {}
for level, folders in FOLDERS.items():
    miss = missing[level]
    for fd in folders:
        if not os.path.isdir(fd): continue
        for fn in sorted(os.listdir(fd)):
            if not fn.lower().endswith(".pdf"): continue
            school = re.sub(r"^0000\d+_","",fn)
            school = re.sub(r"_(대학원_)?모집요강.*|\.pdf$|_한국어교육원.*|_외국인.*|_전문학사.*|_\d{4}.*","",school)
            school = re.sub(r"\[.*?\]|\((글로컬|세종|미래)\)","",school).strip()
            if norm(school) not in miss: continue
            try:
                doc = pymupdf.open(os.path.join(fd,fn))
                full = "\n".join(p.get_text() for p in doc); doc.close()
            except Exception: continue
            if len(full) < 200: continue
            found = {}
            for k,p in PATS.items():
                hits=[m.group(0) for m in re.finditer(r"[^\n]{0,70}(?:"+p+r")[^\n]{0,90}", full)]
                if hits:
                    seen=[]
                    for h in hits:
                        h=re.sub(r"\s+"," ",h).strip()
                        if h not in seen: seen.append(h)
                    found[k]=seen[:4]
            if found:
                out[f"{level}:{school}"] = {"school":school,"level":level,"file":fn,"paths":found}

json.dump(out, open(r"C:\Users\wisew\camnemi-crm\backend\_bypass_missing_raw.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"재추출(미보유): {len(out)}개")
from collections import Counter
c=Counter()
for v in out.values():
    for k in v["paths"]: c[k]+=1
print("유형:", dict(c))
