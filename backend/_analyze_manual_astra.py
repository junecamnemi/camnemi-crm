#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Analyze the HiKorea 체류민원 매뉴얼 (extracted text) with openai/gpt-6-astra-pro."""
import json, os, re, urllib.request

def _auth():
    for p in [r"C:\Users\wisew\AppData\Local\hermes\shared\nous_auth.json",
              r"C:\Users\wisew\AppData\Local\hermes\auth.json"]:
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
MAN = r"C:\Users\wisew\camnemi-crm\backend\hikorea_manuals\260901 체류민원 자격별 안내 매뉴얼.txt"
txt = open(MAN, encoding="utf-8").read()
print("매뉴얼 텍스트 길이:", len(txt))

PROMPT = """다음은 법무부 출입국·외국인정책본부의 「체류민원 자격별 안내 매뉴얼」(2026.9)에서 추출한 텍스트다.
이를 분석해 **유학생 상담에 바로 쓸 수 있는 구조화 데이터**로 정리하라. JSON only.

형식:
{
 "manual": "체류민원 자격별 안내 매뉴얼 2026.9",
 "common": {"적용대상":"", "체류기간부여기준":"", "신청시기":"", "수수료":"", "제출처":""},
 "by_status": [
   {"status":"D-2 (유학)", "purpose":"", "period":"", "required_docs":[], "notes":"", "income_or_financial":""},
   {"status":"D-4 (일반연수)", ...},
   {"status":"D-10 (구직)", ...},
   {"status":"E-7 (특정활동)", ...}
 ],
 "key_rules_for_consulting": ["..."],
 "caution": "원문에 없는 내용은 쓰지 말 것"
}

규칙: 텍스트에 실제로 나온 내용만. 추측 금지. 유학/어학(D-2·D-4·D-10)과 취업(E-7·E-9) 관련을 우선.

텍스트:
"""
body = {"model": MODEL, "messages":[{"role":"user","content": PROMPT + txt[:90000]}], "temperature":0, "max_tokens":18000}
req = urllib.request.Request(BASE.rstrip("/")+"/chat/completions", data=json.dumps(body).encode(),
        headers={"Authorization":f"Bearer {KEY}","Content-Type":"application/json"})
with urllib.request.urlopen(req, timeout=900) as r:
    d = json.loads(r.read())
m = d["choices"][0]["message"]
c = m.get("content") or m.get("reasoning") or ""
print("model:", d.get("model"), "| finish:", d["choices"][0].get("finish_reason"), "| tokens:", d.get("usage",{}).get("total_tokens"))
out = re.sub(r"^```(json)?|```$","",c.strip(),flags=re.M).strip()
mm = re.search(r"\{.*\}", out, re.S)
data = json.loads(mm.group(0) if mm else out)
dst = r"C:\Users\wisew\camnemi-crm\backend\hikorea_manuals\체류민원_매뉴얼_분석_astra.json"
json.dump(data, open(dst,"w",encoding="utf-8"), ensure_ascii=False, indent=1)
print("저장:", dst)
print(json.dumps(data, ensure_ascii=False, indent=1)[:1500])
