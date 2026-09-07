#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests, re
requests.packages.urllib3.disable_warnings()
UA={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"}
s=requests.Session(); s.headers.update(UA)

def clean(html):
    b=re.sub(r'<(script|style)[^>]*>.*?</\1>','',html,flags=re.S)
    t=re.sub(r'<[^>]+>',' ',b); return re.sub(r'\s+',' ',t)

# enter.chsu.ac.kr main
for u in ["https://enter.chsu.ac.kr/","https://enter.chsu.ac.kr/main.do"]:
    try:
        r=s.get(u,verify=False,timeout=40); r.encoding='utf-8'
        print("===== ",u," http",r.status_code,"len",len(r.text))
        t=re.search(r'<title>(.*?)</title>',r.text,re.S)
        print("title:", t.group(1).strip() if t else None)
        if len(r.text)>2000:
            # find links mentioning 외국/모집/요강
            for mt in re.finditer(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>',r.text,re.S):
                href=mt.group(1); tx=clean(mt.group(2))
                if re.search(r'외국|유학|모집|요강|입학',tx,re.I):
                    if not href.startswith('http'): href="https://enter.chsu.ac.kr"+href
                    print("   *",repr(tx[:60]),"->",href[:150])
            open("_enter_chsu_main.html","wb").write(r.content)
            break
    except Exception as e:
        print("ERR",u,e)
