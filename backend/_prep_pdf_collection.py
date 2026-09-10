# -*- coding: utf-8 -*-
"""Build prioritized PDF-collection lists for schools lacking local 요강 PDFs.
Excludes 신학대/교육대/특수 (not consulting targets). Creates batch files per level."""
import os, re, json

BASE = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project"
content = open(r"C:\Users\USER\camnemi-crm\data.js",encoding="utf-8").read()
s=content.find("[");d=0
for i in range(s,len(content)):
    if content[i]=="[":d+=1
    elif content[i]=="]":
        d-=1
        if d==0: data=json.loads(content[s:i+1]);break

def norm(s):
    s = re.sub(r"\[.*?\]","",s)
    s = s.replace("대학교","").replace("전문대학","").replace("전문대","")
    while s.endswith(("대학","대")) and len(s)>1:
        s = s[:-1] if s.endswith("대") else s[:-2]
    return s.replace(" ","")

# excluded: 신학/교육/특수
EXCLUDE_KW = ["신학","교육대","교원대","총신","감리교신학","침례신학","장신대","기독","성결","루터대","성서",
              "가톨릭꽃동네","중앙승가","승가","화성의과학","차의과학","한국기술교육"]
def excluded(n):
    return any(k in n for k in EXCLUDE_KW)

def collect(folders):
    names=set()
    for fd in folders:
        if os.path.isdir(fd):
            for fn in os.listdir(fd):
                if fn.lower().endswith((".pdf",".hwpx",".hwp")):
                    names.add(norm(re.sub(r"^0000\d+_","",fn)))
    return names

ba_pdf = collect([os.path.join(BASE,"adiga_2027_외국인_모집요강","외국인"),
                  os.path.join(BASE,"adiga_2026_외국인_모집요강","외국인")])
ma_pdf = collect([os.path.join(BASE,"adiga_2026_대학원_모집요강")])
jr_pdf = collect([os.path.join(BASE,"adiga_2026_전문대학_모집요강")])
lang_pdf = collect([os.path.join(BASE,"adiga_2026_어학연수_모집요강")])

ba_schools = sorted(set(u.get("n") for u in data if u.get("type")=="univ"))
jr_schools = sorted(set(u.get("n") for u in data if u.get("type")=="junior"))

def missing(schools, pdfset, excl_filter=True):
    out=[]
    for n in schools:
        if excl_filter and excluded(n): continue
        sn=norm(n)
        if not any(sn in p or p in sn for p in pdfset):
            out.append(n)
    return out

BA_need = missing(ba_schools, ba_pdf)
MA_need = missing(ba_schools, ma_pdf)   # all 4-yr without grad PDF
JR_need = missing(jr_schools, jr_pdf)
LANG_need = missing(ba_schools, lang_pdf)

print(f"BA 수집 필요: {len(BA_need)}")
print(f"MA 수집 필요: {len(MA_need)}")
print(f"전문학사 수집 필요: {len(JR_need)}")
print(f"어학연수 수집 필요: {len(LANG_need)}")

# save lists
for nm, lst in [("BA",BA_need),("MA",MA_need),("JR",JR_need),("LANG",LANG_need)]:
    json.dump(lst, open(rf"C:\Users\USER\camnemi-crm\backend\_collect_{nm}.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)

print("\nBA:", ", ".join(BA_need))
print("\n전문학사:", ", ".join(JR_need))
print("\nMA(첫 60):", ", ".join(MA_need[:60]))
