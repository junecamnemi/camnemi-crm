#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""crawl_junior_lang2.py — 전문대 국제교류처/입시홈페이지에서 어학원 링크 추출.

이미 확보한 _junior_ipsi_probe.json(입시홈페이지)과 _junior_foreign_crawl.json(홈페이지)의
국제교류처/입학 링크에서 어학원(한국어교육원) 링크를 찾는다.
출력: backend/_junior_lang2_crawl.json
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

# 이미 확보한 크롤 데이터에서 국제교류처/입학 링크 수집
def collect_seed_urls():
    seeds = {}
    for fname in ["_junior_ipsi_probe.json", "_junior_foreign_crawl.json"]:
        try:
            d = json.load(open(os.path.join(B, fname), encoding="utf-8"))
        except: continue
        for cd, v in d.items():
            name = v.get("name")
            urls = []
            if v.get("hit_url"): urls.append(v["hit_url"])
            for c in v.get("candidates", []):
                u = c.get("url","")
                if any(k in u.lower() for k in ["global","oia","intl","international","inter","foreign","ipsi","iphak","admission","enter"]):
                    urls.append(u)
            if urls:
                seeds.setdefault(name, []).extend(urls)
    return seeds

seeds = collect_seed_urls()
print(f"시드 URL 있는 학교: {len(seeds)}")

LKEY = ["한국어", "어학", "language", "korean", "klec", "kli", "어학당", "한국어교육", "한국어센터", "연수", "어학원"]

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
    name = v["name"]
    seed_urls = seeds.get(name, [])
    if not seed_urls:
        seed_urls = [v.get("homepage")]
    all_found = []
    for u in seed_urls[:3]:
        all_found.extend(crawl(u))
    # 중복 제거
    seen=set(); uniq=[]
    for f in all_found:
        if f["url"] in seen: continue
        seen.add(f["url"]); uniq.append(f)
    out[v["unvCd"]] = {"name": name, "candidates": uniq}
    if uniq:
        print(f"{name}: {len(uniq)}개 어학 링크")
    time.sleep(0.2)

json.dump(out, open(os.path.join(B, "_junior_lang2_crawl.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
withcand = [v for v in out.values() if v["candidates"]]
print(f"\n어학 링크 있는 교: {len(withcand)}")
print("저장: _junior_lang2_crawl.json")