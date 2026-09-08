# -*- coding: utf-8 -*-
"""Re-scan MA (대학원) 요강 PDFs for scholarships with stronger extraction.
Many have 장학 tables/paragraphs the first pass missed."""
import os, re, json
import pymupdf

DIR = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project\adiga_2026_대학원_모집요강"
OUT = r"C:\Users\USER\camnemi-crm\backend\_ma_scholarship_scan.json"

def norm(t): return re.sub(r"[ \t]+"," ",t)

def extract_scholarship(full):
    n = norm(full)
    sects = []
    # look for 장학 sections and capture surrounding text
    for m in re.finditer(r'(?:장학금|장학제도|입학장학금|외국인장학)[^\n]{0,300}', n):
        s = m.group(0).strip()
        if len(s) > 20 and s not in sects:
            sects.append(s)
    # TOPIK/IELTS based scholarship lines
    for m in re.finditer(r'(TOPIK\s*\d급[^\n]{0,80}?(?:등록금|수업료|전액|반액|%|\d{1,3})?[^\n]{0,60}|IELTS[^\n]{0,40}?%[^\n]{0,40}|등록금\s*전액|수업료\s*\d+%)', n):
        s = m.group(0).strip()
        if s not in sects:
            sects.append(s)
    return sects[:8] if sects else None

results={}
for fn in sorted(os.listdir(DIR)):
    if not fn.endswith(".pdf"): continue
    school = re.sub(r"_대학원_모집요강\.pdf|_일반대학원\.pdf|_2026후기1차_|_외국인전형_|\.pdf","",fn)
    try:
        doc=pymupdf.open(os.path.join(DIR,fn))
        full="\n".join(p.get_text() for p in doc)
        doc.close()
    except: continue
    sch = extract_scholarship(full)
    if sch:
        results[school]=sch

json.dump(results, open(OUT,"w",encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"MA 장학금 스캔: {len(results)}개 학교에서 추출")
# 샘플
for s,sch in list(results.items())[:8]:
    print(f"  {s}: {sch[0][:90]}...")
