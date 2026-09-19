#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""crawl_junior_lang3.py — 전문대 국제교류처(global/oia/intl) 페이지에서 어학원 링크 추출.

각 전문대의 국제교류처 하위도메인을 시도하고, 그 페이지에서 어학원(한국어교육원) 링크 추출.
출력: backend/_junior_lang3_crawl.json
"""
import requests, re, json, os, time
from urllib.parse import urljoin
requests.packages.urllib3.disable_warnings()
B = os.path.dirname(os.path.abspath(__file__))
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0) Chrome/124.0", "Accept-Language": "ko-KR,ko;q=0.9"}

idx = json.load(open(os.path.join(B, "unvcd_index.json"), encoding="utf-8"))["schools"]
jr = [v for v in idx.values() if v["school_type"]=="junior" and not v.get("excluded")]
no = [v for v in jr if not v.get("foreign_links",{}).get("lang_foreign")]
print(f"어학원 미보유: {len(no)}")

# 국제교류처 하위도메인 후보
SUBS = ["global", "oia", "intl", "international", "inter", "foreign", "kli", "klec", "ili", "klc"]

def get_domain(home):
    m = re.match(r"https?://([^/]+)", home or "")
    return m.group(1) if m else ""

LKEY = ["한국어", "어학", "language", "korean", "klec", "kli", "어학당", "한국어교육", "한국어센터", "연수", "어학원", "한국어학당"]

def crawl(url):
    try:
        r = requests.get(url, headers=H, verify=False, timeout=10)
        html = r.text
    except: return []
    links = re.findall(r'href=[\'"]([^\'"]+)[\'"][^>]*>([^<]{2,60})</a>', html, re.I)
    found = []
    for href, text in links:
        if not href or href.startswith(("javascript","#","mailto","tel")): continue
        full = urljoin(url, href)
        if "adiga" in full or "uway" in full or "jinhak" in full: continue
        low = (full + " " + text).lower()
        if any(k in low for k in LKEY):
            found.append({"url": full, "text": text.strip()[:40]})
    seen=set(); uniq=[]
    for f in found:
        if f["url"] in seen: continue
        seen.add(f["url"]); uniq.append(f)
    return uniq

out = {}
for v in no:
    dom = get_domain(v.get("homepage"))
    if not dom: continue
    all_found = []
    # 국제교류처 하위도메인 시도
    for sub in SUBS:
        u = f"https://{sub}.{dom}/"
        found = crawl(u)
        if found:
            all_found.extend(found)
            break
    # 홈페이지도 시도
    if not all_found:
        all_found = crawl(v.get("homepage"))
    seen=set(); uniq=[]
    for f in all_found:
        if f["url"] in seen: continue
        seen.add(f["url"]); uniq.append(f)
    out[v["unvCd"]] = {"name": v["name"], "candidates": uniq}
    if uniq:
        print(f"{v['name']}: {len(uniq)}개 어학 링크")
    time.sleep(0.2)

json.dump(out, open(os.path.join(B, "_junior_lang3_crawl.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
withcand = [v for v in out.values() if v["candidates"]]
print(f"\n어학 링크 있는 교: {len(withcand)}")
print("저장: _junior_lang3_crawl.json")