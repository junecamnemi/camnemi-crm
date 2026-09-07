# -*- coding: utf-8 -*-
"""Scan the 16 foreigner-only junior college 요강 PDFs and extract structured facts:
전형일정(원서접수), TOPIK 요건, 학과(전문학사), 등록금, 통합여부, D-2/D-4."""
import os, re, json
import pymupdf

SAVEDIR = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project\adiga_2026_전문대학_모집요강"
OUT = r"C:\Users\USER\camnemi-crm\backend\_junior_foreign_scan.json"

def norm(t): return re.sub(r"[ \t]+"," ",t)

def extract_period(full):
    pats = [
        r"(?:원서접수|접수기간|원서접수기간|지원기간)[^\d]{0,30}((?:20\d\d)[.\-년]?\s*\d{1,2}[.\-월]?\s*\d{1,2}[.\-일]?\s*[~～\-]\s*(?:20\d\d)?[.\-년]?\s*\d{1,2}[.\-월]?\s*\d{1,2}[.\-일]?)",
        r"((?:20\d\d)[.\-년]?\s*\d{1,2}[.\-월]?\s*\d{1,2}[.\-일]?\s*[~～\-]\s*(?:20\d\d)[.\-년]?\s*\d{1,2}[.\-월]?\s*\d{1,2}[.\-일]?)",
    ]
    for p in pats:
        m = re.search(p, norm(full))
        if m:
            return re.sub(r"\s+","",m.group(1))
    return None

def extract_topik(full):
    n = norm(full)
    m = re.search(r"TOPIK\s*(\d+)급", n)
    if m: return f"TOPIK {m.group(1)}급 이상"
    if re.search(r"TOPIK|한국어능력시험", n):
        m2 = re.search(r"(TOPIK|한국어능력시험)[^,;.\n]{0,40}?(\d+)급", n)
        return m2.group(0) if m2 else "TOPIK 기준 (급수 확인)"
    return None

def extract_majors(full):
    n = norm(full)
    # look for 학과/학부 names in 모집학과 section
    majors=[]
    for m in re.finditer(r"([가-힣A-Za-z]{2,12}학과|〔?[가-힣]{2,10}과\]?|계열)", n):
        word=m.group(1)
        if "학과" in word and word not in majors:
            majors.append(word)
    # dedupe & filter noise
    seen=set(); clean=[]
    for m in majors:
        if m in seen: continue
        seen.add(m)
        clean.append(m)
    return clean[:20]

def extract_tuition(full):
    tt = full.replace(",","")
    amounts=[]
    for m in re.finditer(r"(등록금|수업료|학비)[^\d]{0,20}(\d{5,7})", norm(full)):
        amounts.append(int(m.group(2)))
    if not amounts:
        for m in re.finditer(r"(?<!\d)(\d{6,7})(?!\d)", tt):
            v=int(m.group(1))
            if 300000<=v<=2500000 and v not in amounts: amounts.append(v)
    amounts=sorted(set(amounts))
    return {"min":amounts[0],"max":amounts[-1]} if amounts else None

def detect_type(full):
    has_lang = bool(re.search(r"어학연수|D-4|한국어연수", norm(full)))
    has_adv = bool(re.search(r"전공심화|학사학위", norm(full)))
    if has_lang and has_adv: return "combined_lang_degree_adv"
    if has_lang: return "combined_lang_degree"
    if has_adv: return "degree_advanced"
    return "degree_only"

results={}
for fn in sorted(os.listdir(SAVEDIR)):
    if "_외국인모집요강" not in fn: continue
    school = fn.replace("_전문학사_외국인모집요강.pdf","")
    try:
        doc=pymupdf.open(os.path.join(SAVEDIR,fn))
        full="\n".join(p.get_text() for p in doc)
        npages=len(doc); doc.close()
    except Exception as e:
        results[school]={"error":str(e)}; continue
    results[school]={
        "file": fn, "pages": npages, "chars": len(full),
        "period": extract_period(full),
        "topik_req": extract_topik(full),
        "majors": extract_majors(full),
        "tuition": extract_tuition(full),
        "guide_type": detect_type(full),
    }

json.dump(results, open(OUT,"w",encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"분석 {len(results)}개")
for s,v in results.items():
    if "error" in v: print(f"  {s}: ERR {v['error']}")
    else: print(f"  {s}: {v['guide_type']} | 기간={v['period']} | TOPIK={v['topik_req']} | 학과{len(v['majors'])} | 등록금={v['tuition']}")
