#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Opus 4.8로 표본 요강 분석 → pro(KB)와 비교."""
import json, os, urllib.request, time

def _auth():
    for p in [r'C:\Users\USER\AppData\Local\hermes\shared\nous_auth.json', r'C:\Users\USER\AppData\Local\hermes\auth.json']:
        if os.path.exists(p):
            try: return json.load(open(p,encoding='utf-8'))
            except: pass
    return {}
KEY=_auth().get('access_token') or ''
BASE="https://inference-api.nousresearch.com/v1/chat/completions"
MODEL="anthropic/claude-opus-4.8"

PROMPT="""당신은 한국 대학 외국인(재외국민/외국인) 입학 모집요강 전문 분석가입니다. 주어진 요강 텍스트에서 아래 JSON 구조로 정확히 추출하세요. 텍스트에 없는 항목은 null로 두고 절대 추측하지 마세요.

{"school":"대학명","period":"모집시기(수시/정시/전기/후기/학기)","lang_req":"지원자격 언어 요건(TOPIK급, IELTS, TOEFL, 학교 어학원 등 상세)","topik_req":TOPIK필요급수(정수, 없으면null),"ielts_req":IELTS필요(숫자,없으면null),"toefl_req":TOEFL필요(숫자,없으면null),"tuition_semester":"한 학기 등록금(범위)","scholarships":"장학금(명칭/조건/혜택 요약)","majors_ba":"지원 가능 전공(학과 목록, 있으면 간결히)","apply_system":"입학전형/지원방식(원서/서류/면접 등)","apply_evidence":"제출서류","notes":"중요 특이사항"}

모집요강 텍스트만 기준으로 추출하세요."""

def call(text):
    body={"model":MODEL,"messages":[{"role":"user","content":PROMPT+"\n\n[요강텍스트]\n"+text[:42000]}],"temperature":0,"max_tokens":2500}
    for _ in range(3):
        try:
            req=urllib.request.Request(BASE,data=json.dumps(body).encode(),headers={"Authorization":f"Bearer {KEY}","Content-Type":"application/json"})
            d=json.loads(urllib.request.urlopen(req,timeout=300).read())
            c=d["choices"][0]["message"]["content"]
            # extract JSON
            s=c.find("{"); e=c.rfind("}")
            return json.loads(c[s:e+1]) if s>=0 else {"raw":c[:300]}
        except Exception as ex:
            last=str(ex)[:100]; time.sleep(2)
    return {"error":last}

SAMP=r"C:\Users\USER\camnemi-crm\backend\_opus_sample"
schools=["중앙대학교","성균관대학교","인하대학교","경희대학교","한국외국어대학교","경북대학교","홍익대학교","단국대학교","건국대학교","경기대학교"]
opus={}
for nm in schools:
    fp=os.path.join(SAMP,nm.replace('대학교','')+'.txt')
    if not os.path.exists(fp): continue
    txt=open(fp,encoding='utf-8').read()
    if len(txt)<1000: print(f"{nm}: 텍스트 부족({len(txt)})"); continue
    r=call(txt)
    opus[nm]=r
    print(f"{nm}: school={r.get('school')} topik={r.get('topik_req')} ielts={r.get('ielts_req')} | 튜션={str(r.get('tuition_semester'))[:20]}")
    time.sleep(0.5)
json.dump(opus,open(SAMP+r"\_opus_results.json",'w',encoding='utf-8'),ensure_ascii=False,indent=1)
print("완료:",len(opus))