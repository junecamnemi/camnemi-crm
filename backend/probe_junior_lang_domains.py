#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""probe_junior_lang_domains.py — 전문대 어학원 하위도메인 전수 시도.

전문대 어학원은 kli/klec/ili/global/klc/language 등 하위도메인 패턴. requests로 전수 시도.
출력: backend/_junior_lang_domains.json
"""
import requests, re, json, os, time
from urllib.parse import urljoin
requests.packages.urllib3.disable_warnings()
B = os.path.dirname(os.path.abspath(__file__))
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0) Chrome/124.0", "Accept-Language": "ko-KR,ko;q=0.9"}

idx = json.load(open(os.path.join(B, "unvcd_index.json"), encoding="utf-8"))["schools"]
jr = [v for v in idx.values() if v["school_type"]=="junior" and not v.get("excluded")]
# 어학원 미보유
no = [v for v in jr if not v.get("foreign_links",{}).get("lang_foreign")]
print(f"어학원 미보유 전문대: {len(no)}")

# 어학원 하위도메인 후보
SUBS = ["kli", "klec", "ili", "klc", "language", "korean", "global", "intl", "oia", "international", "kli2", "klec2"]

def get_domain(home):
    m = re.match(r"https?://([^/]+)", home or "")
    return m.group(1) if m else ""

def probe(domain):
    """어학원 하위도메인 시도, 성공하면 URL 반환"""
    for sub in SUBS:
        url = f"https://{sub}.{domain}/"
        try:
            r = requests.get(url, headers=H, verify=False, timeout=6)
            if r.status_code == 200:
                # 어학원 관련 키워드 확인
                low = r.text.lower()
                if any(k in low for k in ["한국어", "어학", "korean", "language", "klec", "kli", "연수", "한국어교육"]):
                    return url
        except: continue
    return None

out = {}
for v in no:
    dom = get_domain(v.get("homepage"))
    if not dom: continue
    hit = probe(dom)
    out[v["unvCd"]] = {"name": v["name"], "domain": dom, "lang_url": hit}
    if hit:
        print(f"  HIT {v['name']}: {hit}")
    time.sleep(0.2)

json.dump(out, open(os.path.join(B, "_junior_lang_domains.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
hits = [v for v in out.values() if v["lang_url"]]
print(f"\n어학원 하위도메인 HIT: {len(hits)}교")
print("저장: _junior_lang_domains.json")