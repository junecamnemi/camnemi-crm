# -*- coding: utf-8 -*-
"""Scan the newly-collected MA (대학원) 요강 PDFs (66 schools not yet in KB master)
and extract: majors, lang_req(TOPIK/IELTS/TOEFL), period, tuition."""
import os, re, json
import pymupdf

BASE = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project\adiga_2026_대학원_모집요강"
KB = json.load(open(r"C:\Users\USER\camnemi-crm\backend\verified_kb.json", encoding="utf-8"))
ma_existing = list(KB["master"]["schools"].keys())

def norm(s):
    s=re.sub(r"\[.*?\]","",s)
    s=s.replace("대학교","").replace("대학원","").replace("대학","").replace(" ","")
    while s.endswith(("대학","대")) and len(s)>1: s=s[:-1]
    return s.replace(" ","")

# target files: grad PDFs whose school not in MA KB
targets=[]
for fn in os.listdir(BASE):
    if not fn.endswith(".pdf"): continue
    base=fn.replace("_대학원_모집요강.pdf","")
    # skip 가톨릭대/국민대 multi-file (already in KB as 가톨릭대학교/국민대학교? check)
    sn=norm(base)
    if not any(sn in norm(e) or norm(e) in sn for e in ma_existing):
        targets.append(fn)
print(f"KB에 없는 MA 요강: {len(targets)}")

def extract_lang(full):
    n=re.sub(r"[ \t]+"," ",full)
    parts=[]
    m=re.search(r"(TOPIK[^\n]{0,60})", n)
    if m: parts.append(m.group(1).strip()[:70])
    m=re.search(r"(IELTS[^\n]{0,40})", n)
    if m: parts.append(m.group(1).strip()[:50])
    m=re.search(r"(TOEFL[^\n]{0,40})", n)
    if m: parts.append(m.group(1).strip()[:50])
    return " | ".join(dict.fromkeys(parts))[:300] or None

def extract_period(full):
    n=re.sub(r"[ \t]+"," ",full)
    m=re.search(r"(?:원서접수|접수기간|모집기간)[^\d]{0,15}((?:20\d\d)[.\-년]?\s*\d{1,2}[.\-월]?\s*\d{1,2}[.\-일]?\s*[~～\-]\s*(?:20\d\d)?[.\-년]?\s*\d{1,2}[.\-월]?\s*\d{1,2}[.\-일]?)", n)
    return re.sub(r"\s+","",m.group(1)) if m else None

def extract_majors(full, limit=8):
    # grad depts usually 석사과정/모집단위 lists
    n=re.sub(r"[ \t]+"," ",full)
    majors=[]
    for m in re.finditer(r"([가-힣A-Za-z]{2,15}(?:학과|학부|전공|과))", n):
        w=m.group(1)
        if "학과" in w or "전공" in w and w not in majors:
            majors.append(w)
    # dedupe
    seen=set(); out=[]
    for m in majors:
        if m not in seen: seen.add(m); out.append(m)
    return out[:limit]

def extract_tuition(full):
    tt=full.replace(",","")
    amts=[]
    for m in re.finditer(r"(?<!\d)(\d{6,7})(?!\d)", tt):
        v=int(m.group(1))
        if 2000000<=v<=15000000 and v not in amts: amts.append(v)
    return {"min":min(amts),"max":max(amts)} if amts else None

results={}
for fn in targets:
    try:
        doc=pymupdf.open(os.path.join(BASE,fn))
        full="\n".join(p.get_text() for p in doc)
        doc.close()
    except Exception as e:
        results[fn]={"error":str(e)}; continue
    school=fn.replace("_대학원_모집요강.pdf","")
    results[school]={
        "file":fn,
        "lang":extract_lang(full),
        "period":extract_period(full),
        "majors":extract_majors(full),
        "tuition":extract_tuition(full),
        "has_foreigner": bool(re.search(r"외국인|순수외국인|유학생|foreign", full, re.I)),
    }

json.dump(results, open(r"C:\Users\USER\camnemi-crm\backend\_ma_new_scan.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
n_foreign=sum(1 for v in results.values() if v.get("has_foreigner"))
n_lang=sum(1 for v in results.values() if v.get("lang"))
print(f"스캔 {len(results)}개 | 외국인언급 {n_foreign} | 언어요건 {n_lang}")
for s,v in list(results.items())[:6]:
    if "error" not in v: print(f"  {s}: 외국인={v['has_foreigner']} 언어={str(v['lang'])[:40]} 기간={v['period']}")
