#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests, os
requests.packages.urllib3.disable_warnings()
UA={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"}
s=requests.Session(); s.headers.update(UA)
base="https://iec.chsu.ac.kr"
s.get(base+"/page.jsp?menuId=4000000155",verify=False,timeout=40)
q="?NTCE_SNTNC_NO=6&ATCH_SEQ=1&BOARD_ID=202502180000000006"
for path in ["/ardFileDownload.do","/iec/ardFileDownload.do","/boardPage.do/ardFileDownload.do"]:
    url=base+path+q
    r=s.get(url,verify=False,timeout=60)
    print(path,"http",r.status_code,"bytes",len(r.content),"ctype",r.headers.get("Content-Type"))
    if r.content[:4]==b'%PDF':
        fn=os.path.join(os.path.dirname(os.path.abspath(__file__)),"_chsu_guide.pdf")
        open(fn,"wb").write(r.content)
        print("SAVED",fn)
        break
    else:
        print("  not pdf:",r.content[:80])
