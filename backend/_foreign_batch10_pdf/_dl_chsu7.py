#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests, re, os
requests.packages.urllib3.disable_warnings()
UA={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"}
s=requests.Session(); s.headers.update(UA)
base="https://iec.chsu.ac.kr"
boardview=base+"/boardPage.do?jspPage=/common/boardView&menuId=4000000155&SITE_ID=0000000006&BOARD_ID=202502180000000006&NTCE_SNTNC_NO=6&PAGE_NUM=1"
s.get(base+"/page.jsp?menuId=4000000155",verify=False,timeout=40)
s.get(boardview,verify=False,timeout=50)  # establish session + referer chain
url=base+"/ardFileDownload.do?NTCE_SNTNC_NO=6&ATCH_SEQ=1&BOARD_ID=202502180000000006"
r=s.get(url,verify=False,timeout=60,headers={"Referer":boardview})
print("http",r.status_code,"bytes",len(r.content),"ctype",r.headers.get("Content-Type"))
if r.content[:4]==b'%PDF':
    open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"_chsu_guide.pdf"),"wb").write(r.content)
    print("SAVED PDF")
else:
    txt=re.sub(r'<[^>]+>',' ',r.text); print("ERRBODY:", re.sub(r'\s+',' ',txt)[:600])
