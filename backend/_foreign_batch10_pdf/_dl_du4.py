#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests, os, re
requests.packages.urllib3.disable_warnings()
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"}
OUT = os.path.dirname(os.path.abspath(__file__))
s = requests.Session(); s.headers.update(UA)

# get the ENG pdf url from 모집요강 page
u="https://enter.du.ac.kr/submenu.do?menuUrl=xb3PYzpHlMe9%2fKoPQ1rtwA%3d%3d"
h=s.get(u,verify=False,timeout=40); h.encoding="utf-8"
m=re.search(r'href="([^"]*download\.do[^"]*ENG[^"]*)"', h.text)
eng_url="https://enter.du.ac.kr"+m.group(1)
# KOR from notice
h2=s.get("https://enter.du.ac.kr/detail.do?mainNotice=Y&board_seq=6613",verify=False,timeout=40); h2.encoding="utf-8"
m2=re.search(r'href="([^"]*download\.do[^"]*KOR[^"]*)"', h2.text)
kor_url="https://enter.du.ac.kr"+m2.group(1)

for label,url in [("ENG",eng_url),("KOR",kor_url)]:
    r=s.get(url,verify=False,timeout=60)
    fn=os.path.join(OUT,f"_du_{label}.pdf")
    open(fn,"wb").write(r.content)
    print(label, "http", r.status_code, "bytes", len(r.content), "ctype", r.headers.get("Content-Type"), "->", fn)
    if r.content[:4]==b'%PDF': print("  valid PDF")
    else: print("  NOT PDF:", r.content[:100])
