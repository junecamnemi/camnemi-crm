#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Add language-school (어학당/한국어과정) URLs to the KB for junior colleges (전문대학).
Merges web-researched URLs into verified_kb.json junior section (lang_src field)."""
import json, os

BASE = r"C:\Users\USER\camnemi-crm\backend"
KB = os.path.join(BASE, "verified_kb.json")

# Junior-college language school URLs (web-researched, 2026)
JUNIOR_LANG_URLS = {
    "명지전문대학": "https://mjklec.mjc.ac.kr/",
    "동양미래대학교": "https://www.dongyang.ac.kr/dmu31003/5091/subview.do",
    "부천대학교": "https://dept.bc.ac.kr/itntn/corp/immigration-office001.do",
    "대림대학교": "https://dept.daelim.ac.kr/gli/index.do",
    "신구대학교": "http://ilc.shingu.ac.kr/kor/main.html",
    "김포대학교": "https://global.ukp.ac.kr/",
    "인덕대학교": "https://www.induk.ac.kr/global/cms/frCmnCon/index.do?MENU_ID=310",
    "용인예술과학대학교": "https://ate.ysc.ac.kr/global/CMS/Contents/Contents.do?mCode=MN033",
    "서정대학교": "https://seojeong.ac.kr/korLang/main.do",
    "동남보건대학교": "https://ilec.dongnam.ac.kr/",
    "숭의여자대학교": "https://www.sewu.ac.kr/inic/index.do",
    "경기과학기술대학교": "https://www.gtec.ac.kr/global",
    "삼육보건대학교": "https://global.shu.ac.kr/",
    "한양여자대학교": "https://www.hywoman.ac.kr/hyce/",
    "서일대학교": "https://www.seoil.ac.kr/",
    "배화여자대학교": "https://www.baewha.ac.kr/",
}

with open(KB, encoding="utf-8") as f:
    kb = json.load(f)

junior = kb.get("junior", {}).get("schools", {})
added = 0
for name, url in JUNIOR_LANG_URLS.items():
    # find in junior (exact or fuzzy)
    key = None
    if name in junior:
        key = name
    else:
        for k in junior:
            if name.replace("대학교", "").replace("대학", "")[:4] in k.replace("대학교", "").replace("대학", "")[:5] or k.replace("대학교", "").replace("대학", "")[:4] in name:
                key = k
                break
    if key:
        junior[key]["lang_src"] = url
        added += 1
        print(f"  ✓ {key} → {url}")
    else:
        print(f"  ✗ {name} (junior 목록에 없음)")

kb["junior"]["schools"] = junior
with open(KB, "w", encoding="utf-8") as f:
    json.dump(kb, f, ensure_ascii=False, indent=2)
print(f"\n{added}개 전문대학 언어학교 URL 추가 완료")
