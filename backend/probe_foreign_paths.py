#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""probe_foreign_paths.py — 각 학교 입시홈페이지 도메인에서 외국인 입시 경로 후보를 requests로 직접 시도.

패턴: {domain}/international, /abroad, /foreign, /global, /oia, /admission/international 등
200 응답 + 외국인 키워드 포함 시 후보로 기록.
출력: backend/_foreign_path_probe.json
"""
import requests, re, json, os, sys, time
from urllib.parse import urlparse, urljoin
requests.packages.urllib3.disable_warnings()
sys.path.insert(0, ".")
B = os.path.dirname(os.path.abspath(__file__))
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0) Chrome/124.0", "Accept-Language": "ko-KR,ko;q=0.9"}

univ4 = json.load(open(os.path.join(B, "univ4_foreign_links.json"), encoding="utf-8"))
# ba 미보유 61교 (master에서)
master = json.load(open(os.path.join(B, "_univ4_2027_master_links.json"), encoding="utf-8"))
no_ba = [cd for cd, v in master.items() if not v.get("ba_url")]

# 각 학교의 입시홈페이지/홈페이지 도메인
targets = {}
for cd in no_ba:
    v = univ4.get(cd, {})
    base = v.get("ipsi_homepage") or v.get("homepage")
    if not base: continue
    targets[cd] = {"name": v.get("name"), "base": base}

# 외국인 경로 후보
PATHS = ["international", "abroad", "foreign", "global", "oia", "intl",
         "admission/international", "admission/abroad", "international/admission",
         "international/undergraduate", "international/guide", "admission/foreign",
         "international/notice", "international/apply", "international/application"]

def probe(base, path):
    url = urljoin(base.rstrip("/") + "/", path)
    try:
        r = requests.get(url, headers=H, verify=False, timeout=12, allow_redirects=True)
        if r.status_code != 200: return None
        low = r.text.lower()
        # 외국인 관련 키워드
        if any(k in low for k in ["외국인", "international", "foreign", "global", "oia", "유학생", "abroad"]):
            return {"url": r.url, "status": r.status_code, "len": len(r.text)}
    except Exception:
        pass
    return None

out = {}
for cd, t in targets.items():
    found = []
    for p in PATHS:
        res = probe(t["base"], p)
        if res:
            found.append(res)
            if len(found) >= 3: break
        time.sleep(0.15)
    out[cd] = {"name": t["name"], "base": t["base"], "hits": found}
    print(f"{t['name']}: {len(found)} hits")

json.dump(out, open(os.path.join(B, "_foreign_path_probe.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print(f"\n저장: _foreign_path_probe.json ({len(out)}교)")