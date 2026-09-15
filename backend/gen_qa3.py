#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Retry failed buckets (transient 502/520) with astra, then merge all Q&A profiles."""
import json, os, re, urllib.request, random, time

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

FAILED = {
 "H-2 방문취업": ["H-2","방문취업","동포"],
 "D-2 유학 시간제취업": ["D-2","시간제","아르바이트","유학생"],
 "D-4 어학연수": ["D-4","어학","연수"],
 "자진출국·입국규제": ["자진출국","입국규제","범칙금","강제퇴거"],
 "출산·자녀·난민": ["출산","자녀","난민","F-1-8","아이"],
 "재입국·재입국허가": ["재입국","재입국허가"],
}
def cases_for(kws, n=8):
    out=[]
    for p in prof:
        t=(p.get("question","")+" "+p.get("answer","")+" "+p.get("visa","")).lower()
        if any(k.lower() in t for k in kws): out.append(p)
    random.seed(9); random.shuffle(out); return out[:n]
PROMPT = """한국 이민·노동 상담 전문가로서 [실제 사례]·[우리 KB] 근거로 상담 Q&A 프로필 JSON만 출력.
{"id":"CASE-2026-NNN","title":"한줄","profile":{"체류자격":"","국적":"","상황":"2-3문장","질문":["q1","q2","q3"]},
 "answers":[{"q":"","a":"구체·실행가능","절차":["1).."],"근거":"법령","공식출처":["기관"]}],"주의":[".."],"다음단계":["1345"]}
※키는 다음단계. 근거있는 내용만, 없으면 "확인 필요(1345)". 추측 금지. 한국어.
[실제 사례]
<<CASES>>
[우리 KB]
<<KB>>
"""
def build(kws):
    cs=cases_for(kws)
    if not cs: return None
    ctext="\n\n".join(f"[Q{i+1}] {p['question'][:500]}\n[A] {p.get('answer','(답변없음)')[:400]}" for i,p in enumerate(cs))
    kb_=json.dumps({k:v for k,v in list(labor.items())+list(kb.get("che_statuses",{}).items()) if any(w in str(k) for w in kws)}, ensure_ascii=False)[:2500]
    prompt=PROMPT.replace("<<CASES>>",ctext[:7000]).replace("<<KB>>",kb_)
    body={"model":MODEL,"messages":[{"role":"user","content":prompt}],"temperature":0,"max_tokens":4000}
    for t in range(4):
        try:
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
        except Exception as e:
            if t==3: print(f"  {str(e)[:50]}"); return None
            time.sleep(5)

# merge existing
b1 = json.load(open(os.path.join(B,"qa_profiles_kr.json"), encoding="utf-8"))
b2 = json.load(open(os.path.join(B,"qa_profiles_kr2.json"), encoding="utf-8"))
have = {x.get("_bucket") for x in b1+b2}
print("기존:", len(b1), "+", len(b2), "=", len(b1)+len(b2))
new=[]
for name,kws in FAILED.items():
    if name in have: continue
    print(f"재시도 {name}...")
    try:
        o=build(kws)
        if o: o["_bucket"]=name; new.append(o); print("  OK", o.get("title","")[:50])
        else: print("  fail")
    except Exception as e: print("  ERR", str(e)[:50])
allq = b1+b2+new
# renumber ids
for i,x in enumerate(allq): x["id"]=f"CASE-2026-{i+1:03d}"
json.dump(allq, open(os.path.join(B,"qa_profiles_kr.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(new, open(os.path.join(B,"qa_profiles_kr2.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"\n최종 Q&A 프로필: {len(allq)}건")
for x in allq: print(f"  [{x['id']}] {x.get('title','')[:60]}")
