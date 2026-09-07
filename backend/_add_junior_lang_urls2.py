#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Add more junior-college language-school URLs (batch 2) to verified_kb.json."""
import json, os

BASE = r"C:\Users\USER\camnemi-crm\backend"
KB = os.path.join(BASE, "verified_kb.json")

MORE_URLS = {
    "우송정보대학": "https://wsckli.wsi.ac.kr/",
    "충청대학교": "https://www.ok.ac.kr/www/contents.do?key=5695",
    "동아방송예술대학교": "https://klec.dima.ac.kr/kr/admission/admission.php",
    "동원대학교": "https://www.tw.ac.kr/contents/contents.do?ciIdx=826&menuId=2474",
}

with open(KB, encoding="utf-8") as f:
    kb = json.load(f)

junior = kb.get("junior", {}).get("schools", {})
added = 0
for name, url in MORE_URLS.items():
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
        print(f"  ✗ {name} (목록에 없음)")

kb["junior"]["schools"] = junior
with open(KB, "w", encoding="utf-8") as f:
    json.dump(kb, f, ensure_ascii=False, indent=2)
print(f"\n{added}개 추가 완료")

# count total junior with lang_src
n = sum(1 for s in junior.values() if s.get("lang_src"))
print(f"전문대학 언어학교 URL 보유: {n}개 / {len(junior)}개")
