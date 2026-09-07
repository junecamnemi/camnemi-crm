#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Try session-based pagination with collAjax - some sites store page state in session."""
import requests, re
requests.packages.urllib3.disable_warnings()
BASE = 'https://www.adiga.kr'
HEADERS = {'User-Agent': 'Mozilla/5.0', 'Accept-Language': 'ko-KR,ko;q=0.9'}

s = requests.Session()
s.headers.update(HEADERS)
s.verify = False

# First load the list page to establish session
r0 = s.get(f'{BASE}/ucp/uvt/col/collList.do?menuId=PCPRCINF3000&searchSyr=2027', timeout=30)
print('세션 쿠키:', dict(s.cookies))

# Now request page with offset-based params
for params in [
    {'searchSyr': '2027', 'currentPage': '2', 'cntPerPage': '15', 'offset': '15'},
    {'searchSyr': '2027', 'currentPage': '2', 'cntPerPage': '15', 'start': '16'},
    {'searchSyr': '2027', 'currentPage': '2', 'cntPerPage': '15', 'pageIndex': '2', 'searchUnvCodeAllYn': 'true'},
    {'searchSyr': '2027', 'currentPage': '1', 'cntPerPage': '15', 'searchSchoolType': '10'},
]:
    try:
        r = s.post(f'{BASE}/ucp/uvt/col/collAjax.do', data=params, timeout=30)
        items = re.findall(r'code="(\d+)">([^<]+)</a>', r.text)
        first = items[0][1] if items else '?'
        print(f'{list(params.items())} → {len(items)}개, 첫={first}')
    except Exception as e:
        print(f'{list(params.items())} → ERR {e}')
