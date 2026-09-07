#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests, re, os, sys
requests.packages.urllib3.disable_warnings()
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"}
OUT = os.path.dirname(os.path.abspath(__file__))
s = requests.Session(); s.headers.update(UA)

# Notice detail page -> extract download URLs (순수외국인 모집요강)
detail = "https://enter.du.ac.kr/detail.do?mainNotice=Y&board_seq=6613"
r = s.get(detail, verify=False, timeout=40)
r.encoding = "utf-8"
print("detail http", r.status_code, "len", len(r.text))
print("is dongseoul?", "동서울" in r.text)
# all download links
for m in re.finditer(r'href="([^"]*download\.do[^"]*)"', r.text):
    url = m.group(1)
    if not url.startswith("http"):
        url = "https://enter.du.ac.kr" + url
    print("DL:", url[:200])
