#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Try to find each junior college's unvCd via adiga search-by-name on collAjax."""
import requests, re, json
requests.packages.urllib3.disable_warnings()
BASE = 'https://www.adiga.kr'
HEADERS = {'User-Agent': 'Mozilla/5.0', 'Accept-Language': 'ko-KR,ko;q=0.9'}

# load 126 junior names
with open(r"C:\Users\USER\camnemi-crm\backend\verified_kb.json", encoding="utf-8") as f:
    kb = json.load(f)
juniors = list(kb["junior"]["schools"].keys())

# load existing known unvcds
with open(r"C:\Users\USER\camnemi-crm\backend\_guide_2027_junior.json", encoding="utf-8") as f:
    existing = json.load(f)
known = {name: v["unvCd"] for name, v in existing.items() if v["unvCd"]}

found = dict(known)
# test search params on a few to discover the mechanism
def try_search(name):
    for params in [
        {'searchSyr': '2027', 'searchUnvNm': name},
        {'searchSyr': '2027', 'searchUnvCode': '', 'searchUnvNm': name, 'cntPerPage': '200'},
        {'searchSyr': '2027', 'schNm': name},
        {'searchSyr': '2027', 'searchTitle': name},
    ]:
        try:
            r = requests.post(f'{BASE}/ucp/uvt/col/collAjax.do', data=params, headers=HEADERS, verify=False, timeout=20)
            items = re.findall(r'code="(\d+)">([^<]+)</a>', r.text)
            for cd, nm in items:
                if name.replace("대학","").replace("대학교","")[:4] in nm:
                    return cd
        except:
            pass
    return None

# test on first 5 unknowns
tested = 0
for name in juniors:
    if name in found:
        continue
    cd = try_search(name)
    if cd:
        found[name] = cd
        print(f"발견: {name} → {cd}")
    tested += 1
    if tested >= 10:
        break

print(f"\n테스트 {tested}개 중 발견 {len(found)-len(known)}개")
print("총 알려진 unvCd:", len(found))
