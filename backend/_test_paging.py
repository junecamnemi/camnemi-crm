#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Try various pagination params for collAjax to get page 2 of junior colleges."""
import requests, re, json
requests.packages.urllib3.disable_warnings()
BASE = 'https://www.adiga.kr'
HEADERS = {'User-Agent': 'Mozilla/5.0', 'Accept-Language': 'ko-KR,ko;q=0.9'}

# Different param combos to get page 2 (should NOT be 가톨릭상지대 if paging works)
tests = [
    {'searchSyr': '2027', 'currentPage': '2', 'cntPerPage': '15'},
    {'searchSyr': '2027', 'page': '2', 'cntPerPage': '15'},
    {'searchSyr': '2027', 'currentPage': '2'},
    {'searchSyr': '2027', 'pageIndex': '2', 'cntPerPage': '15'},
    {'searchSyr': '2027', 'pageNum': '2', 'cntPerPage': '15'},
]

for params in tests:
    try:
        r = requests.post(f'{BASE}/ucp/uvt/col/collAjax.do', data=params, headers=HEADERS, verify=False, timeout=30)
        items = re.findall(r'code="(\d+)">([^<]+)</a>', r.text)
        first = items[0][1] if items else '?'
        print(f'{list(params.items())} → {len(items)}개, 첫={first}')
    except Exception as e:
        print(f'{list(params.items())} → ERR {e}')
