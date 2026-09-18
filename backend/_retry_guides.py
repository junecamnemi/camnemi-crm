#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""51개 실패 요강 재시도 (더 긴 타임아웃 + 재시도)."""
import json, os, re, time, urllib.request
B=r"C:\Users\USER\camnemi-crm\backend"
DEST=r"C:\Users\USER\camnemi-crm\guides_all"
UA={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/131.0.0.0 Safari/537.36'}

enmap=json.load(open(B+r"\school_en_map.json",encoding="utf-8"))
umap=json.load(open(B+r"\adiga2027_upload_map.json",encoding="utf-8"))
master=json.load(open(B+r"\_guide_2027_master.json",encoding="utf-8"))
kb=json.load(open(B+r"\verified_kb.json",encoding="utf-8"))
junior=kb.get("junior",{}).get("schools",{})

# build school+level -> url
src={}
for fn,meta in umap.items():
    base=os.path.basename(fn); m=re.match(r'(\d+)_([^\[\]_]+)',base)
    if m:
        src.setdefault((m.group(2).strip(),'BA'),(m.group(1),meta.get('viewLink','') if isinstance(meta,dict) else ''))
for x in master:
    for lv,key in [('ba','BA'),('ma','MA')]:
        u=x.get(f"{lv}_url")
        if u and 'http' in u: src.setdefault((x['school'],key),('',u))
for name,s in junior.items():
    if isinstance(s,dict) and s.get('guide_url'):
        src.setdefault((name,'JUNIOR'),('',s['guide_url']))

fails=["가천대학교/MA","강남대학교/MA","강원대학교/BA","경기대학교/MA","경일대학교/MA","광주대학교/BA","광주여자대학교/BA","광주여자대학교/MA","대진대학교/MA","동서대학교/BA","동의대학교/BA","삼육대학교/BA","서울기독대학교/MA","세명대학교/BA","세명대학교/MA","세종대학교/MA","세한대학교/MA","우석대학교/BA","우석대학교/MA","우송대학교/MA","을지대학교/MA","장로회신학대학교/MA","제주국제대학교/MA","조선대학교/BA","중원대학교/MA","창신대학교/MA","총신대학교/BA","추계예술대학교/BA","호남대학교/BA","호남대학교/MA","대림대학교/JUNIOR","신구대학교/JUNIOR","신안산대학교/JUNIOR","웅지세무대학교/JUNIOR","한국영상대학교/JUNIOR","부산과학기술대학교/JUNIOR","부산예술대학교/JUNIOR","춘해보건대학교/JUNIOR","경북과학대학교/JUNIOR","구미대학교/JUNIOR","성운대학교/JUNIOR","포항대학교/JUNIOR","거제대학교/JUNIOR","창원문성대학교/JUNIOR","한국승강기대학교/JUNIOR","광주보건대학교/JUNIOR","동강대학교/JUNIOR","광양보건대학교/JUNIOR","동아보건대학교/JUNIOR","제주관광대학교/JUNIOR","제주한라대학교/JUNIOR"]

def dl(url,tries=3):
    for t in range(tries):
        try:
            if 'drive.google' in url:
                m=re.search(r'/file/d/([^/]+)',url) or re.search(r'[?&]id=([^&]+)',url)
                if m: url=f"https://drive.google.com/uc?export=download&id={m.group(1)}"
            return urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=150).read()
        except Exception as e:
            time.sleep(4)
    return None
def safe(s): return re.sub(r'[\\/:*?"<>|]+','',str(s)).strip()

ok=0; fail2=[]
for f in fails:
    nm,lv=f.split('/')
    info=src.get((nm,lv)) or src.get((nm,'BA'))
    if not info: fail2.append(f); continue
    aid,url=info
    data=dl(url)
    if not data or len(data)<1000: fail2.append(f); continue
    en=enmap.get(nm,''); en_part=safe(en)
    parts=[aid or str(900000), safe(nm)]
    if en_part: parts.append(en_part)
    parts.append(lv)
    y=re.search(r'(202[67])',url); year=y.group(1) if y else ''
    if year: parts.append(year)
    term='전기' if '전기' in url else ('후기' if '후기' in url else '')
    if term: parts.append(term)
    fn="_".join(parts)+".pdf"
    open(os.path.join(DEST,fn),'wb').write(data)
    ok+=1; print(f"[OK] {fn}")
    time.sleep(1)
print(f"\n재시도 성공: {ok} | 여전히 실패: {len(fail2)}", fail2[:10])