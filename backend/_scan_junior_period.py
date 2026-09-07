# -*- coding: utf-8 -*-
"""Scan junior college 요강 PDFs (degree + foreigner) for application period (원서접수)."""
import os, re, json
import pymupdf

DIR = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project\adiga_2026_전문대학_모집요강"
OUT = r"C:\Users\USER\camnemi-crm\backend\_junior_period_scan.json"

def norm(t): return re.sub(r"[ \t]+"," ",t)

def extract_period(full):
    n = norm(full)
    # patterns: 원서접수/접수기간/지원기간 followed by date range
    pats = [
        r"(?:원서접수|접수기간|원서접수기간|지원기간|모집기간|접수)[^\d]{0,30}?((?:20\d\d)[.\-년]?\s*\d{1,2}[.\-월]?\s*\d{1,2}[.\-일]?\s*[~～\-]\s*(?:20\d\d)?[.\-년]?\s*\d{1,2}[.\-월]?\s*\d{1,2}[.\-일]?)",
        r"((?:20\d\d)[.\-년]?\s*\d{1,2}[.\-월]?\s*\d{1,2}[.\-일]?\s*[~～\-]\s*(?:20\d\d)[.\-년]?\s*\d{1,2}[.\-월]?\s*\d{1,2}[.\-일]?)",
        r"((?:20\d\d)[.\-년]?\s*\d{1,2}[.\-월]?\s*\d{1,2}[.\-일]?\s*~)",  # open-ended (서류마감 후)
    ]
    for p in pats:
        m = re.search(p, n)
        if m:
            return re.sub(r"\s+","",m.group(1))
    return None

results={}
for fn in sorted(os.listdir(DIR)):
    if not fn.endswith(".pdf"): continue
    school = fn.replace(".pdf","")
    school = re.sub(r"_전문학사_(모집요강|입학안내\(렌더\)|외국인모집요강|입학안내)|_전문학사학위심화_모집요강","",school)
    try:
        doc=pymupdf.open(os.path.join(DIR,fn))
        full="\n".join(p.get_text() for p in doc)
        doc.close()
    except: continue
    p = extract_period(full)
    if p:
        results[school]=p

json.dump(results, open(OUT,"w",encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"전문학사 지원시기 추출: {len(results)}개")
for k,v in list(results.items())[:20]: print(f"  {k}: {v}")
