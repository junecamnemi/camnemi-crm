#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""crawl_junior_foreign.py — 전문대 홈페이지에서 외국인 학부 입학 링크를 requests로 추출.

각 전문대 home에서 외국인/국제/입학/모집 링크를 찾아 후보 URL 수집.
출력: backend/_junior_foreign_crawl.json
"""
import requests, re, json, os, sys, time
from urllib.parse import urljoin
requests.packages.urllib3.disable_warnings()
B = os.path.dirname(os.path.abspath(__file__))
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0) Chrome/124.0", "Accept-Language": "ko-KR,ko;q=0.9"}

idx = json.load(open(os.path.join(B, "unvcd_index.json"), encoding="utf-8"))["schools"]
jr = [v for v in idx.values() if v["school_type"]=="junior" and not v.get("excluded")]
# 이미 URL 있는 것 제외
targets = [v for v in jr if not v.get("foreign_links",{}).get("ba_foreign")]
print(f"전문대 미보유: {len(targets)}")

FKEY = ["외국인", "국제", "글로벌", "international", "foreign", "global", "oia", "abroad", "유학", "입학", "모집", "admission", "apply"]

def crawl(url):
    try:
        r = requests.get(url, headers=H, verify=False, timeout=15)
        html = r.text
    except Exception as e:
        return {"error": str(e)[:50]}
    links = re.findall(r'href=[\'"]([^\'"]+)[\'"][^>]*>([^<]{2,60})</a>', html, re.I)
    found = []
    for href, text in links:
        if not href or href.startswith(("javascript", "#", "mailto", "tel")): continue
        full = urljoin(url, href)
        if "adiga" in full or "uway" in full or "jinhak" in full: continue
        low = (full + " " + text).lower()
        if any(k in low for k in FKEY):
            found.append({"url": full, "text": text.strip()[:40]})
    # 중복 제거
    seen=set(); uniq=[]
    for f in found:
        if f["url"] in seen: continue
        seen.add(f["url"]); uniq.append(f)
    return {"links": uniq, "html_len": len(html)}

out = {}
for v in targets:
    home = v.get("homepage")
    if not home: continue
    res = crawl(home)
    out[v["unvCd"]] = {"name": v["name"], "home": home, "candidates": res.get("links", []), "error": res.get("error")}
    print(f"{v['name']}: {len(res.get('links',[]))} 후보")
    time.sleep(0.3)

json.dump(out, open(os.path.join(B, "_junior_foreign_crawl.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print(f"\n저장: _junior_foreign_crawl.json ({len(out)}교)")