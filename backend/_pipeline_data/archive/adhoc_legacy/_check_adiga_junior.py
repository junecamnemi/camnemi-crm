#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests, re, json
requests.packages.urllib3.disable_warnings()
BASE = 'https://www.adiga.kr'
HEADERS = {'User-Agent': 'Mozilla/5.0', 'Accept-Language': 'ko-KR,ko;q=0.9'}
r = requests.post(f'{BASE}/ucp/prc/uni/admssUnivDetailFrgnrGnrl.do',
                  data={'searchSyr': '2027', 'unvCd': '0002654', 'slcnCd': '09'},
                  headers=HEADERS, verify=False, timeout=30)
html = r.text
print('응답 길이:', len(html))

# find download links with labels
dls = re.findall(r'href="([^"]+)"[^>]*>\s*(?:<[^>]*>\s*)?([^<]{2,40})', html)
req_dls = [(u, t.strip()) for u, t in dls if any(k in t for k in ['외국인', '요강', '모집', '다운'])]
print('요강 다운로드 후보:')
for u, t in req_dls[:10]:
    print(f'  [{t}] {u[:90]}')

# fileDown occurrences
for m in re.finditer(r'fileDown', html):
    ctx = html[max(0, m.start()-50):m.start()+100]
    print('  fileDown ctx:', re.sub(r'\s+', ' ', ctx)[:140])
    break

# any disabled markers for 외국인
dis = re.findall(r'disabled[^>]*>\s*<[^>]*>\s*([^<]*외국인[^<]*)', html)
print('disabled 외국인:', dis[:3])
