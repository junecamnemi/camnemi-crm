#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""crawl_foreign_links.py — 4년제 각 학교 입시홈페이지에서 외국인/국제 입시 링크 추출.

정적(requests) 우선, JS사이트는 browser_exec로 별도. 출력: backend/_foreign_links_crawl.json
각 학교: {unvCd, name, ipsi_homepage, foreign_links: [..], foreign_admission_candidates: [...]}
"""
import requests, re, json, os, sys, time
from urllib.parse import urljoin

requests.packages.urllib3.disable_warnings()
sys.path.insert(0, ".")
B = os.path.dirname(os.path.abspath(__file__))
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0) Chrome/124.0", "Accept-Language": "ko-KR,ko;q=0.9"}

univ4 = json.load(open(os.path.join(B, "univ4_foreign_links.json"), encoding="utf-8"))
ipsi_to_cd = {}
for cd, v in univ4.items():
    if v.get("ipsi_homepage"):
        ipsi_to_cd[cd] = v

# 외국인 관련 링크 판별 키워드
FKEY = ["외국인", "국제", "글로벌", "international", "foreign", "global", "oia", "abroad", "해외", "유학생", "intl"]

def crawl(cd, url):
    try:
        r = requests.get(url, headers=H, verify=False, timeout=20)
        html = r.text
    except Exception as e:
        return {"error": str(e)[:60]}
    links = re.findall(r'href=[\'"]([^\'"]+)[\'"][^>]*>([^<]{2,60})</a>|<a[^>]+href=[\'"]([^\'"]+)[\'"]', html, re.I)
    found = []
    for m in links:
        href = m if isinstance(m, str) else (m[0] or m[2])
        text = (m[1] if isinstance(m, tuple) and len(m)>1 else "") or ""
        if not href or href.startswith(("javascript", "#", "mailto", "tel")): continue
        full = urljoin(url, href)
        if "adiga" in full: continue
        low = (full + " " + text).lower()
        if any(k in low for k in ["foreign", "international", "외국인", "국제", "global", "oia", "abroad", "유학", "intl"]):
            found.append({"url": full, "text": text.strip()[:40]})
    # 중복 제거
    seen = set(); uniq = []
    for f in found:
        if f["url"] in seen: continue
        seen.add(f["url"]); uniq.append(f)
    return {"links": uniq, "html_len": len(html)}

out = {}
for cd, v in list(ipsi_to_cd.items())[:70]:  # 배치1: 70교
    res = crawl(cd, v["ipsi_homepage"])
    out[cd] = {"name": v["name"], "ipsi_homepage": v["ipsi_homepage"],
               "foreign_candidates": res.get("links", []), "error": res.get("error")}
    print(f"{v['name']}: {len(res.get('links',[]))} foreign-candidate links")
    time.sleep(0.3)

json.dump(out, open(os.path.join(B, "_foreign_links_crawl.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print(f"\n저장: _foreign_links_crawl.json ({len(out)}교)")