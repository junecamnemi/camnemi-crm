#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""전체 요강 Opus 4.8 분석 — fetch + Opus 추출, JSONL 이어하기."""
import json, os, re, time, urllib.request
import pymupdf

OUT=r"C:\Users\USER\camnemi-crm\backend\_opus_full.jsonl"
LOG=r"C:\Users\USER\camnemi-crm\backend\_opus_full_log.txt"
UA={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/131.0.0.0 Safari/537.36'}

def _auth():
    for p in [r'C:\Users\USER\AppData\Local\hermes\shared\nous_auth.json', r'C:\Users\USER\AppData\Local\hermes\auth.json']:
        if os.path.exists(p):
            try: return json.load(open(p,encoding='utf-8'))
            except: pass
    return {}
KEY=_auth().get('access_token') or ''
BASE="https://inference-api.nousresearch.com/v1/chat/completions"
MODEL="anthropic/claude-opus-4.8"

PROMPT="""당신은 한국 대학 외국인(재외국민/외국인) 입학 모집요강 전문 분석가입니다. 주어진 요강 텍스트에서 아래 JSON 구조로 정확히 추출하세요. 텍스트에 없는 항목은 null로 두고 절대 추측하지 마세요. 특히 장학금과 지원시스템은 최대한 상세히.

{"school":"대학명","level":"ba/ma/junior/lang","period":"모집시기","lang_req":"지원자격 언어요건(TOPIK/IELTS/TOEFL/어학원 상세)","topik_req":TOPIK필요급수정수,"ielts_req":IELTS숫자,"toefl_req":TOEFL숫자,"tuition_semester":"한 학기 등록금 범위","scholarships":"장학금(명칭/조건/혜택 전부 상세히)","majors":"지원가능 전공","apply_system":"전형/평가방식 상세(서류/면접/실기 비율 등)","apply_evidence":"제출서류 전체","notes":"특이사항"}"""

def dl_gdrive(url):
    m=re.search(r'/file/d/([^/]+)',url)
    if not m: return None
    try:
        dl=f"https://drive.google.com/uc?export=download&id={m.group(1)}"
        return urllib.request.urlopen(urllib.request.Request(dl,headers=UA),timeout=60).read()
    except: return None
def dl(url):
    try:
        if 'drive.google' in url: return dl_gdrive(url)
        return urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=60).read()
    except: return None
def pdftext(data):
    try:
        d=pymupdf.open(stream=data,filetype="pdf")
        return "\n".join(p.get_text() for p in d)
    except: return ""
def call(text):
    body={"model":MODEL,"messages":[{"role":"user","content":PROMPT+"\n\n[요강]\n"+text[:45000]}],"temperature":0,"max_tokens":3000}
    for _ in range(3):
        try:
            req=urllib.request.Request(BASE,data=json.dumps(body).encode(),headers={"Authorization":f"Bearer {KEY}","Content-Type":"application/json"})
            d=json.loads(urllib.request.urlopen(req,timeout=300).read())
            c=d["choices"][0]["message"]["content"]
            s=c.find("{"); e=c.rfind("}")
            return json.loads(c[s:e+1]) if s>=0 else {"raw":c[:200]}
        except Exception as ex:
            last=str(ex)[:80]; time.sleep(3)
    return {"error":last}

def load_done():
    done={}
    if os.path.exists(OUT):
        for l in open(OUT,encoding='utf-8'):
            if l.strip():
                r=json.loads(l); done[(r['school'],r['level'])]=r
    return done

# source: _guide_2027_master (BA + MA, 최신 요강)
B=r"C:\Users\USER\camnemi-crm\backend"
m=json.load(open(B+r"\_guide_2027_master.json",encoding='utf-8'))
sources=[]
for x in m:
    for lv in ["ba","ma"]:  # lang/junior는 나중에
        u=x.get(f"{lv}_url")
        if u and "http" in u:
            sources.append((x["school"], lv, u))

done=load_done()
f=open(OUT,'a',encoding='utf-8')
log=open(LOG,'a',encoding='utf-8')
n=0
for school,level,url in sources:
    if (school,level) in done: continue
    data=dl(url); txt=pdftext(data) if data else ""
    if len(txt)<800:
        msg=f"[skip] {school}/{level}: 텍스트 부족 {len(txt)}"
        log.write(msg+"\n"); log.flush(); continue
    r=call(txt)
    r["school"]=school; r["level"]=level; r["url"]=url
    f.write(json.dumps(r,ensure_ascii=False)+"\n"); f.flush()
    n+=1
    log.write(f"[ok] {school}/{level}: topik={r.get('topik_req')} ielts={r.get('ielts_req')} | {len(txt)}자\n"); log.flush()
    print(f"[{n}] {school}/{level} ok", flush=True)
    time.sleep(0.3)
f.close(); log.close()
print("완료. 새로 분석:", n)