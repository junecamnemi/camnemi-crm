#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Try to enumerate junior colleges (전문대학) from adiga.kr.
The univGroupAjax API returns only 4-year univs; junior colleges use unvCd
like 0002654 (인하공업전문대학). Try the search/list APIs to enumerate them."""
import requests, re
requests.packages.urllib3.disable_warnings()
BASE = 'https://www.adiga.kr'
HEADERS = {'User-Agent': 'Mozilla/5.0', 'Accept-Language': 'ko-KR,ko;q=0.9'}

# Try the collDetail (전문대학?) API used on the search page
# collDetail.do = 대학(전문대?) 상세. Search API variants:
endpoints = [
    ('univAjax.do', {'searchSyr': '2027', 'currentPage': 1, 'cntPerPage': 15}),
    ('/ucp/uvt/col/collAjax.do', {'searchSyr': '2027', 'currentPage': 1, 'cntPerPage': 15}),
    ('/ucp/uvt/uni/univSearchAjax.do', {'searchSyr': '2027'}),
]

for ep, params in endpoints:
    try:
        url = BASE + ep if ep.startswith('/') else BASE + '/ucp/uvt/uni/' + ep
        r = requests.post(url, data=params, headers=HEADERS, verify=False, timeout=30)
        # look for univ codes
        cds = re.findall(r'searchUnvCode[^>]*value="(\d+)"', r.text)
        names = re.findall(r'<label[^>]*>\s*([^<]+?)\s*<strong>', r.text, re.S)
        total = re.search(r'totRecordCnt[^>]*value="(\d+)"', r.text)
        print(f'{ep}: codes={len(cds)}, names={len(names)}, total={total.group(1) if total else "?"}')
        if names:
            print('   샘플:', [n.strip()[:30] for n in names[:5]])
    except Exception as e:
        print(f'{ep}: ERR {e}')

# Known junior unvCds to test individually
print('\n--- 알려진 전문대 unvCd 테스트 (univFileAjax) ---')
for cd in ['0002654', '0002760', '0002810']:
    try:
        r = requests.post(f'{BASE}/ucp/uvt/uni/univFileAjax.do',
                          data={'searchSyr': '2027', 'unvCd': cd},
                          headers=HEADERS, verify=False, timeout=30)
        # is it disabled or has files?
        has_file = 'disabled' not in r.text
        nli = r.text.count('<li')
        print(f'  unvCd={cd}: {nli} 항목, enabled={has_file}')
    except Exception as e:
        print(f'  unvCd={cd}: ERR {e}')
