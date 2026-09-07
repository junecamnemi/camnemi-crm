#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests, re, os
requests.packages.urllib3.disable_warnings()
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"}
s = requests.Session(); s.headers.update(UA)
url="https://enter.du.ac.kr/submenu.do?menuUrl=xb3PYzpHlMe9%2fKoPQ1rtwA%3d%3d"
h=s.get(url,verify=False,timeout=40); h.encoding="utf-8"; html=h.text
# readable text of main content area
body=re.sub(r'<(script|style)[^>]*>.*?</\1>','',html,flags=re.S)
text=re.sub(r'<[^>]+>',' ',body)
text=re.sub(r'\s+',' ',text)
# focus on region mentioning 외국/모집/입학
idx=text.find('모집요강')
print(text[max(0,idx-200):idx+1500])
print("\n=== ALL download links full ===")
for m in re.finditer(r'href="([^"]*download\.do[^"]*)"', html):
    u=m.group(1)
    if not u.startswith("http"): u="https://enter.du.ac.kr"+u
    print(u)
