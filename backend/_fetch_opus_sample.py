#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""표본 학교 요강 PDF 다운로드 + 텍스트 추출"""
import json, os, urllib.request, urllib.parse, io, re, time
import pymupdf

OUT=r"C:\Users\USER\camnemi-crm\backend\_opus_sample"
os.makedirs(OUT,exist_ok=True)
UA={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/131.0.0.0 Safari/537.36'}

def dl_gdrive(url):
    fid=re.search(r'/file/d/([^/]+)',url)
    if not fid: return None
    dl=f"https://drive.google.com/uc?export=download&id={fid.group(1)}"
    try:
        req=urllib.request.Request(dl,headers=UA)
        return urllib.request.urlopen(req,timeout=60).read()
    except Exception as e:
        print("  gdrive오류",e); return None

def dl(url):
    try:
        if 'drive.google' in url: return dl_gdrive(url)
        req=urllib.request.Request(url,headers=UA)
        return urllib.request.urlopen(req,timeout=60).read()
    except Exception as e:
        print("  dl오류",str(e)[:80]); return None

def pdftext(data):
    try:
        d=pymupdf.open(stream=data,filetype="pdf")
        return "\n".join(p.get_text() for p in d)
    except Exception as e: return ""

B=r"C:\Users\USER\camnemi-crm\backend"
u=json.load(open(B+r"\upserted_2027.json",encoding='utf-8')).get('upserts',[])
ba={}
for s in u:
    if s[1]=='ba': ba.setdefault(s[0],s[2])
sample=["경북대학교","전북대학교","중앙대학교","건국대학교","부산대학교","경희대학교","성균관대학교","한양대학교","국민대학교","한국외국어대학교","경기대학교","명지대학교","단국대학교","홍익대학교","인하대학교"]
res={}
for nm in sample:
    url=ba.get(nm)
    if not url: print(nm,"URL없음"); continue
    data=dl(url)
    txt=pdftext(data) if data else ""
    chars=len(txt)
    res[nm]={"url":url,"chars":chars}
    print(f"{nm}: {chars}자")
    if chars>0:
        open(os.path.join(OUT,nm.replace('대학교','')+'.txt'),'w',encoding='utf-8').write(txt[:60000])
    time.sleep(1)
json.dump(res,open(OUT+r"\_meta.json",'w',encoding='utf-8'),ensure_ascii=False)
print("완료:", {k:v['chars'] for k,v in res.items()})