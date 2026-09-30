#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""48개 실패 요강 — Playwright로 학교 페이지에서 PDF 링크 찾아 다운로드."""
import json, os, re, sys, time, urllib.request
import pymupdf
from playwright.sync_api import sync_playwright

B=r"C:\Users\wisew\camnemi-crm\backend"
DEST=r"C:\Users\wisew\camnemi-crm\guides_all"
enmap=json.load(open(B+r"\school_en_map.json",encoding='utf-8'))

# failed (school, level) → URL 재구성 (master에서)
master=json.load(open(B+r"\_guide_2027_master.json",encoding='utf-8'))
url_map={}
for x in master:
    for lv in ["ba","ma"]:
        if x.get(f"{lv}_url"): url_map[(x["school"],lv.upper())]=x[f"{lv}_url"]
fails=[]
for line in open(B+r"\_guides_consolidate_log.txt",encoding='utf-8'):
    if line.startswith('[FAIL]'):
        sl=line.replace('[FAIL]','').strip()  # "가천대학교/MA"
        if '/' in sl:
            sch,lv=sl.rsplit('/',1)
            u=url_map.get((sch.strip(),lv.upper().strip()))
            if u: fails.append((sch.strip(),lv.upper().strip(),u))

aid_map={}
umap=json.load(open(B+r"\adiga2027_upload_map.json",encoding='utf-8'))
for fn in umap:
    b=os.path.basename(fn); m=re.match(r'(\d+)_([^\[\]_]+)',b)
    if m: aid_map[m.group(2)]=m.group(1)

def safe(s): return re.sub(r'[\\/:*?"<>|]+','',str(s)).strip()
def std_name(school,lv):
    en=enmap.get(school,'')
    aid=aid_map.get(school) or ('9'+str(900000+len(os.listdir(DEST))))
    p=[aid,safe(school)]
    if en: p.append(en)
    p.append(lv); p.append('2026')
    return "_".join(p)+".pdf"

def dl(url,tmo=60):
    req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
    return urllib.request.urlopen(req,timeout=tmo).read()

ok=fail=0
with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,args=['--no-sandbox'])
    pg=browser.new_page(user_agent='Mozilla/5.0 Chrome/131')
    for school,lv,url in fails:
        fname=std_name(school,lv)
        try:
            pg.goto(url,wait_until='domcontentloaded',timeout=60000); time.sleep(3)
            # collect candidate pdf links
            cands=pg.eval_on_selector_all("a[href*='.pdf'], a[href*='download'], a[href*='atchmnfl']",
                "els=>els.map(e=>({h:e.href,t:e.textContent.trim()})).filter(x=>x.h && x.h.startsWith('http'))")
            got=False
            for c in cands[:8]:
                try:
                    data=dl(c['h'],tmo=60)
                    if len(data)>2000 and data[:5]==b'%PDF':
                        open(os.path.join(DEST,fname),'wb').write(data); ok+=1; got=True
                        print(f"OK {school} {lv} <- {c['h'][:60]}",flush=True); break
                except: pass
            if not got:
                fail+=1; print(f"FAIL {school} {lv} (PDF링크 못 찾음)",flush=True)
        except Exception as e:
            fail+=1; print(f"FAIL {school} {lv} {str(e)[:50]}",flush=True)
    browser.close()
print(f"완료: 성공 {ok} 실패 {fail} / 총 {len(fails)}")
