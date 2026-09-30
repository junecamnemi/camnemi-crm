# -*- coding: utf-8 -*-
"""Extract language-requirement ALTERNATIVE/BYPASS paths from local 외국인 모집요강 PDFs.
Bypass paths = 자체시험, 국제처/총장 추천, 세종학당, KIIP/사회통합, 어학당 수료, 영어 면제, 면접 대체.
Keyword-context extraction → output JSON per school for later pro-model structuring."""
import os, re, json
import pymupdf

BASE = r"C:\Users\wisew\내 드라이브\02_Crawling_Sheet\University_Project"
FOLDERS = {
    "BA": [os.path.join(BASE,"adiga_2027_외국인_모집요강","외국인"),
           os.path.join(BASE,"adiga_2026_외국인_모집요강","외국인")],
    "MA": [os.path.join(BASE,"adiga_2026_대학원_모집요강")],
    "junior": [os.path.join(BASE,"adiga_2026_전문대학_모집요강")],
}
# bypass keyword patterns
PATTERNS = {
 "selftest": r"(자체\s*한국어\s*능력\s*시험|본교\s*한국어\s*능력\s*시험|자체\s*시험|본원\s*한국어\s*시험|본교\s*한국어\s*교육과정\s*\d급\s*수료|자체\s*평가|자체\s*출제)",
 "recommend_org": r"(협약|협정|자매)[^\n]{0,25}(기관|대학|고등교육기관|센터)[^\n]{0,15}추천|해외센터[^\n]{0,15}추천|협정기관\s*추천",
 "recommend_gov": r"(교육부\s*장관|정부초청|정부\s*초청|지자체|지방자치단체|외국정부)[^\n]{0,25}(추천|장학생|위탁생)|위탁생|교환학생|교류학생",
 "recommend_intl": r"(국제처|국제교류원?|국제협력과|국제교육원|총장|학부\(과\)장|지도교수|입학처)[^\n]{0,20}추천",
 "sejong": r"세종학당",
 "kiip": r"(KIIP|사회통합프로그램|사전평가)",
 "langcourse": r"(한국어교육원|한국어학당|어학당|언어교육원|한국어\s*정규과정)[^\n]{0,25}(수료|이수)",
 "eng_exempt": r"(영어권|영어를\s*모국어|모국어가\s*영어|영어\s*능력[^\n]{0,10}면제|영어로\s*수업|영어트랙|영어\s*모국어)",
 "interview": r"(면접[^\n]{0,15}대체|구술\s*시험|면접으로\s*대체|한국어\s*면접|전공\s*면접)",
 "dept_waiver": r"(외국인\s*전담학과|이중언어과정|전담학과|기준\s*완화|요건\s*완화|별도\s*기준)",
}

def norm(s):
    s = re.sub(r"\[.*?\]","",s).replace("대학교","").replace("대학원","").replace("대학","").replace(" ","")
    while s.endswith(("대학","대")) and len(s)>1:
        s = s[:-1] if s.endswith("대") else s[:-2]
    return s.replace(" ","")

out = {}
for level, folders in FOLDERS.items():
    for fd in folders:
        if not os.path.isdir(fd): continue
        for fn in sorted(os.listdir(fd)):
            if not fn.lower().endswith(".pdf"): continue
            fp = os.path.join(fd, fn)
            school = re.sub(r"^0000\d+_","", fn)
            school = re.sub(r"_(대학원_)?모집요강.*|\.pdf$|_한국어교육원.*|_외국인.*|_전문학사.*|_\d{4}.*", "", school)
            school = re.sub(r"\[.*?\]|\((글로컬|세종|미래)\)","",school).strip()
            try:
                doc = pymupdf.open(fp)
                full = "\n".join(p.get_text() for p in doc)
                doc.close()
            except Exception:
                continue
            if len(full) < 200: continue
            found = {}
            for k, pat in PATTERNS.items():
                hits = [m.group(0) for m in re.finditer(r"[^\n]{0,60}(?:"+pat+r")[^\n]{0,70}", full)]
                if hits:
                    # dedupe, keep 3
                    seen=[]
                    for h in hits:
                        h=re.sub(r"\s+"," ",h).strip()
                        if h not in seen: seen.append(h)
                    found[k] = seen[:3]
            if found:
                key = f"{level}:{school}"
                out[key] = {"school": school, "level": level, "file": fn, "paths": found}

json.dump(out, open(r"C:\Users\wisew\camnemi-crm\backend\_bypass_raw.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"추출 학교: {len(out)}")
from collections import Counter
c=Counter()
for v in out.values():
    for k in v["paths"]: c[k]+=1
print("경로별 학교 수:", dict(c))
