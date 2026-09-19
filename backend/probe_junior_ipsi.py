#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""probe_junior_ipsi.py — 전문대 미보유 55교의 입시홈페이지(ipsi/iphak) 도메인을 requests로 직접 시도.

전문대는 대부분 ipsi.{domain} 또는 iphak.{domain} 패턴. 이걸 requests로 시도해 외국인 링크 추출.
출력: backend/_junior_ipsi_probe.json
"""
import requests, re, json, os, time
from urllib.parse import urljoin
requests.packages.urllib3.disable_warnings()
B = os.path.dirname(os.path.abspath(__file__))
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0) Chrome/124.0", "Accept-Language": "ko-KR,ko;q=0.9"}

idx = json.load(open(os.path.join(B, "unvcd_index.json"), encoding="utf-8"))["schools"]
jr = [v for v in idx.values() if v["school_type"]=="junior" and not v.get("excluded")]
no = [v for v in jr if not v.get("foreign_links",{}).get("ba_foreign")]
print(f"미보유 전문대: {len(no)}")

FKEY = ["외국인", "국제", "글로벌", "international", "foreign", "global", "oia", "abroad", "유학", "입학", "모집", "admission", "apply", "재외"]

def probe(domain, paths):
    for p in paths:
        url = f"https://{domain}{p}"
        try:
            r = requests.get(url, headers=H, verify=False, timeout=10)
            if r.status_code != 200: continue
            html = r.text
            links = re.findall(r'href=[\'"]([^\'"]+)[\'"][^>]*>([^<]{2,60})</a>', html, re.I)
            found = []
            for href, text in links:
                if not href or href.startswith(("javascript","#","mailto","tel")): continue
                full = urljoin(url, href)
                if "adiga" in full or "uway" in full or "jinhak" in full: continue
                low = (full+" "+text).lower()
                if any(k in low for k in FKEY):
                    found.append({"url": full, "text": text.strip()[:40]})
            if found:
                return url, found
        except: continue
    return None, []

out = {}
for v in no:
    home = v.get("homepage") or ""
    m = re.match(r"https?://([^/]+)", home)
    domain = m.group(1) if m else ""
    if not domain: continue
    # ipsi/iphak/입학 경로 후보
    paths = ["/ipsi/", "/iphak/", "/ipsi", "/iphak", "/admission/", "/enter/", "/ip/"]
    hit_url, found = probe(domain, paths)
    out[v["unvCd"]] = {"name": v["name"], "domain": domain, "hit_url": hit_url, "candidates": found}
    print(f"{v['name']}: {'HIT '+hit_url if hit_url else 'miss'} ({len(found)})")
    time.sleep(0.3)

json.dump(out, open(os.path.join(B, "_junior_ipsi_probe.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print(f"\n저장: _junior_ipsi_probe.json ({len(out)}교)")