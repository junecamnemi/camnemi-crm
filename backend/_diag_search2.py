#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Try GET requests and full param sets for collAjax (maybe POST params are ignored)."""
import requests, re
requests.packages.urllib3.disable_warnings()
BASE = 'https://www.adiga.kr'
HEADERS = {'User-Agent': 'Mozilla/5.0', 'Accept-Language': 'ko-KR,ko;q=0.9'}

# try GET with query string
tests = [
    ('GET', f'{BASE}/ucp/uvt/col/collAjax.do?searchSyr=2027&searchUnvNm=대구보건대학교&cntPerPage=200'),
    ('GET', f'{BASE}/ucp/uvt/col/collList.do?menuId=PCPRCINF3000&searchSyr=2027&searchUnvNm=대구보건대학교'),
    ('POST', f'{BASE}/ucp/uvt/col/collAjax.do', {'searchSyr':'2027','searchUnvNm':'대구보건대학교','searchUnvCodeAllYn':'true','cntPerPage':'200'}),
    ('POST', f'{BASE}/ucp/uvt/col/collAjax.do', {'searchSyr':'2027','searchUnvNm':'대구보건대학교','pageSize':'200','cntPerPage':'200'}),
    ('POST', f'{BASE}/ucp/uvt/col/collAjax.do', {'searchSyr':'2027','searchUnvNm':'대구보건대학교','cntPerPage':'200','searchUnvNmList':''}),
]

for method, url, *data in tests:
    try:
        if method == 'GET':
            r = requests.get(url, headers=HEADERS, verify=False, timeout=25)
        else:
            r = requests.post(url, data=data[0], headers=HEADERS, verify=False, timeout=25)
        items = re.findall(r'code="(\d+)">([^<]+)</a>', r.text)
        has_target = any('대구보건' in nm for _, nm in items)
        print(f'{method} {url[:80]} → {len(items)}개, 대구보건 포함={has_target}')
        if has_target:
            for cd, nm in items:
                if '대구보건' in nm:
                    print(f'   ★ {cd}: {nm}')
    except Exception as e:
        print(f'{method} → ERR {e}')
