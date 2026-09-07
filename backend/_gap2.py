# -*- coding: utf-8 -*-
"""Full gap analysis per level. Count schools in KB lacking a local PDF."""
import json, os, re

BASE = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project"
KB = json.load(open(r"C:\Users\USER\camnemi-crm\backend\verified_kb.json", encoding="utf-8"))

def norm_folder(folder):
    """set of normalized school tokens present as PDFs in folder"""
    names = set()
    if not os.path.isdir(folder): return names
    for fn in os.listdir(folder):
        if not fn.endswith(".pdf"): continue
        nm = re.sub(r"^0000\d+_","",fn)
        nm = re.sub(r"\[.*?\]","",nm)
        nm = re.sub(r"_(20\d\d|2026|2027).*","",nm)
        nm = re.sub(r"_(외국인|한국어교육원|대학원|모집요강|어학연수|한국어과정|한국어학당|재외국민|정규|국제).*","",nm)
        nm = re.sub(r"_(국문|영문|최종|1차|2차|수시|정시|편입|추가|하계|동계).*","",nm)
        nm = re.sub(r"(대학교|대학원|대학)$","",nm)
        names.add(nm.replace("_","").strip())
    return names

def match(school, folder_names):
    s = re.sub(r"\[.*?\]","",school).replace("대학교","").replace("대학","").replace(" ","")
    return any(s in p or p in s or s==p for p in folder_names)

ba_pdf = norm_folder(os.path.join(BASE,"adiga_2027_외국인_모집요강","외국인")) | norm_folder(os.path.join(BASE,"adiga_2026_외국인_모집요강","외국인"))
ma_pdf = norm_folder(os.path.join(BASE,"adiga_2026_대학원_모집요강"))
lang_pdf = norm_folder(os.path.join(BASE,"adiga_2026_어학연수_모집요강"))

# --- BA ---
ba_schools = KB["schools"]
ba_need = [s for s in ba_schools if not match(s, ba_pdf)]
print(f"[학사 BA] KB {len(ba_schools)} | PDF없음 {len(ba_need)}")
print("  ", sorted(ba_need)[:80])

# --- MA ---
ma_schools = KB["master"]["schools"]
ma_need = [s for s in ma_schools if not match(s, ma_pdf)]
print(f"\n[석사 MA] KB {len(ma_schools)} | PDF없음 {len(ma_need)}")
print("  ", sorted(ma_need)[:80])

# --- junior (전문학사) ---
j_schools = KB["junior"]["schools"]
# junior pdfs live where? check lang_guides + junior_guides + any adiga junior
junior_pdf_dir = os.path.join(BASE, "adiga_2026_어학연수_모집요강")  # may contain junior 어학
# Actually junior college degree guides — check if any dedicated folder
print(f"\n[전문학사 junior] KB {len(j_schools)}")
# Find junior guide PDFs across all adiga folders
junior_hits = 0
junior_with = []
for d in [os.path.join(BASE,x) for x in os.listdir(BASE) if os.path.isdir(os.path.join(BASE,x))]:
    pass
print("(junior 전용 학사요강 폴더 존재 여부는 별도 확인 필요)")

# --- lang ---
lang_schools = KB["lang_programs"]["schools"] if "lang_programs" in KB else {}
lang_need = [s for s in lang_schools if not match(s, lang_pdf)]
print(f"\n[어학 lang] KB {len(lang_schools)} | PDF없음 {len(lang_need)}")
print("  ", sorted(lang_need))
