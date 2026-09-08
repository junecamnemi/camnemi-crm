# -*- coding: utf-8 -*-
"""Re-scan lang-program PDFs for tuition (수강료) with stronger extraction, filling
gaps where tuition_range is missing in consulting_db."""
import os, re, json
import pymupdf

DIR = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project\adiga_2026_어학연수_모집요강"
KB = json.load(open(r"C:\Users\USER\camnemi-crm\backend\verified_kb.json", encoding="utf-8"))
lp = KB["lang_programs"]["schools"]

def norm(s): return re.sub(r"\[.*?\]","",s).replace("대학교","").replace("대학","").replace(" ","")

# schools missing tuition
need = []
have_norm = set()
for fn in os.listdir(DIR):
    if not fn.endswith(".pdf"): continue
    # map file to lang key
    base = fn.replace(".pdf","").replace("_한국어교육원","").replace("_한국어교육원_2026가을겨울","")
    # skip if already has tuition in KB
    for k,v in lp.items():
        if v.get("tuition_range"): have_norm.add(norm(k))

# find files for schools missing tuition
targets=[]
for fn in sorted(os.listdir(DIR)):
    if not fn.endswith(".pdf"): continue
    base = re.sub(r"_한국어교육원.*","",fn)
    # does any KB lang school (no tuition) match this file?
    for k,v in lp.items():
        if v.get("tuition_range"): continue
        if norm(k) and (norm(k) in norm(base) or norm(base) in norm(k)):
            targets.append((k, os.path.join(DIR,fn)))
            break
# dedupe
seen=set(); targets2=[]
for k,f in targets:
    if k in seen: continue
    seen.add(k); targets2.append((k,f))
print(f"수업료 미확보 어학 학교: {len(targets2)}")

def find_tuition(full):
    n = re.sub(r"[ \t]+"," ",full)
    tt = n.replace(",","")
    amounts=[]
    # 수강료/등록금/학비 following amount
    for m in re.finditer(r"(?:수강료|등록금|교육비|학비|학기당|1학기당)[^\d]{0,15}(\d{1,2}[,，]?\d{3}(?:,\d{3})?|\d{6,7})", tt):
        v=int(m.group(1).replace(",","").replace("，",""))
        if 300000<=v<=3000000 and v not in amounts: amounts.append(v)
    if not amounts:
        # plain large numbers in tuition range
        for m in re.finditer(r"(?<!\d)(\d{6,7})(?!\d)", tt):
            v=int(m.group(1))
            if 400000<=v<=3000000 and v not in amounts: amounts.append(v)
    return sorted(amounts)

found={}
for k,f in targets2:
    try:
        doc=pymupdf.open(f)
        full="\n".join(p.get_text() for p in doc)
        doc.close()
    except: continue
    amts=find_tuition(full)
    if amts:
        found[k]={"min":amts[0],"max":amts[-1]}

json.dump(found, open(r"C:\Users\USER\camnemi-crm\backend\_lang_tuition_gap.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"수업료 추가 추출: {len(found)}개")
for k,v in list(found.items())[:20]: print(f"  {k}: {v}")
