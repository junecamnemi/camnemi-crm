#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check if collList.do page embeds the full junior college list in JS/JSON."""
import requests, re, json
requests.packages.urllib3.disable_warnings()
BASE = 'https://www.adiga.kr'
HEADERS = {'User-Agent': 'Mozilla/5.0', 'Accept-Language': 'ko-KR,ko;q=0.9'}

r = requests.get(f'{BASE}/ucp/uvt/col/collList.do?menuId=PCPRCINF3000&searchSyr=2027',
                 headers=HEADERS, verify=False, timeout=45)
html = r.text
print('페이지 길이:', len(html))

# look for embedded JSON or univ lists
# search for unvCd patterns
cods = re.findall(r'000\d{3,4}', html)
print('unvCd 코드 수:', len(set(cods)))

# look for a JSON array of colleges
json_like = re.findall(r'\[\s*\{[^]]*unvCd[^]]*\}\]', html)
print('JSON 배열 후보:', len(json_like))
if json_like:
    print(json_like[0][:500])

# search for '가톨릭상지대' occurrences and what's around
idxs = [m.start() for m in re.finditer(r'가톨릭상지대', html)]
print('\n가톨릭상지대 등장:', len(idxs))
if idxs:
    print(html[max(0,idxs[0]-100):idxs[0]+100].replace('\n',' ')[:200])

# Check if there's a script with all colleges
scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.S)
big = [s for s in scripts if '전문' in s or 'univCd' in s.lower() or '0000' in s]
print('\n관련 스크립트 블록:', len(big))
for s in big[:2]:
    print('  길이:', len(s), '| 샘플:', s[:200].replace('\n',' '))
