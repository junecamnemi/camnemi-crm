#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests, re, os
requests.packages.urllib3.disable_warnings()
UA={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"}
s=requests.Session(); s.headers.update(UA)
base="https://iec.chsu.ac.kr"
# try contView directly
for u in [base+"/contView.do?menuId=4000000106",
          base+"/page.jsp?menuId=4000000106",
          base+"/iec/contView.do?menuId=4000000106"]:
    try:
        r=s.get(u,verify=False,timeout=40); r.encoding='utf-8'
        print("URL",u,"http",r.status_code,"len",len(r.text))
        # visible text
        body=re.sub(r'<(script|style)[^>]*>.*?</\1>','',r.text,flags=re.S)
        t=re.sub(r'<[^>]+>',' ',body); t=re.sub(r'\s+',' ',t)
        print("TEXT:",t[:700])
        # links
        for mt in re.finditer(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>',r.text,re.S):
            href=mt.group(1); tx=re.sub(r'<[^>]+>','',mt.group(2)).strip()
            if re.search(r'\.pdf|\.hwp|외국|입학|모집|요강|download|첨부',href+tx,re.I):
                if not href.startswith('http'): href=base+href
                print("  *",repr(tx[:60]),"->",href[:170])
    except Exception as e:
        print("ERR",u,e)
