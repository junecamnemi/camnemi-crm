#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Evaluate the trilingual translator: EN→KM (kiripost pairs) + KO→KM (dict) with pro-judge."""
import json, os, re, sys, random, urllib.request, csv

K = r"C:\Users\USER\khmer"; N = r"C:\Users\USER\khmer_news"; B = r"C:\Users\USER\camnemi-crm\backend"
def _auth():
    for p in [r"C:\Users\USER\AppData\Local\hermes\shared\nous_auth.json", r"C:\Users\USER\AppData\Local\hermes\auth.json"]:
        if not os.path.exists(p): continue
        d = json.load(open(p, encoding="utf-8"))
        if d.get("access_token"): return d.get("inference_base_url") or "https://inference-api.nousresearch.com/v1", d["access_token"]
        n = (d.get("providers") or {}).get("nous") or {}
        if n.get("agent_key"): return n.get("inference_base_url") or "https://inference-api.nousresearch.com/v1", n["agent_key"]
    raise SystemExit("no auth")
BASE, KEY = _auth(); MODEL="deepseek/deepseek-v4-pro"

sys.path.insert(0, B)
import translate_kr as TR

def kh_ratio(t): return sum(1 for c in (t or "") if '\u1780'<=c<='\u17ff')/max(1,len(t or ""))
def tok_overlap(ref, hyp):
    def toks(s): return set(re.findall(r"[\u1780-\u17ff]+|[A-Za-z]+", (s or "").lower()))
    a,b = toks(ref), toks(hyp)
    return len(a&b)/max(1,len(a)) if a else 0.0

def judge(src, ref, hyp, direction):
    prompt = f"""번역 품질 평가. [원문]과 [참조번역]을 기준으로 [번역]의 정확도를 평가하라.
JSON만: {{"score":0-100,"verdict":"정확|부분|오역|비번역","reason":"한문장"}}
[원문] {src}
[참조번역] {ref}
[번역] {hyp}
방향: {direction}"""
    body={"model":MODEL,"messages":[{"role":"user","content":prompt}],"temperature":0,"max_tokens":24000}
    req=urllib.request.Request(BASE.rstrip("/")+"/chat/completions",data=json.dumps(body).encode(),
        headers={"Authorization":f"Bearer {KEY}","Content-Type":"application/json"})
    with urllib.request.urlopen(req,timeout=300) as r: d=json.loads(r.read())
    m=d["choices"][0]["message"]; c=(m.get("content") or "")+"\n"+(m.get("reasoning") or "")
    mm=re.search(r"\{[^{}]*score[^{}]*\}", c, re.S)
    if mm:
        try: return json.loads(mm.group(0))
        except Exception: pass
    return {"score":0,"verdict":"?","reason":"parse"}

# test sets
tests=[]
pd=os.path.join(N,"pairs")
for f in os.listdir(pd) if os.path.isdir(pd) else []:
    if f.endswith(".json"):
        for x in json.load(open(os.path.join(pd,f),encoding="utf-8")):
            if len(x.get("en",""))>80 and len(x.get("km",""))>40:
                tests.append(("en","km",x["en"][:400],x["km"][:400]))
# KO→KM from dict (limited)
kk=[]
p=os.path.join(K,"km_ko_dict.jsonl")
for line in open(p,encoding="utf-8"):
    try:
        o=json.loads(line)
        if o.get("ko") and o.get("km") and len(o["ko"])>3: kk.append((o["ko"],o["km"]))
    except Exception: pass
random.seed(1); random.shuffle(kk)
for ko,km in kk[:10]: tests.append(("ko","km",ko,km))

random.seed(2); random.shuffle(tests); tests=tests[:22]
print(f"평가 셋: {len(tests)}건")

res=[]
for frm,to,src,ref in tests:
    try:
        o,_ = TR.translate(src, to=to, frm=frm)
        hyp=o.get("translation","")
    except Exception as e:
        hyp=""; 
    ov=tok_overlap(ref,hyp); kr=kh_ratio(hyp)
    try: j=judge(src,ref,hyp,f"{frm.upper()}→{to.upper()}")
    except Exception as e: j={"score":0,"verdict":"ERR","reason":str(e)[:40]}
    res.append({"from":frm,"to":to,"src":src[:150],"ref":ref[:150],"hyp":hyp[:150],
                "overlap":round(ov,3),"khmer_ratio":round(kr,3),"score":j.get("score",0),"verdict":j.get("verdict"),"reason":j.get("reason","")})
    print(f"  [{frm}→{to}] {j.get('verdict'):5} score={j.get('score'):3} ov={ov:.2f} | {src[:40]}")

import statistics as st
sc=[r["score"] for r in res if isinstance(r["score"],(int,float))]
ov=[r["overlap"] for r in res]
kr=[r["khmer_ratio"] for r in res if r["to"]=="km"]
print(f"\n■ 평가 결과 ({len(res)}건)")
print(f"  평균 점수(pro 판정): {st.mean(sc):.1f}" if sc else "  점수 없음")
print(f"  토큰 중첩(ref): {st.mean(ov)*100:.1f}%")
if kr: print(f"  크메르 문자 비율: {st.mean(kr)*100:.1f}%")
from collections import Counter
print("  판정 분포:", dict(Counter(r["verdict"] for r in res)))
json.dump(res, open(os.path.join(B,"translation_eval.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
print("저장: translation_eval.json")
