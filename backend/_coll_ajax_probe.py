#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Enumerate junior colleges from adiga collAjax.do (132 items = 전문대학?)."""
import requests, re, json
requests.packages.urllib3.disable_warnings()
BASE = 'https://www.adiga.kr'
HEADERS = {'User-Agent': 'Mozilla/5.0', 'Accept-Language': 'ko-KR,ko;q=0.9'}

r = requests.post(f'{BASE}/ucp/uvt/col/collAjax.do',
                  data={'searchSyr': '2027', 'currentPage': 1, 'cntPerPage': 200},
                  headers=HEADERS, verify=False, timeout=30)
html = r.text
print('응답 길이:', len(html))

# extract univ codes and names - try multiple patterns
codes = re.findall(r'value="(\d+)"', html)
print('value 숫자 개수:', len(codes))
# look at raw structure around '대학'
idx = html.find('전문')
print('전문 context:', html[max(0,idx-80):idx+80] if idx >= 0 else '전문 없음')
idx2 = html.find('<li')
print('li context:', html[idx2:idx2+200] if idx2 >= 0 else 'li 없음')
# print first 300 chars of body
print('\n=== HTML 시작 (300자) ===')
print(html[:300])
