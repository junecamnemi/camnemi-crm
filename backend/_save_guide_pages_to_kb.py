# -*- coding: utf-8 -*-
"""Save discovered 모집요강 page URLs into verified_kb as guide_page_url.
Sources: _guide_pages.json (BA/MA/lang/junior), _junior_guide_pages.json,
_lang_guide_pages.json. Only page_found entries with a real http page_url."""
import json, os

BASE = r"C:\Users\USER\camnemi-crm\backend"
KB = os.path.join(BASE, "verified_kb.json")

kb = json.load(open(KB, encoding="utf-8"))

# collect page_url per school (level -> section path)
def collect(path):
    d = json.load(open(os.path.join(BASE, path), encoding="utf-8"))
    out = {}
    for n, v in d.items():
        if v.get("status") == "page_found" and v.get("page_url", "").startswith("http"):
            out[n] = v["page_url"]
    return out

pages = collect("_guide_pages.json")          # ba/ma/lang/junior (level field)
pages.update(collect("_junior_guide_pages.json"))  # junior
pages.update(collect("_lang_guide_pages.json"))    # lang

# section map: school key -> (kb_section, subkey)
def set_guide_page(school, url):
    # try each section
    for sec, sub in [("schools", None), ("master", "schools"),
                     ("junior", "schools"), ("lang_programs", "schools")]:
        try:
            d = kb[sec][sub] if sub else kb[sec]
        except Exception:
            continue
        # match exact or short
        for key in (school, school.replace("대학교", ""), school.replace("대학", "")):
            if key in d:
                d[key]["guide_page_url"] = url
                return True
    return False

filled = 0
unmatched = []
for n, url in pages.items():
    if set_guide_page(n, url):
        filled += 1
    else:
        unmatched.append(n)

json.dump(kb, open(KB, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"guide_page_url 저장: {filled}교")
print(f"매칭 실패: {len(unmatched)}")
for n in unmatched[:20]:
    print("  ", n)
