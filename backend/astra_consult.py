#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build a consultation-ready KB from real counseling cases using gpt-6-astra (deep analysis)."""
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
BASE, KEY = _auth()
MODEL = "openai/gpt-6-astra-pro"   # 사용자 지시: 'astra' = gpt-6-astra

prof = json.load(open(os.path.join(D,"profiles_all.json"), encoding="utf-8"))
kb = json.load(open(os.path.join(B,"visa_kb_kr.json"), encoding="utf-8"))
labor = json.load(open(os.path.join(B,"labor_medical_rights_kr.json"), encoding="utf-8"))

# group cases by visa + topic keyword for astra analysis
def topic(q):
    for k in ["임금체불","퇴직금","산재","해고","출국만기","건강보험","의료","최저임금","연차","사업장","체류","자진출국","불법체류","미등록","재입국","가족","초청"]:
        if k in q: return k
    return "기타"
groups = collections.defaultdict(list)
for p in prof:
    if len(p.get("question",""))>80:
        groups[(p.get("visa") or "?", topic(p["question"]))].append(p)
print("그룹:", len(groups))

# pick top groups
top = sorted(groups.items(), key=lambda x:-len(x[1]))[:12]

PROMPT = """너는 한국 이민·노동 상담 전문가다. 아래는 실제 상담사례(질문+공식 답변) 모음이다.
이를 바탕으로 **상담용 지식**을 JSON으로 정리하라. 봇이 실제 상담에서 바로 쓸 수 있게.
출력 JSON:
{"topic":"주제","situation_patterns":["전형적 상황1","상황2"],
 "guidance":"핵심 안내(3-5문장)",
 "procedure":["절차1","절차2"],
 "required_docs":["서류1"],
 "legal_basis":["근거법령"],
 "agencies":["담당기관·연락처"],
 "cautions":["주의사항"],
 "common_questions":[{"q":"자주 묻는 질문","a":"답변"}]}
규칙: 실제 사례·법령에 근거한 내용만. 추측 금지. JSON만 출력.
사례:
"""
res=[]
for (visa,tp), items in top:
    txt = "\n\n".join(f"[사례 {i+1}] Q: {p['question'][:600]}\nA: {p.get('answer','')[:600]}" for i,p in enumerate(items[:10]))
    body={"model":MODEL,"messages":[{"role":"user","content":PROMPT+txt[:14000]}],"temperature":0,"max_tokens":4000}
    try:
        req=urllib.request.Request(BASE.rstrip("/")+"/chat/completions",data=json.dumps(body).encode(),
            headers={"Authorization":f"Bearer {KEY}","Content-Type":"application/json"})
        with urllib.request.urlopen(req,timeout=600) as r: d=json.loads(r.read())
        msg=d["choices"][0]["message"]; c=(msg.get("content") or "")+"\n"+(msg.get("reasoning") or "")
        m=re.search(r"\{.*\}", c, re.S)
        data=json.loads(m.group(0)) if m else {}
        data["_visa"]=visa; data["_n_cases"]=len(items)
        res.append(data)
        print(f"OK  [{visa}|{tp}] {len(items)}건 → {data.get('topic','')[:40]}")
    except Exception as e:
        print(f"MISS [{visa}|{tp}] {str(e)[:70]}")
json.dump(res, open(os.path.join(B,"consultation_kr.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"\n저장: consultation_kr.json ({len(res)}개 주제)")
