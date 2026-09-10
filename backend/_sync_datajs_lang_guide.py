#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Safely sync lang_guide URLs into data.js for session D-4 language schools.
ONLY fills lang_guide where currently empty. Backs up data.js first.
Preserves UNIV_GUIDES and overall structure; rewrites UNIV_KNOWLEDGE minified."""
import json, os, shutil, datetime

DATA = r"C:\Users\USER\camnemi-crm\data.js"
bak = DATA.replace(".js", f"_bak_{datetime.date.today().isoformat()}.js")
shutil.copy(DATA, bak)
print("백업:", bak)

content = open(DATA, encoding="utf-8").read()

# --- locate UNIV_KNOWLEDGE array and UNIV_GUIDES start ---
start = content.find("["); depth = 0; end = None
for i in range(start, len(content)):
    if content[i] == "[": depth += 1
    elif content[i] == "]":
        depth -= 1
        if depth == 0: end = i; break
pre = content[:start]
arr = json.loads(content[start:end+1])
# UNIV_GUIDES is after "];\n\nwindow.UNIV_GUIDES = {"
guides_start = content.find("window.UNIV_GUIDES")
guides_body = content[guides_start:] if guides_start >= 0 else ""
print("UNIV_KNOWLEDGE 레코드:", len(arr), "| UNIV_GUIDES 존재:", guides_start >= 0)

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

# rebuild minified: preserve pre + UNIV_KNOWLEDGE + the separator to UNIV_GUIDES
sep = content[end+1:guides_start] if guides_start >= 0 else content[end+1:]
# ensure separator ends before guides; guides_body keeps original guides fully
new_content = pre + json.dumps(arr, ensure_ascii=False, separators=(",", ":")) + sep + guides_body
open(DATA, "w", encoding="utf-8").write(new_content)

# verify
v = open(DATA, encoding="utf-8").read()
import re
vstart=v.find("["); vd=0; vend=None
for i in range(vstart,len(v)):
    if v[i]=="[":vd+=1
    elif v[i]=="]":
        vd-=1
        if vd==0: vend=i; break
newarr=json.loads(v[vstart:vend+1])
print(f"\nlang_guide 채움: {filled}개 | 이미 있던(스킵): {len(already)}: {already}")
print(f"레코드 수: {len(arr)} → {len(newarr)}")
print(f"파일 크기: 원본 {os.path.getsize(bak)//1024}KB → 새 {os.path.getsize(DATA)//1024}KB")
print("저장 완료:", DATA)
