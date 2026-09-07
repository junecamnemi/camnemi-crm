# -*- coding: utf-8 -*-
"""Gap analysis: which schools lack a local PDF for each program level.
Levels: junior(전문학사), ba(학사), ma(석사), lang(어학연수).
Cross-references verified_kb.json school lists vs local PDF folders."""
import json, os, glob, re

BASE = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project"
KB = json.load(open(r"C:\Users\USER\camnemi-crm\backend\verified_kb.json", encoding="utf-8"))

# ---- local PDF folders ----
FOLDERS = {
    "ba2027": os.path.join(BASE, "adiga_2027_외국인_모집요강", "외국인"),
    "ba2026": os.path.join(BASE, "adiga_2026_외국인_모집요강", "외국인"),
    "ma": os.path.join(BASE, "adiga_2026_대학원_모집요강"),
    "lang": os.path.join(BASE, "adiga_2026_어학연수_모집요강"),
    "junior_guides": r"C:\Users\USER\camnemi-crm\junior_guides",
}

def norm_pdf_names(folder):
    names = set()
    if not os.path.isdir(folder):
        return names
    for fn in os.listdir(folder):
        if not fn.endswith(".pdf"):
            continue
        nm = fn.replace(".pdf", "")
        # strip campus brackets, leading codes, year/track suffixes
        nm = re.sub(r"^0000\d+_", "", nm)
        nm = re.sub(r"\[.*?\]", "", nm)
        nm = re.sub(r"_(20\d\d|2026|2027).*", "", nm)
        nm = re.sub(r"_(외국인|한국어교육원|대학원|모집요강|어학연수|한국어과정|재외국민).*", "", nm)
        nm = re.sub(r"_(국문|영문|최종|1차|2차|수시|정시|편입).*", "", nm)
        nm = re.sub(r"(대학|대학교|대학원)$", "", nm)  # normalize suffix
        names.add(nm.replace("_", ""))
    return names

def norm_school(s):
    s = re.sub(r"\[.*?\]", "", s)
    s = re.sub(r"\((글로컬|세종|미래|ERICA)\)", "", s)
    return s.replace("대학교", "").replace("대학", "").replace(" ", "")

def has_local_pdf(school, folder):
    sn = norm_school(school)
    pn = norm_pdf_names(folder)
    return any(sn in p or p in sn or sn == p for p in pn)

# ---- KB school lists ----
junior_names = set(KB.get("junior", {}).get("schools", {}).keys()) if KB.get("junior") else set()
lang_names = set(KB.get("lang_programs", {}).get("schools", {}).keys()) if KB.get("lang_programs") else set()
# lang also includes those in language_school_urls.json
lang_urls = json.load(open(r"C:\Users\USER\camnemi-crm\backend\language_school_urls.json", encoding="utf-8"))
lang_all = set(x["school"] for x in lang_urls) | lang_names

report = {
    "junior(전문학사)": {"kb_count": len(junior_names)},
    "lang(어학연수)": {"kb_count": len(lang_all)},
}

# print summary of coverage
print("=== 어학연수 PDF 커버리지 ===")
lang_pdf = norm_pdf_names(FOLDERS["lang"])
lang_without = [s for s in sorted(lang_all) if not any(norm_school(s) in p or p in norm_school(s) for p in lang_pdf)]
print(f"lang_all {len(lang_all)} | 로컬 PDF {len(lang_pdf)} | PDF없음(코퍼스에 파일명 없음): {len(lang_without)}")
print("  ", lang_without[:50])

print("\n=== 전문학사(junior) — PDF/갭 ===")
print(f"junior KB {len(junior_names)}")
# junior guides on disk anywhere?

print("\n=== 어학 PDF 실제 개수 ===")
print("lang folder:", len(os.listdir(FOLDERS["lang"])) if os.path.isdir(FOLDERS["lang"]) else 0)
