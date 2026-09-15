#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the 일자리(취업) 매뉴얼 KB — 외국인 유학생 취업 전 경로, pro 구조화."""
import json, os, re, urllib.request

def _auth():
    for p in [r"C:\Users\USER\AppData\Local\hermes\shared\nous_auth.json", r"C:\Users\USER\AppData\Local\hermes\auth.json"]:
        if not os.path.exists(p): continue
        d = json.load(open(p, encoding="utf-8"))
        if d.get("access_token"):
            return d.get("inference_base_url") or "https://inference-api.nousresearch.com/v1", d["access_token"]
        n = (d.get("providers") or {}).get("nous") or {}
        if n.get("agent_key"):
            return n.get("inference_base_url") or "https://inference-api.nousresearch.com/v1", n["agent_key"]
    raise SystemExit("no auth")
BASE, KEY = _auth(); MODEL="deepseek/deepseek-v4-pro"
B = r"C:\Users\USER\camnemi-crm\backend"; HM=os.path.join(B,"hikorea_manuals")
che = open(os.path.join(HM,"체류민원_md.txt"), encoding="utf-8").read()
saj = open(os.path.join(HM,"사증민원_매뉴얼_전체.txt"), encoding="utf-8").read()

def g(t,key,start,n=9000):
    p=t.find(key,start); return t[p:p+n] if p>0 else f"[{key} 없음]"

payload = "\n\n".join([
 "### [체류] 시간제취업 활동 허가\n"+g(che,"시간제취업 활동 허가",27000,13000),
 "### [체류] E-7 특정활동\n"+g(che,"특정활동(E-7)",76000,9000),
 "### [체류] D-10 구직\n"+g(che,"구직(D-10)",87000,8000),
 "### [체류] E-9 비전문취업\n"+g(che,"비전문취업(E-9)",100000,6000),
 "### [사증] E-7 허용직종\n"+g(saj,"허용직종",15000,12000),
 "### [사증] E-7-4 숙련기능인력\n"+g(saj,"숙련기능인력(E-7-4)",10,9000),
])

PROMPT = """너는 법무부 출입국 자료 전문가다. 아래 발췌로 **외국인 유학생 「일자리 매뉴얼」**용 데이터를 구조화하라.
출력 JSON:
{"time_parttime":{"basic_principle":"","target":"","allowed_hours":[{"process":"","korean_req":"","weekday":"","weekend_vacation":"","certified":"","english_track":""}],
  "start_by_status":{"D-2":"","D-4":""},"period_place":{"D-2":"","D-4":""},
  "restricted_fields":[],"exceptions":[],"required_docs":[],"violation_penalty":[]},
 "employment_paths":[{"from":"","to":"","condition":"","income":"","note":""}],
 "e7_fields":"","e7_4_skilled":{"target":"","requirement":"","quota":""},
 "key_notes":[]}
규칙: 발췌문에 실제 있는 내용만, 추측 금지. 없으면 빈 문자열/빈배열. JSON만.
발췌:
"""
body={"model":MODEL,"messages":[{"role":"user","content":PROMPT+payload[:80000]}],"temperature":0,"max_tokens":24000}
req=urllib.request.Request(BASE.rstrip("/")+"/chat/completions",data=json.dumps(body).encode(),
    headers={"Authorization":f"Bearer {KEY}","Content-Type":"application/json"})
with urllib.request.urlopen(req,timeout=1500) as r: d=json.loads(r.read())
m=d["choices"][0]["message"]; c=m.get("content") or m.get("reasoning") or ""
print("tokens:", d.get("usage",{}).get("total_tokens"))
o=re.sub(r"^```(json)?|```$","",c.strip(),flags=re.M).strip()
mm=re.search(r"\{.*\}",o,re.S); data=json.loads(mm.group(0) if mm else o)
json.dump(data, open(os.path.join(B,"job_manual_kr.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
print("저장: job_manual_kr.json")
print("시간제취업 허용시간 행:", len(data.get("time_parttime",{}).get("allowed_hours",[])))
print("취업경로:", [x.get("from")+"→"+x.get("to") for x in data.get("employment_paths",[])])
print("제한분야:", len(data.get("time_parttime",{}).get("restricted_fields",[])))
