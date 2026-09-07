#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Diagnose why searchUnvNm misses some junior colleges — test a failing name directly."""
import requests, re
requests.packages.urllib3.disable_warnings()
BASE = 'https://www.adiga.kr'
HEADERS = {'User-Agent': 'Mozilla/5.0', 'Accept-Language': 'ko-KR,ko;q=0.9'}

for probe in ['대구보건대학교', '대구보건', '보건대학교', '대구', '명지전문대학', '명지']:
    r = requests.post(f'{BASE}/ucp/uvt/col/collAjax.do',
                      data={'searchSyr': '2027', 'searchUnvNm': probe},
                      headers=HEADERS, verify=False, timeout=25)
    items = re.findall(r'code="(\d+)">([^<]+)</a>', r.text)
    print(f'검색 "{probe}": {len(items)}개')
    for cd, nm in items[:8]:
        print(f'    {cd}: {nm}')
    print()
