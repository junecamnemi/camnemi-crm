#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extract ALL junior colleges from adiga collAjax.do.
The API returns a JSON array with pagination; iterate all pages (132 total)."""
import requests, re, json, time
requests.packages.urllib3.disable_warnings()
BASE = 'https://www.adiga.kr'
HEADERS = {'User-Agent': 'Mozilla/5.0', 'Accept-Language': 'ko-KR,ko;q=0.9'}

# The response seems to contain JSON - let's inspect the raw structure more
# We saw 'pagination':{...} in the response - it's likely a JS object assignment
# Let's fetch page 1 and dump the raw structure to understand pagination
r = requests.post(f'{BASE}/ucp/uvt/col/collAjax.do',
                  data={'searchSyr': '2027', 'currentPage': 1, 'cntPerPage': 15},
                  headers=HEADERS, verify=False, timeout=45)
html = r.text

# Look for the actual data structure - maybe it's JSON embedded
# Try to find a JSON block
json_match = re.search(r'(\{.*"pagination".*\})', html, re.S)
if json_match:
    try:
        data = json.loads(json_match.group(1))
        print("JSON 구조 키:", list(data.keys()))
        print("pagination:", data.get("pagination"))
        items = data.get("list") or data.get("rows") or data.get("result") or []
        print("아이템 수:", len(items) if isinstance(items, list) else "?")
        if isinstance(items, list) and items:
            print("첫 아이템:", items[0])
    except Exception as e:
        print("JSON 파싱 실패:", e)
else:
    print("JSON 블록 없음")

# Save raw for inspection
with open(r'C:\Users\USER\camnemi-crm\backend\_coll_raw_page1.txt', 'w', encoding='utf-8') as f:
    f.write(html)
print("\n원본 저장 완료 (backend/_coll_raw_page1.txt)")
