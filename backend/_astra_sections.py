#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extract D-2 / D-4 / D-10 / E-7 sections from the manual text and structure them with astra."""
import json, os, re, urllib.request

def _auth():
    for p in [r"C:\Users\wisew\AppData\Local\hermes\shared\nous_auth.json", r"C:\Users\wisew\AppData\Local\hermes\auth.json"]:
        if not os.path.exists(p): continue
        d = json.load(open(p, encoding="utf-8"))
        if isinstance(d, dict) and d.get("access_token"):
            return d.get("inference_base_url") or "https://inference-api.nousresearch.com/v1", d["access_token"]
        n = (d.get("providers") or {}).get("nous") or {}
        if n.get("agent_key"):
            return n.get("inference_base_url") or "https://inference-api.nousresearch.com/v1", n["agent_key"]
    raise SystemExit("no auth")

BASE, KEY = _auth()
MODEL = "openai/gpt-6-astra-pro"
TXT = r"C:\Users\wisew\camnemi-crm\backend\hikorea_manuals\체류민원_md.txt"
t = open(TXT, encoding="utf-8").read()
print("전체 길이:", len(t))

# locate key sections
anchors = {"D-2": ["10. 유학(D-2)", "유학(D-2)"], "D-4": ["12. 일반연수(D-4)", "일반연수(D-4)"],
           "D-10": ["18. 구직(D-10)", "구직(D-10)"], "E-7": ["25. 특정활동(E-7)", "특정활동(E-7)"]}
chunks = {}
for k, pats in anchors.items():
    pos = -1
    for p in pats:
        pos = t.find(p)
        if pos > 0: break
    if pos > 0:
        chunks[k] = t[pos:pos+9000]
        print(f"  {k}: pos {pos}")
    else:
        print(f"  {k}: 못 찾음")

payload = "\n\n##########\n".join(f"[{k} 섹션]\n{v}" for k, v in chunks.items())
PROMPT = """다음은 법무부 「외국인체류 안내매뉴얼 2026.9」에서 발췌한 D-2(유학)·D-4(일반연수)·D-10(구직)·E-7(특정활동) 부분이다.
유학생 상담용으로 구조화하라. JSON only.

형식:
{"by_status":[
 {"status":"D-2 (유학)","purpose":"","apply_target":"","period":"","required_docs":["..."],"notes":""},
 {"status":"D-4 (일반연수)", ...},
 {"status":"D-10 (구직)", ...},
 {"status":"E-7 (특정활동)", ...}
]}

규칙: 발췌문에 실제로 나온 내용만. 없으면 빈 문자열/빈 배열. 추측 금지.

발췌문:
"""
body = {"model": MODEL, "messages":[{"role":"user","content": PROMPT + payload[:60000]}], "temperature":0, "max_tokens":16000}
req = urllib.request.Request(BASE.rstrip("/")+"/chat/completions", data=json.dumps(body).encode(),
        headers={"Authorization":f"Bearer {KEY}","Content-Type":"application/json"})
with urllib.request.urlopen(req, timeout=900) as r:
    d = json.loads(r.read())
m = d["choices"][0]["message"]; c = m.get("content") or m.get("reasoning") or ""
print("model:", d.get("model"), "| finish:", d["choices"][0].get("finish_reason"), "| tokens:", d.get("usage",{}).get("total_tokens"))
out = re.sub(r"^```(json)?|```$","",c.strip(),flags=re.M).strip()
mm = re.search(r"\{.*\}", out, re.S)
data = json.loads(mm.group(0) if mm else out)
dst = r"C:\Users\wisew\camnemi-crm\backend\hikorea_manuals\체류민원_D2D4D10E7_astra.json"
json.dump(data, open(dst,"w",encoding="utf-8"), ensure_ascii=False, indent=1)
print("저장:", dst)
for x in data.get("by_status", []):
    print(f"\n■ {x.get('status')} | 목적:{x.get('purpose')} | 대상:{(x.get('apply_target') or '')[:70]}")
    print(f"   기간: {x.get('period')}")
    print(f"   서류: {x.get('required_docs')}")
    if x.get('notes'): print(f"   비고: {str(x.get('notes'))[:200]}")
