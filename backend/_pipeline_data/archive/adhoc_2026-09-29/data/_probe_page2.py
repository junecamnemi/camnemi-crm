#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Inspect how adiga pages the junior college list — look at the full collAjax response structure."""
import requests, re, json
requests.packages.urllib3.disable_warnings()
BASE = 'https://www.adiga.kr'
HEADERS = {'User-Agent': 'Mozilla/5.0', 'Accept-Language': 'ko-KR,ko;q=0.9'}

r = requests.post(f'{BASE}/ucp/uvt/col/collAjax.do',
                  data={'searchSyr': '2027', 'currentPage': 2, 'cntPerPage': 15},
                  headers=HEADERS, verify=False, timeout=45)
html = r.text
print('=== page=2 응답에서 selectUniv 항목 ===')
items = re.findall(r'code="(\d+)">([^<]+)</a>', html)
for cd, n in items:
    print(f'  {cd}: {n}')

print(f'\n총 {len(items)}개')

# Check pagination markers
for marker in ['currentPage', 'pageIndex', 'pageNum', 'next', 'pagination', 'goPage', 'movePage']:
    idxs = [m.start() for m in re.finditer(marker, html)]
    if idxs:
        print(f'\n{marker} @ {idxs[:3]}: {html[max(0,idxs[0]-30):idxs[0]+60]}')
