#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests, re, os
requests.packages.urllib3.disable_warnings()
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"}
s = requests.Session(); s.headers.update(UA)
url="https://iec.chsu.ac.kr/page.jsp?menuId=4000000106"
r=s.get(url,verify=False,timeout=50)
print("http", r.status_code, "len", len(r.content))
r.encoding = r.apparent_encoding if r.encoding=='ISO-8859-1' else r.encoding
# save raw
open("_chsu_page.html","wb").write(r.content)
# title
t=re.search(r'<title>(.*?)</title>', r.text, re.S)
print("title:", t.group(1).strip() if t else None)
# detect charset
m=re.search(r'charset=([\w-]+)', r.text[:2000])
print("charset decl:", m.group(1) if m else None)
# text
txt=re.sub(r'<(script|style)[^>]*>.*?</\1>','',r.text,flags=re.S)
txt=re.sub(r'<[^>]+>',' ',txt); txt=re.sub(r'[ \t\r\f\v]+',' ',txt)
print(txt[:1800])
print("\n=== links containing 외국/입학/요강/pdf/hwp/download/파일 ===")
for mt in re.finditer(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', r.text, re.S):
    href=mt.group(1); txt2=re.sub(r'<[^>]+>','',mt.group(2)).strip()
    if re.search(r'외국|입학|모집|요강|\.pdf|\.hwp|download|Down|File|파일|유학|가이드', href+txt2, re.I):
        if not href.startswith("http"): href="https://iec.chsu.ac.kr"+href
        print(" *", repr(txt2[:70]), "=>", href[:180])
