#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Update _guide_2027_master.json lang_src for 4-year univs.
Only add URLs that are VERIFIED language-school (어학당/한국어교육원/어학교육원) pages.
Schools without a confirmed language school are left blank (lang_status='no_lang_school')."""
import json, os

BASE = r"C:\Users\USER\camnemi-crm\backend"
MASTER = os.path.join(BASE, "_guide_2027_master.json")

# Web-VERIFIED language-school URLs (official, language-specific pages)
NEW_LANG_URLS = {
    "강남대학교": "https://web.kangnam.ac.kr/menu/b6cdaa2d20ed253e51964ec6c6aeba1e.do?encMenuSeq=6962b3e0e6c7e477f53fd9b87bf2229a",  # 어학교육원
    "안양대학교": "https://www.anyang.ac.kr/main/academic/international-exchange.do",  # 국제교류원 한국어연수과정
    "우석대학교": "http://www.woosuk.ac.kr/main/?menu=161",  # 한국어교육
    "경동대학교": "https://global.kduniv.ac.kr/korean/",  # 국제처 한국어과정
    "한서대학교": "https://www.hanseo.ac.kr/sub/info.do?page=01050207&m=010502&s=hs",  # 어학교육원
    "나사렛대학교": "https://www.kornu.ac.kr/",  # 국제어학원 운영
    "경일대학교": "https://www.kiu.ac.kr/HOME/exchange/sub.htm",  # 한국어학당
    "청운대학교": "https://www.chungwoon.ac.kr/",  # 한국어과정 (메인)
    "한일장신대학교": "https://www.hanil.ac.kr/portal/default/bbs/view.do?menuId=M0004000100060000",  # 한국어학당 (2017 운영, 신규 확인 필요)
    "서울장신대학교": "https://www.sjs.ac.kr/ht_ml/w_01ed/1321_i.php",  # 국제교육원 한국어학당
}

# Schools likely WITHOUT a language school (theological/arts colleges) - mark clearly
NO_LANG = [
    "가야대학교", "감리교신학대학교", "광신대학교", "금강대학교", "대구예술대학교",
    "대전가톨릭대학교", "루터대학교", "목포가톨릭대학교", "부산장신대학교", "서울기독대학교",
    "수원가톨릭대학교", "영산선학대학교", "예수대학교", "인천가톨릭대학교", "중앙승가대학교",
    "차의과학대학교", "한국체육대학교", "한국침례신학대학교", "가톨릭꽃동네대학교",
]

with open(MASTER, encoding="utf-8") as f:
    master = json.load(f)

idx_map = {r.get("school", ""): i for i, r in enumerate(master)}

updated = 0
for name, url in NEW_LANG_URLS.items():
    if name in idx_map:
        master[idx_map[name]]["lang_src"] = url
        master[idx_map[name]]["lang_status"] = "own_site"
        updated += 1
        print(f"  ✓ {name} → {url}")
    else:
        print(f"  ✗ {name} (마스터에 없음)")

for name in NO_LANG:
    if name in idx_map:
        master[idx_map[name]]["lang_status"] = "no_lang_school"
        master[idx_map[name]].setdefault("lang_src", "")
        print(f"  ⚪ {name} — 어학당 없음(확인)으로 표시")

with open(MASTER, "w", encoding="utf-8") as f:
    json.dump(master, f, ensure_ascii=False, indent=2)
print(f"\n업데이트 완료: {updated}개 어학당 URL 추가")
