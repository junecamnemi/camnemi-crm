#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extract junior colleges from adiga collAjax.do — try larger page size."""
import requests, re, json
requests.packages.urllib3.disable_warnings()
BASE = 'https://www.adiga.kr'
HEADERS = {'User-Agent': 'Mozilla/5.0', 'Accept-Language': 'ko-KR,ko;q=0.9'}

# try cntPerPage=200 to get all at once
for params in [
    {'searchSyr': '2027', 'currentPage': 1, 'cntPerPage': 200},
    {'searchSyr': '2027', 'currentPage': 1, 'cntPerPage': 200, 'searchUnvCodeAllYn': 'true'},
    {'searchSyr': '2027', 'currentPage': 1, 'cntPerPage': 999},
]:
    try:
        r = requests.post(f'{BASE}/ucp/uvt/col/collAjax.do', data=params, headers=HEADERS, verify=False, timeout=60)
        items = re.findall(r'code="(\d+)">([^<]+)</a>', r.text)
        print(f'params {params} → {len(items)}개')
        if len(items) > 15:
            with open(r'C:\Users\USER\camnemi-crm\backend\_junior_unis.json', 'w', encoding='utf-8') as f:
                json.dump(dict(items), f, ensure_ascii=False, indent=2)
            print('저장 완료!')
            names = [n for _, n in items]
            print('샘플:', names[:10])
            break
    except Exception as e:
        print(f'ERR: {e}')
