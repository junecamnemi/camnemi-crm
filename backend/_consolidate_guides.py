#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""모든 모집요강을 한 폴더로 통합 + ADIGAID_학교_영어_레벨_연도_전후기.pdf 표준화."""
import json, os, re, time, urllib.request, shutil
import pymupdf

B=r"C:\Users\wisew\camnemi-crm\backend"
DEST=r"C:\Users\wisew\camnemi-crm\guides_all"
os.makedirs(DEST,exist_ok=True)
UA={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/131.0.0.0 Safari/537.36'}

# 영어이름 맵
enmap=json.load(open(B+r"\school_en_map.json",encoding="utf-8"))
# adiga upload map: filename(key) → {viewLink,...}
umap=json.load(open(B+r"\adiga2027_upload_map.json",encoding="utf-8"))
# guide master
master=json.load(open(B+r"\_guide_2027_master.json",encoding="utf-8"))
# junior
kb=json.load(open(B+r"\verified_kb.json",encoding="utf-8"))
junior=kb.get("junior",{}).get("schools",{})

def dl(url):
    try:
        if 'drive.google' in url:
            m=re.search(r'/file/d/([^/]+)',url) or re.search(r'[?&]id=([^&]+)',url)
            if m: url=f"https://drive.google.com/uc?export=download&id={m.group(1)}"
        return urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=90).read()
    except Exception as e:
        return None

def safe(s): return re.sub(r'[\\/:*?"<>|]+','',str(s)).strip()

def level_from(fn, kind):
    b=fn.lower()
    if kind=='junior' or '_전문학사' in b or 'junior' in b or '전문대' in b: return 'JUNIOR'
    if '_lang' in b or '_어학' in b or 'language' in b or '한국어학당' in b or '_학당' in b: return 'LANGUAGE'
    if 'ma' in b or '_대학원' in b or 'graduate' in b: return 'MA'
    return 'BA'

def year_from(fn):
    m=re.search(r'(202[67])',fn)
    return m.group(1) if m else ''

def term_from(fn):
    b=fn
    if '전기' in b or 'spring' in b.lower(): return '전기'
    if '후기' in b or 'fall' in b.lower(): return '후기'
    return ''

# build records
recs={}
# 1) adiga upload map
for fn,meta in umap.items():
    base=os.path.basename(fn)
    m=re.match(r'(\d+)_([^\[\]_]+)',base)
    aid=m.group(1) if m else ''
    name=(m.group(2) if m else base.replace('.pdf','')[:40]).strip()
    year=year_from(base)
    lv=level_from(base, '4year')
    url=meta.get('viewLink') if isinstance(meta,dict) else ''
    key=(aid,name,lv,year)
    if aid and url: recs.setdefault(key,url)
# 2) guide master ba/ma
for x in master:
    for lv in ['ba','ma']:
        u=x.get(f"{lv}_url")
        if not (u and 'http' in u): continue
        name=x['school']; year=''
        y=re.search(r'(202[67])', str(x.get(f"{lv}_title") or ''))
        if y: year=y.group(1)
        if not year: year='2027' if '2027' in str(x.get(f"{lv}_status")) else '2026'
        # adiga id from processed_guides if exists
        recs.setdefault(('',name,lv.upper(),year),u)
# 3) junior
for name,s in junior.items():
    if not isinstance(s,dict): continue
    u=s.get('guide_url')
    if u and 'http' in u:
        recs.setdefault(('',name,'JUNIOR',''),u)

print(f"통합 대상 요강: {len(recs)}개")
# adiga id coverage
with_aid=sum(1 for (aid,*_),_ in recs.items() if aid)
print(f"adiga ID 보유: {with_aid} | 미보유: {len(recs)-with_aid}")

# download + rename (sequential id for missing adiga)
seq=900000
done=0; fail=0
log=open(B+r"\_guides_consolidate_log.txt",'w',encoding='utf-8')
for (aid,name,lv,year),url in recs.items():
    data=dl(url)
    if not data or len(data)<1000:
        fail+=1; log.write(f"[FAIL] {name}/{lv}\n"); continue
    # english name
    en=enmap.get(name,'')
    en_part=safe(en) if en else ''
    if not aid:
        aid=str(seq); seq+=1
    if not year: year=''
    term=term_from(os.path.basename(url))
    parts=[f"{aid}", safe(name)]
    if en_part: parts.append(en_part)
    parts.append(lv)
    if year: parts.append(year)
    if term: parts.append(term)
    fname="_".join(parts)+".pdf"
    fpath=os.path.join(DEST,fname)
    open(fpath,'wb').write(data)
    done+=1
    log.write(f"[OK] {fname}\n")
    if done%25==0: print(f"... {done} 다운로드",flush=True)
log.close()
print(f"완료: {done} 다운로드 | 실패: {fail} | 총 {len(recs)}")