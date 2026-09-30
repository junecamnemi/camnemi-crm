#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Safely sync lang_guide URLs into data.js for session D-4 language schools.
ONLY fills lang_guide where currently empty. Backs up data.js first.
PRESERVES window.UNIV_GUIDES and window.UNIV_SPECIAL verbatim; rewrites
UNIV_KNOWLEDGE. Refuses to write unless all three globals survive and the
result passes `node --check` (see _datajs_safe.py).
"""
import json, os, shutil, datetime, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _datajs_safe import parse_globals, render, write_safe

DATA = r"C:\Users\wisew\camnemi-crm\data.js"
bak = DATA.replace(".js", f"_bak_{datetime.date.today().isoformat()}.js")
shutil.copy(DATA, bak)
print("백업:", bak)

# string-aware parse; raises if UNIV_KNOWLEDGE / UNIV_GUIDES / UNIV_SPECIAL is missing
_gl = parse_globals(DATA)
arr = _gl["knowledge"]
print("UNIV_KNOWLEDGE 레코드:", len(arr), "| UNIV_GUIDES 키:", len(_gl["guides"]),
      "| UNIV_SPECIAL 키:", len(_gl["special"]))

dn = {u.get("n"): u for u in arr}

# lang_guide URLs (official language center) verified this session
lang_urls = {
  "인천대학교": "https://korean.inu.ac.kr/inukli/6853/subview.do",
  "인하대학교": "https://www.inha.ac.kr/kr/index.do",  # 어학당 is via oia; best official portal
  "경인여자대학교": "https://www.kiwu.ac.kr/ko/cms/FR_CON/index.do?MENU_ID=640",
  "가톨릭대학교": "https://kli.catholic.ac.kr/kli/index.do",
  "서울여자대학교": "https://klc.swu.ac.kr/skin/page/info01.html",
  "덕성여자대학교": "https://dilc.ds.ac.kr/kor/kor03.php",
  "동의대학교": "https://deuhome.deu.ac.kr/language/index.do",
  "이화여자대학교": "https://elc.ewha.ac.kr/elc/main.do",
  "서강대학교": "https://klec.sogang.ac.kr/?url=/dep_03/3110.php",
  "연세대학교": "https://www.yskli.com/",
  "국민대학교": "https://kli.kookmin.ac.kr/",
  "삼육대학교": "https://global.sahmyook.ac.kr/",
  "서일대학교": "https://www.seoil.ac.kr/global/751/subview.do",
}

filled = 0; already = []
for name, url in lang_urls.items():
    u = dn.get(name)
    if not u:
        print(f"  ⚠ {name}: data.js 레코드 없음")
        continue
    cur = u.get("lang_guide")
    if cur:
        already.append(name)
        continue
    u["lang_guide"] = url
    filled += 1

new_content = render(_gl["prefix"], arr, _gl["guides"], _gl["special"], knowledge_indent=1)
have = write_safe(DATA, new_content,
                  expect={"UNIV_KNOWLEDGE": len(arr),
                          "UNIV_GUIDES": len(_gl["guides"]),
                          "UNIV_SPECIAL": len(_gl["special"])})

print(f"\nlang_guide 채움: {filled}개 | 이미 있던(스킵): {len(already)}: {already}")
print("레코드 수:", have)
print(f"파일 크기: 원본 {os.path.getsize(bak)//1024}KB → 새 {os.path.getsize(DATA)//1024}KB")
print("저장 완료:", DATA)
