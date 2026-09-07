#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests, re, os
requests.packages.urllib3.disable_warnings()
UA={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"}
s=requests.Session(); s.headers.update(UA)
# warm up with the list page to get cookies
base="https://iec.chsu.ac.kr"
s.get(base+"/page.jsp?menuId=4000000155",verify=False,timeout=40)
view=base+"/boardPage.do?jspPage=/common/boardView&menuId=4000000155&SITE_ID=0000000006&BOARD_ID=202502180000000006&NTCE_SNTNC_NO=6&PAGE_NUM=1"
r=s.get(view,verify=False,timeout=50)
print("view http",r.status_code,"len",len(r.text))
r.encoding='utf-8'
open("_chsu_notice_view.html","wb").write(r.content)
# visible text around title
body=re.sub(r'<(script|style)[^>]*>.*?</\1>','',r.text,flags=re.S)
txt=re.sub(r'<[^>]+>',' ',body); txt=re.sub(r'\s+',' ',txt)
i=txt.find('모집 요강')
print("CTX:", txt[max(0,i-100):i+400] if i>=0 else txt[:400])
print("=== attachments ===")
# ITS attachments typically load via fileDown or a data service; look for links/files
for m in re.finditer(r'(?:href|src|value)="([^"]+)"', r.text):
    u=m.group(1)
    if re.search(r'\.(pdf|hwp|docx?|xlsx?|zip)|fileDown|download|atchFile|File',u,re.I):
        if not u.startswith('http'): u=base+u
        print("  ",u[:220])
# look for attach list container
for kw in ['첨부','파일','attach','fileNm','atch','Download','downFile','\.pdf']:
    c=re.findall(r'.{0,60}'+kw+r'.{0,80}', r.text, re.I)
    if c:
        print(f"[{kw}]", c[0][:200])
