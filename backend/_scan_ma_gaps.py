# -*- coding: utf-8 -*-
"""Scan MA (대학원) 요강 PDFs for foreigner admission: TOPIK/IELTS req, tuition,
scholarship, application period. Fill MA gaps in the consulting DB."""
import os, re, json
import pymupdf

DIR = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project\adiga_2026_대학원_모집요강"
OUT = r"C:\Users\USER\camnemi-crm\backend\_ma_scan_lang.json"

def norm(t): return re.sub(r"[ \t]+"," ",t)

def extract_topik(full):
    n = norm(full)
    m = re.search(r"(?:TOPIK|한국어능력시험)[^\d\n]{0,30}?(\d+)급", n)
    return f"TOPIK {m.group(1)}급" if m else (f"TOPIK {m.group(1)}급" if (m:=re.search(r"TOPIK\s*(\d+)",n)) else None)

def extract_ielts(full):
    n = norm(full)
    m = re.search(r"IELTS[^\d\n]{0,10}?(\d+(?:\.\d+)?)", n)
    return f"IELTS {m.group(1)}" if m else None

def extract_toefl(full):
    n = norm(full)
    m = re.search(r"TOEFL[^\d\n]{0,10}?(\d+)", n)
    return f"TOEFL {m.group(1)}" if m else None

def extract_tuition(full):
    tt = full.replace(",","")
    nums=[]
    for m in re.finditer(r"(?<!\d)(\d{6,7})(?!\d)", tt):
        v=int(m.group(1))
        if 1000000<=v<=20000000: nums.append(v)
    nums=sorted(set(nums))
    return {"min":nums[0],"max":nums[-1]} if nums else None

def extract_period(full):
    n = norm(full)
    m = re.search(r"(?:원서접수|접수기간|모집기간)[^\d]{0,20}((?:20\d\d)[.\-년]?\s*\d{1,2}[.\-월]?\s*\d{1,2}[.\-일]?\s*[~～\-]\s*(?:20\d\d)?[.\-년]?\s*\d{1,2}[.\-월]?\s*\d{1,2}[.\-일]?)", n)
    return re.sub(r"\s+","",m.group(1)) if m else None

def extract_scholarship(full):
    n = norm(full)
    sects = re.findall(r"(?:장학금|장학)[^.\n]{0,120}?(?:TOPIK|토픽|IELTS|등록금|수업료)[^.\n]{0,60}", n)
    return sects[:6] if sects else None

results={}
for fn in sorted(os.listdir(DIR)):
    if not fn.endswith(".pdf"): continue
    school = fn.replace("_대학원_모집요강.pdf","").replace("_일반대학원.pdf","").replace("_2026후기1차_","").replace("_외국인전형_","")
    try:
        doc=pymupdf.open(os.path.join(DIR,fn))
        full="\n".join(p.get_text() for p in doc)
        doc.close()
    except: continue
    results[school]={
        "file": fn,
        "topik": extract_topik(full),
        "ielts": extract_ielts(full),
        "toefl": extract_toefl(full),
        "tuition": extract_tuition(full),
        "period": extract_period(full),
        "scholarship": extract_scholarship(full),
    }

json.dump(results, open(OUT,"w",encoding="utf-8"), ensure_ascii=False, indent=1)
n_topik=sum(1 for v in results.values() if v.get("topik"))
n_ielts=sum(1 for v in results.values() if v.get("ielts"))
n_tuit=sum(1 for v in results.values() if v.get("tuition"))
n_period=sum(1 for v in results.values() if v.get("period"))
n_sch=sum(1 for v in results.values() if v.get("scholarship"))
print(f"MA 스캔 {len(results)}개 | TOPIK {n_topik} | IELTS {n_ielts} | 수업료 {n_tuit} | 기간 {n_period} | 장학 {n_sch}")
