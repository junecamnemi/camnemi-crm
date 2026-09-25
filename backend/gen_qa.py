#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate a Q&A consultation KB (profiles) from real cases + official KB, using gpt-6-astra."""
import json, os, re, urllib.request, collections, random

D = r"C:\Users\wisew\visa_qa"; B = r"C:\Users\wisew\camnemi-crm\backend"
def _auth():
    for p in [r"C:\Users\wisew\AppData\Local\hermes\shared\nous_auth.json", r"C:\Users\wisew\AppData\Local\hermes\auth.json"]:
        if not os.path.exists(p): continue
        d = json.load(open(p, encoding="utf-8"))
        if d.get("access_token"): return d.get("inference_base_url") or "https://inference-api.nousresearch.com/v1", d["access_token"]
        n = (d.get("providers") or {}).get("nous") or {}
        if n.get("agent_key"): return n.get("inference_base_url") or "https://inference-api.nousresearch.com/v1", n["agent_key"]
    raise SystemExit("no auth")
BASE, KEY = _auth(); MODEL="openai/gpt-6-astra-pro"

prof = json.load(open(os.path.join(D,"profiles_all.json"), encoding="utf-8"))
kb = json.load(open(os.path.join(B,"visa_kb_kr.json"), encoding="utf-8"))
labor = json.load(open(os.path.join(B,"labor_medical_rights_kr.json"), encoding="utf-8"))

# situation buckets to cover (diverse)
BUCKETS = {
 "E-9 사업장변경·임금체불": ["E-9","사업장","임금"],
 "E-9 퇴직금·출국만기보험": ["E-9","퇴직금","출국만기"],
 "미등록 임금체불 구제": ["미등록","임금"],
 "미등록 의료지원": ["미등록","병원","의료"],
 "산재 신청·보상": ["산재","다쳐","공상"],
 "F-6 결혼이민(이혼·양육)": ["F-6","이혼","양육"],
 "F-4 재외동포 취업제한": ["F-4","취업","단순노무"],
 "F-2 거주자격·연장": ["F-2","거주"],
 "F-5 영주·국적": ["F-5","영주","귀화"],
 "G-1 인도적체류·난민": ["G-1","난민","인도적"],
 "H-2 방문취업": ["H-2","방문취업"],
 "D-2 유학 시간제취업": ["D-2","시간제","아르바이트"],
 "D-4 어학연수": ["D-4","어학"],
 "D-10 구직": ["D-10","구직"],
 "E-7-4 숙련기능인력": ["E-7-4","숙련"],
 "자진출국·입국규제": ["자진출국","불법체류","입국규제"],
 "건강보험·4대보험": ["건강보험","4대보험","보험료"],
 "해고·부당해고": ["해고","부당"],
 "출산·자녀 체류": ["출산","자녀","아이"],
 "재입국·재입국허가": ["재입국"],
}
def cases_for(kws, n=8):
    out=[]
    for p in prof:
        t = p.get("question","") + " " + p.get("answer","") + " " + p.get("visa","")
        if all(any(k.lower() in t.lower() for k in [kw]) for kw in [kws[0]]) and any(k in t for k in kws[1:]):
            out.append(p)
    random.seed(3); random.shuffle(out)
    return out[:n]

PROMPT = """너는 한국 이민·노동 상담 전문가다. 아래 [실제 사례]와 [우리 KB]를 근거로 **상담 Q&A 프로필**을 만들어라.
JSON만 출력(설명 없이):
{"id":"CASE-YYYY-NNN","title":"한 줄 제목",
 "profile":{"체류자격":"","국적":"","상황":"2-3문장","질문":["핵심질문1","핵심질문2","핵심질문3"]},
 "answers":[{"q":"질문","a":"답변(구체적·실행가능)","절차":["1)..","2).."],"근거":"법령·규정","공식출처":["기관"]}],
 "주의":["주의1"],"다음단계":["1345 등"]}
규칙: 실제 사례·KB에 근거한 내용만. 추측 금지. 없으면 "확인 필요"로 표기. 한국어.

[실제 사례]
<<CASES>>

[우리 KB (관련)]
<<KB>>
"""
def build(name, kws, idx):
    cs = cases_for(kws)
    if not cs: return None
    ctext = "\n\n".join(f"[Q{i+1}] {p['question'][:500]}\n[A] {p.get('answer','(답변 없음)')[:400]}" for i,p in enumerate(cs))
    # relevant KB slice
    kbtxt = json.dumps({k:v for k,v in labor.items() if any(w in k for w in kws)}, ensure_ascii=False)[:2500]
    prompt = PROMPT.replace("<<CASES>>", ctext[:8000]).replace("<<KB>>", kbtxt)
    body={"model":MODEL,"messages":[{"role":"user","content":prompt}],"temperature":0,"max_tokens":4000}
    req=urllib.request.Request(BASE.rstrip("/")+"/chat/completions",data=json.dumps(body).encode(),
        headers={"Authorization":f"Bearer {KEY}","Content-Type":"application/json"})
    with urllib.request.urlopen(req,timeout=600) as r: d=json.loads(r.read())
    c=(d["choices"][0]["message"].get("content") or "")
    depth=0; start=None
    for i,ch in enumerate(c):
        if ch=="{":
            if depth==0: start=i
            depth+=1
        elif ch=="}":
            depth-=1
            if depth==0 and start is not None:
                try:
                    o=json.loads(c[start:i+1])
                    if o.get("title"): return o
                except Exception: pass
                start=None
    return None

out=[]
for i,(name,kws) in enumerate(BUCKETS.items()):
    try:
        o = build(name, kws, i)
        if o:
            o["_bucket"]=name; out.append(o)
            print(f"OK  {name} → {o.get('title','')[:50]}")
        else: print(f"MISS {name}")
    except Exception as e:
        print(f"ERR {name}: {str(e)[:60]}")
json.dump(out, open(os.path.join(B,"qa_profiles_kr.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"\n저장: qa_profiles_kr.json ({len(out)}건)")
