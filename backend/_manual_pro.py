#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Deep-analysis of 체류민원 매뉴얼 with deepseek-v4-pro (per model policy: pro for deep analysis)."""
import json, os, re, urllib.request, urllib.parse

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
MODEL = "deepseek/deepseek-v4-pro"
MAN = r"C:\Users\wisew\camnemi-crm\backend\hikorea_manuals\체류민원_md.txt"
t = open(MAN, encoding="utf-8").read()

# locate body sections (skip TOC ~0-2000 and index ~23000)
sec = {
 "D-2 (유학)": t.find("유학(D-2)", 25000),
 "D-4 (일반연수)": t.find("일반연수(D-4)", 31000),
 "E-7 (특정활동)": t.find("특정활동(E-7)", 75000),
 "D-10 (구직)": t.find("구직(D-10)", 87000),
}
payload = ""
for k, pos in sec.items():
    payload += f"\n\n########## [{k}] ##########\n" + (t[pos:pos+12000] if pos > 0 else "[미발견]")

PROMPT = """너는 대한민국 법무부 「외국인체류 안내매뉴얼 2026.9」 전문가다. 아래는 D-2(유학)·D-4(일반연수)·E-7(특정활동)·D-10(구직) 본문 발췌다.
유학생 상담에 바로 쓰는 구조화 JSON으로 정리하라. 형식:
{"by_status":[{"status":"","apply_target":"","activity_scope":"","period":"","required_docs":[""],"additional_docs_by_case":[],"work_rights":"","notes":""}]}
규칙: (1) 발췌문에 실제로 나온 내용만. (2) 추측 금지. (3) 표·각주도 반영. (4) required_docs는 서류, additional_docs_by_case는 조건별 추가서류(예: D-4→D-2, 정부초청, 비자심사강화대학 등). (5) work_rights는 근무·활동 관련 규정.

발췌문:
"""
body = {"model": MODEL, "messages":[{"role":"user","content": PROMPT + payload[:70000]}], "temperature":0, "max_tokens":24000}
req = urllib.request.Request(BASE.rstrip("/")+"/chat/completions", data=json.dumps(body).encode(),
        headers={"Authorization":f"Bearer {KEY}","Content-Type":"application/json"})
with urllib.request.urlopen(req, timeout=900) as r:
    d = json.loads(r.read())
m = d["choices"][0]["message"]; c = m.get("content") or m.get("reasoning") or ""
print("model:", d.get("model"), "| finish:", d["choices"][0].get("finish_reason"), "| tokens:", d.get("usage",{}).get("total_tokens"))
out = re.sub(r"^```(json)?|```$","",c.strip(),flags=re.M).strip()
mm = re.search(r"\{.*\}", out, re.S)
data = json.loads(mm.group(0) if mm else out)
dst = r"C:\Users\wisew\camnemi-crm\backend\hikorea_manuals\체류민원_D2D4D10E7_pro.json"
json.dump(data, open(dst,"w",encoding="utf-8"), ensure_ascii=False, indent=1)
print("저장:", dst)
for x in data["by_status"]:
    print(f"\n■ {x['status']}")
    print("  대상:", str(x.get('apply_target'))[:130])
    print("  기간:", str(x.get('period'))[:80])
    docs = x.get('required_docs') or []
    print(f"  서류({len(docs)}):", [s[:45] for s in docs][:8])
    if x.get('additional_docs_by_case'): print("  조건별:", str(x['additional_docs_by_case'])[:150])
    if x.get('work_rights'): print("  활동:", str(x['work_rights'])[:100])
