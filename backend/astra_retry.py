#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Retry the 2 failed astra consultation topics with robust JSON extraction + merge."""
import json, os, re, urllib.request, collections

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
cons = json.load(open(os.path.join(B,"consultation_kr.json"), encoding="utf-8"))
have = {c.get("topic","")[:20] for c in cons}

# rebuild the groups that failed: E-9 unrelated(기타) and F-6
def topic(q):
    for k in ["임금체불","퇴직금","산재","해고","출국만기","건강보험","의료","최저임금","연차","사업장","체류","자진출국","불법체류","미등록","재입국","가족","초청","주거","월세","학교","자녀"]:
        if k in q: return k
    return "기타"
groups = collections.defaultdict(list)
for p in prof:
    if len(p.get("question",""))>80: groups[(p.get("visa") or "?", topic(p["question"]))].append(p)

PROMPT = """한국 이민·노동 상담사례를 상담용 지식 JSON으로 정리하라. JSON **하나만** 출력(설명·중복 금지).
{"topic":"주제","situation_patterns":[".."],"guidance":"핵심안내(3-5문장)","procedure":[".."],"required_docs":[".."],"legal_basis":[".."],"agencies":[".."],"cautions":[".."],"common_questions":[{"q":"","a":""}]}
실제 사례·법령 근거만. 사례:
"""
def run(items, visa):
    txt = "\n\n".join(f"[사례 {i+1}] Q: {p['question'][:600]}\nA: {p.get('answer','')[:600]}" for i,p in enumerate(items[:12]))
    body={"model":MODEL,"messages":[{"role":"user","content":PROMPT+txt[:14000]}],"temperature":0,"max_tokens":4000}
    req=urllib.request.Request(BASE.rstrip("/")+"/chat/completions",data=json.dumps(body).encode(),
        headers={"Authorization":f"Bearer {KEY}","Content-Type":"application/json"})
    with urllib.request.urlopen(req,timeout=600) as r: d=json.loads(r.read())
    c=(d["choices"][0]["message"].get("content") or "")
    # robust: take first balanced {...}
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
                    if isinstance(o,dict) and o.get("topic"): return o
                except Exception: pass
                start=None
    return None

added=0
for (visa,tp), items in groups.items():
    key=(f"{visa}|{tp}")
    if f"{visa}|{tp}"=="E-9|기타" or (visa=="F-6" and added<2):
        if any(tp[:4] in h for h in have) and visa!="F-6": continue
        print(f"재시도 [{visa}|{tp}] {len(items)}건...")
        try:
            o=run(items, visa)
            if o:
                o["_visa"]=visa; o["_n_cases"]=len(items); cons.append(o); added+=1
                print("  OK:", o.get("topic","")[:50])
            else: print("  parse fail")
        except Exception as e: print("  ERR", str(e)[:60])
json.dump(cons, open(os.path.join(B,"consultation_kr.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"\n총 주제: {len(cons)} (추가 {added})")
