# -*- coding: utf-8 -*-
"""Point KB guide_pdf/guide_page_url to the newly-downloaded 2027 guides."""
import json, os

BASE = r"C:\Users\USER\camnemi-crm\backend"
UP = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project"
KB = os.path.join(BASE, "verified_kb.json")
STATE = os.path.join(BASE, "_guide_2027_detected.json")

kb = json.load(open(KB, encoding="utf-8"))
state = json.load(open(STATE, encoding="utf-8"))

dl = {n: v for n, v in state.items() if v.get("downloaded") and v.get("saved")}
print(f"다운로드된 2027: {len(dl)}")

def find_section(school, level):
    sec_map = {"ba": ("schools", None), "ma": ("master", "schools"),
               "junior": ("junior", "schools"), "lang": ("lang_programs", "schools")}
    sec, sub = sec_map.get(level, ("schools", None))
    try:
        d = kb[sec][sub] if sub else kb[sec]
    except Exception:
        return None, None
    for k in d:
        if school in k or k in school:
            return sec, k
    return None, None

updated = 0
for n, v in dl.items():
    sec, key = find_section(n, v.get("level", "ba"))
    if not key:
        print(f"  {n}: KB 매칭 실패")
        continue
    if sec == "schools":
        d = kb["schools"][key]
    else:
        sub = {"master": "schools", "junior": "schools", "lang_programs": "schools"}[sec]
        d = kb[sec][sub][key]
    d["guide_pdf"] = v["saved"]
    if v.get("page_url"):
        d["guide_page_url"] = v["page_url"]
    d["guide_year"] = "2027"
    updated += 1
    print(f"  {n} -> {sec}/{key} guide_pdf=2027")

json.dump(kb, open(KB, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"KB 업데이트: {updated}교")
