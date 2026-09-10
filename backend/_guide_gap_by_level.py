# -*- coding: utf-8 -*-
"""Identify schools with NO foreigner admission guide (모집요강) per level.
Levels: BA(학사 2026+2027), MA(석사), 전문학사(junior), 어학연수(lang).
Cross-references local guide PDF folders + verified_kb against the master school list."""
import os, re, json, glob

BASE = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project"
KB = json.load(open(r"C:\Users\USER\camnemi-crm\backend\verified_kb.json", encoding="utf-8"))

# local guide folders per level
FOLDERS = {
    "BA": [os.path.join(BASE,"adiga_2027_외국인_모집요강","외국인"),
           os.path.join(BASE,"adiga_2026_외국인_모집요강","외국인")],
    "MA": [os.path.join(BASE,"adiga_2026_대학원_모집요강")],
    "junior": [os.path.join(BASE,"adiga_2026_전문대학_모집요강")],
    "lang": [os.path.join(BASE,"adiga_2026_어학연수_모집요강")],
}

def norm(s):
    s = re.sub(r"\[.*?\]","",s)
    s = re.sub(r"\((글로컬|세종|미래|ERICA)\)","",s)
    s = s.replace("대학교","").replace("전문대학","").replace("전문대","")
    while s.endswith(("대학","대")) and len(s)>1:
        s = s[:-1] if s.endswith("대") else s[:-2]
    return s.replace(" ","")

def collect_pdf_names(folders):
    names=set()
    for fd in folders:
        if not os.path.isdir(fd): continue
        for fn in os.listdir(fd):
            if not fn.lower().endswith((".pdf",".hwpx",".hwp")): continue
            nm = re.sub(r"^0000\d+_","",fn)
            nm = norm(nm)
            names.add(nm)
    return names

def has_pdf(school, names):
    sn = norm(school)
    # check partial containment carefully
    return any(sn and (sn in p or p in sn) for p in names)

# school universe: all schools that appear anywhere in KB (BA+MA+junior as degree schools)
# Master list of degree-granting schools (4-yr + junior) from data.js
content = open(r"C:\Users\USER\camnemi-crm\data.js",encoding="utf-8").read()
s=content.find("[");d=0
for i in range(s,len(content)):
    if content[i]=="[":d+=1
    elif content[i]=="]":
        d-=1
        if d==0: data=json.loads(content[s:i+1]);break

# BA list (4-yr) — from data.js univ type
ba_schools = sorted(set(u.get("n") for u in data if u.get("type")=="univ"))
# junior list
jr_schools = sorted(set(u.get("n") for u in data if u.get("type")=="junior"))

def report(schools, level, folders):
    names = collect_pdf_names(folders)
    missing=[]
    for s in schools:
        if not has_pdf(s, names):
            missing.append(s)
    print(f"\n=== {level} 요강 없는 학교: {len(missing)}개 ===")
    print("  ", ", ".join(missing))
    return missing

print(f"BA 4년제 학교 수: {len(ba_schools)}")
print(f"전문대 학교 수: {len(jr_schools)}")
print(f"BA PDF폴더 수: {len(collect_pdf_names(FOLDERS['BA']))}")
print(f"MA PDF 수: {len(collect_pdf_names(FOLDERS['MA']))}")
print(f"junior PDF 수: {len(collect_pdf_names(FOLDERS['junior']))}")
print(f"lang PDF 수: {len(collect_pdf_names(FOLDERS['lang']))}")

ba_miss = report(ba_schools, "BA", FOLDERS["BA"])
# MA: for the BA (4-yr) schools
report(ba_schools, "MA", FOLDERS["MA"])
report(jr_schools, "전문학사", FOLDERS["junior"])
# lang: degree schools (BA+jr) that lack a language-program guide
lang_schools = ba_schools  # 4-yr primarily run language centers
report(ba_schools, "어학연수", FOLDERS["lang"])
