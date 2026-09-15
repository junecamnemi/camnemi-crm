#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate remaining Q&A profiles with deepseek-v4-pro (astra credits exhausted)."""
import json, os, re, urllib.request, random

D = r"C:\Users\USER\visa_qa"; B = r"C:\Users\USER\camnemi-crm\backend"
def _auth():
    for p in [r"C:\Users\USER\AppData\Local\hermes\shared\nous_auth.json", r"C:\Users\USER\AppData\Local\hermes\auth.json"]:
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

BUCKETS = {
 "F-4 재외동포 취업제한": ["F-4","취업","단순노무","재외동포"],
 "H-2 방문취업": ["H-2","방문취업"],
 "D-2 유학 시간제취업": ["D-2","시간제","아르바이트","유학"],
 "D-4 어학연수": ["D-4","어학","연수"],
 "D-10 구직": ["D-10","구직"],
 "E-7-4 숙련기능인력": ["E-7-4","숙련","점수제"],
 "자진출국·입국규제": ["자진출국","불법체류","입국규제","범칙금"],
 "건강보험·4대보험": ["건강보험","4대보험","보험료","연금"],
 "해고·부당해고": ["해고","부당","권고사직"],
 "출산·자녀·난민": ["출산","자녀","난민","아이","F-1-8"],
 "재입국·재입국허가": ["재입국","출국","복수사증"],
 "E-7 취업·직종": ["E-7","특정활동","직종"],
 "F-5 영주 요건": ["F-5","영주","영주권"],
 "결혼이민 F-6": ["F-6","결혼","국적"],
}
def cases_for(kws, n=8):
    out=[]
    for p in prof:
        t = (p.get("question","") + " " + p.get("answer","") + " " + p.get("visa","")).lower()
        if any(k.lower() in t for k in kws): out.append(p)
    random.seed(5); random.shuffle(out)
    return out[:n]

PROMPT = """너는 한국 이민·노동 상담 전문가다. [실제 사례]·[우리 KB]를 근거로 상담 Q&A 프로필 JSON만 출력.
{"id":"CASE-2026-NNN","title":"한줄","profile":{"체류자격":"","국적":"","상황":"2-3문장","질문":["q1","q2","q3"]},
 "answers":[{"q":"질문","a":"구체·실행가능 답변","절차":["1).."],"근거":"법령·규정","공식출처":["기관"]}],
 "주의":[".."],"다음단계":["1345 등"]}
규칙: 근거 있는 내용만. 없으면 "확인 필요(1345)". 추측 금지. 한국어.
[실제 사례]
<<CASES>>
[우리 KB]
<<KB>>
"""
def build(kws):
    cs = cases_for(kws)
    if not cs: return None
    ctext = "\n\n".join(f"[Q{i+1}] {p['question'][:500]}\n[A] {p.get('answer','(답변없음)')[:400]}" for i,p in enumerate(cs))
    kb_ = json.dumps({k:v for k,v in list(labor.items())+list(kb.get("che_statuses",{}).items()) if any(w in str(k) for w in kws)} , ensure_ascii=False)[:2500]
    prompt = PROMPT.replace("<<CASES>>", ctext[:7000]).replace("<<KB>>", kb_)
    body={"model":MODEL,"messages":[{"role":"user","content":prompt}],"temperature":0,"max_tokens":24000}
    req=urllib.request.Request(BASE.rstrip("/")+"/chat/completions",data=json.dumps(body).encode(),
        headers={"Authorization":f"Bearer {KEY}","Content-Type":"application/json"})
    with urllib.request.urlopen(req,timeout=600) as r: d=json.loads(r.read())
    m=d["choices"][0]["message"]; c=(m.get("content") or "")+"\n"+(m.get("reasoning") or "")
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
        o=build(kws)
        if o: o["_bucket"]=name; out.append(o); print(f"OK  {name} → {o.get('title','')[:55]}")
        else: print(f"MISS {name}")
    except Exception as e: print(f"ERR {name}: {str(e)[:60]}")
json.dump(out, open(os.path.join(B,"qa_profiles_kr2.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"\n저장 (2차): {len(out)}건")
