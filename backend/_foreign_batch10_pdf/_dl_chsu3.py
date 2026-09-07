#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests, re, os
requests.packages.urllib3.disable_warnings()
UA={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"}
s=requests.Session(); s.headers.update(UA)
base="https://iec.chsu.ac.kr"

def clean(html):
    b=re.sub(r'<(script|style)[^>]*>.*?</\1>','',html,flags=re.S)
    t=re.sub(r'<[^>]+>',' ',b); return re.sub(r'\s+',' ',t)

# 1) main international page full text + links
r=s.get(base+"/contView.do?menuId=4000000106",verify=False,timeout=40); r.encoding='utf-8'
print("=== main contView 4000000106 TEXT ===")
print(clean(r.text))
print("\n=== DOC LINKS ===")
for mt in re.finditer(r'(?:href|src)="([^"]+\.(?:pdf|hwp|docx?|xlsx?|zip))"', r.text, re.I):
    u=mt.group(1)
    if not u.startswith('http'): u=base+u
    print("  DOC:", u)
for mt in re.finditer(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>',r.text,re.S):
    href=mt.group(1); tx=clean(mt.group(2))
    if re.search(r'외국|입학|모집|요강|다운|첨부',tx,re.I):
        if not href.startswith('http'): href=base+href
        print("  *",repr(tx[:70]),"->",href[:160])

# 2) notice board page (foreigner admission notices)
print("\n\n=== NOTICE BOARD 4000000155 ===")
r2=s.get(base+"/page.jsp?menuId=4000000155",verify=False,timeout=40); r2.encoding='utf-8'
print("len",len(r2.text),"title", (re.search(r'<title>(.*?)</title>',r2.text,re.S).group(1) if re.search(r'<title>(.*?)</title>',r2.text,re.S) else None))
# it may JS redirect; try boardPage / contView
open("_chsu_notice.html","wb").write(r2.content)
print("links to notice items:")
for mt in re.finditer(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>',r2.text,re.S):
    href=mt.group(1); tx=clean(mt.group(2))
    if re.search(r'외국|입학|모집|요강|2026|2027',tx,re.I):
        if not href.startswith('http'): href=base+href
        print("  *",repr(tx[:70]),"->",href[:160])
