#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""COMBINED analysis: 사증민원(비자 발급, 해외) + 체류민원(국내 변경) as ONE connected flow.
Focus statuses: D-2, D-4, D-10, E-7 (+ D-4→D-2 change path). Model: deepseek-v4-pro.
"""
import json, os, re, urllib.request

def _auth():
    for p in [r"C:\Users\USER\AppData\Local\hermes\shared\nous_auth.json", r"C:\Users\USER\AppData\Local\hermes\auth.json"]:
        if not os.path.exists(p): continue
        d = json.load(open(p, encoding="utf-8"))
        if isinstance(d, dict) and d.get("access_token"):
            return d.get("inference_base_url") or "https://inference-api.nousresearch.com/v1", d["access_token"]
        n = (d.get("providers") or {}).get("nous") or {}
        if n.get("agent_key"):
            return n.get("inference_base_url") or "https://inference-api.nousresearch.com/v1", n["agent_key"]
    raise SystemExit("no auth")
BASE, KEY = _auth()
MODEL = "deepseek/deepseek-v4-pro"
HM = r"C:\Users\USER\camnemi-crm\backend\hikorea_manuals"

saj = open(os.path.join(HM,"사증민원_매뉴얼_전체.txt"), encoding="utf-8").read()
che = open(os.path.join(HM,"체류민원_md.txt"), encoding="utf-8").read()

# --- 사증민원: D-2 / D-4 / E-7 / D-10 발급 본문 ---
def grabt(t, key, start, n=11000):
    p = t.find(key, start)
    return t[p:p+n] if p > 0 else f"[{key} 미발견]"

saj_parts = "\n\n".join([
  "### [사증] D-2(유학)\n"+grabt(saj,"유학(D-2)",50000),
  "### [사증] D-4(일반연수)\n"+grabt(saj,"일반연수(D-4)",58000),
  "### [사증] E-7(특정활동)\n"+grabt(saj,"특정활동(E-7)",40000),
  "### [사증] D-10(구직)\n"+grabt(saj,"구직(D-10)",107000),
])

# --- 체류민원: 자격별 본문 (D-2/D-4/D-10/E-7) ---
che_parts = "\n\n".join([
  "### [체류] D-2(유학)\n"+grabt(che,"유학(D-2)",30000),
  "### [체류] D-4(일반연수)\n"+grabt(che,"일반연수(D-4)",60000),
  "### [체류] E-7(D-4-6 수료생 특례)\n"+grabt(che,"특정활동(E-7)",76000),
  "### [체류] D-10(구직)\n"+grabt(che,"구직(D-10)",87000),
])

PROMPT = """너는 법무부 출입국·외국인정책본부 자료 전문가다. 아래는 두 매뉴얼 발췌다:
[A] 사증민원 자격별 안내 매뉴얼 (2026.9) — **해외에서 비자(사증) 발급** 절차·서류
[B] 체류민원 자격별 안내 매뉴얼 (2026.9) — **한국 입국 후 체류자격 변경·체류허가** 절차·서류

핵심: 사증발급(해외) → 입국 → 체류자격 변경(국내)은 **연결된 하나의 흐름**이다. 이를 통합해 정리하라.

출력 JSON:
{"flow_note":"사증과 체류의 연결 설명(1-2문장)",
 "statuses":[{"status":"D-2 유학","sajeung_issuance":{"target":"","required_docs":[],"by_case":[]},
   "domestic_change":{"allowed_from":[],"restricted_from":[],"required_docs":[],"period":"","activities":""},
   "connection":"발급→변경 연결 요점"}]}

규칙: (1) 발췌문에 실제 있는 내용만, 추측 금지. (2) D-4→D-2 변경 경로를 반드시 포함. (3) 어학연수(D-4) 관련 서류 우선. (4) 비면책: 해당없으면 "발췌문에 없음".

발췌문:
"""
payload = f"===== [A] 사증민원 (해외 비자 발급) =====\n{saj_parts}\n\n===== [B] 체류민원 (국내 변경) =====\n{che_parts}"
body = {"model": MODEL, "messages":[{"role":"user","content":PROMPT+payload[:90000]}], "temperature":0, "max_tokens":24000}
req = urllib.request.Request(BASE.rstrip("/")+"/chat/completions", data=json.dumps(body).encode(),
        headers={"Authorization":f"Bearer {KEY}","Content-Type":"application/json"})
with urllib.request.urlopen(req, timeout=1500) as r:
    d = json.loads(r.read())
m=d["choices"][0]["message"]; c=m.get("content") or m.get("reasoning") or ""
print("model:", d.get("model"), "| finish:", d["choices"][0].get("finish_reason"), "| tokens:", d.get("usage",{}).get("total_tokens"))
out = re.sub(r"^```(json)?|```$","",c.strip(),flags=re.M).strip()
mm = re.search(r"\{.*\}", out, re.S)
data = json.loads(mm.group(0) if mm else out)
json.dump(data, open(os.path.join(HM,"사증_체류_통합분석_pro.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
print("flow:", str(data.get("flow_note"))[:200])
for x in data.get("statuses",[]):
    print(f"\n■ {x['status']}")
    si=x.get('sajeung_issuance',{}); dc=x.get('domestic_change',{})
    print("  [사증] 대상:", str(si.get('target'))[:110])
    print("  [사증] 서류:", [s[:40] for s in (si.get('required_docs') or [])][:6])
    print("  [체류] 허용:", str(dc.get('allowed_from'))[:130])
    print("  [체류] 제한:", str(dc.get('restricted_from'))[:110])
    print("  [연결]:", str(x.get('connection'))[:150])
