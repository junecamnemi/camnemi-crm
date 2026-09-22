# -*- coding: utf-8 -*-
"""Fill verified lang guide_url from _lang_url_backfill.json — only confident hits."""
import json, os

BASE = r"C:\Users\USER\camnemi-crm\backend"
KB = os.path.join(BASE, "verified_kb.json")

# school -> (url, is_good). Only is_good entries get filled.
FILL = {
    "동아방송예술대학교": ("https://klec.dima.ac.kr/kr/", True),     # K-WAVE 한국어교육원
    "우송정보대학": ("https://www.wsi.ac.kr/page/index.jsp?code=organization0201w", True),  # 한국어교육센터
    "동원대학교": ("https://www.tw.ac.kr/contents/contents.do?ciIdx=387&menuId=1695", True),  # 국제교류원
    "동남보건대학교": ("https://ilec.dongnam.ac.kr/ilec/index.do", True),  # 국제교류센터
    "안양대": ("https://www.anyang.ac.kr/main/academic/international-exchange.do", True),  # 국제교류
    "신경주대": ("https://www.sgu.ac.kr/organization/international-affairs", True),  # 국제교류처
}

kb = json.load(open(KB, encoding="utf-8"))
L = kb["lang_programs"]["schools"]
filled = 0
for n, (url, good) in FILL.items():
    if n in L and good:
        if not (L[n].get("guide_url") and L[n]["guide_url"].startswith("http")):
            L[n]["guide_url"] = url
            filled += 1

json.dump(kb, open(KB, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"lang guide_url 추가 채움: {filled}")
total = sum(1 for v in L.values() if v.get("guide_url") and v["guide_url"].startswith("http"))
print(f"lang guide_url 총: {total}/{len(L)}")
