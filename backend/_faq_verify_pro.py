#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verify visa_faq_kr.json (20 Q&A) against 체류민원 매뉴얼 with deepseek-v4-pro."""
import json, os, re, time, urllib.request

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

B = r"C:\Users\wisew\camnemi-crm\backend"
faq = json.load(open(os.path.join(B, "_faq_items.json"), encoding="utf-8"))
MAN = open(os.path.join(B, "hikorea_manuals", "체류민원_md.txt"), encoding="utf-8").read()
KB = open(os.path.join(B, "visa_kb_kr.json"), encoding="utf-8").read()

# manual sections relevant to FAQ topics
anchors = {
    "시간제취업": ["시간제취업 활동 허가", "체류자격외 활동"],
    "불법체류/범칙금": ["불법체류", "범칙금"],
    "자진출국": ["자진출국", "출국권고"],
    "가족초청/F-3": ["동반(F-3)", "유학생(D-2) 배우자(F-3)", "방문동거(F-1)"],
    "D-4→D-2": ["체류자격 변경허가", "어학연수(D-4)"],
    "E-7": ["특정활동(E-7)"],
    "F-5 영주": ["영주(F-5)"],
    "F-6 이혼": ["혼인단절", "결혼이민(F-6)"],
    "재입국": ["재입국허가"],
    "체류기간연장": ["체류기간 연장허가"],
    "체류기간만료": ["출국기한 유예"],
    "E-9": ["비전문취업(E-9)", "사업장변경"],
    "난민": ["난민"],
    "건강보험": ["건강보험"],
    "퇴직금/보험": ["퇴직금", "출국만기보험"],
    "체류자격변경": ["체류자격 변경허가"],
}
ctx = {}
for label, kws in anchors.items():
    parts = []
    for kw in kws:
        i = MAN.find(kw)
        if i >= 0:
            parts.append(MAN[i:i+3500])
    if parts:
        ctx[label] = re.sub(r'[ \t]+',' ', " / ".join(parts))[:9000]

faq_block = "\n\n".join(
    f"### Q{i}. {f['q']}\n답변: {f['a']}\n근거: {'; '.join(f['src'])}" for i, f in enumerate(faq, 1))

kb_head = KB[:2500]
all_results = []
for batch_idx in range(0, len(faq), 10):
    batch = faq[batch_idx:batch_idx+10]
    batch_block = "\n\n".join(
        f"### Q{i}. {f['q']}\n답변: {f['a']}\n근거: {'; '.join(f['src'])}" for i, f in enumerate(batch, batch_idx+1))
    PROMPT = f"""너는 법무부 「체류민원 자격별 안내매뉴얼 2026.9」 전문가다. 아래는 비자 FAQ Q&A {batch_idx+1}~{batch_idx+len(batch)}번과 매뉴얼 발췌, KB 요약이다.
각 답변이 매뉴얼·법령과 일치하는지 검증하라. 규칙:
(1) 매뉴얼/법령에 없는 내용·과장·오류를 잡아라.
(2) 수치(시간·금액·기간·배수)가 틀리면 정확히 고쳐라.
(3) 정확하면 OK, 수정 필요하면 CORRECT + 수정된 답변.
(4) 근거가 없으면 UNVERIFIED.
출력 JSON만 반환:
{{"results":[{{"n":<번호>,"status":"OK|CORRECT|UNVERIFIED","issue":"간단히","corrected_answer":"CORRECT일 때만 전체 수정답변","note":""}}]}}

### FAQ ###
{batch_block}

### 매뉴얼 발췌 ###
{json.dumps(ctx, ensure_ascii=False)[:22000]}

### KB ###
{kb_head}
"""
    body = {"model": MODEL, "messages":[{"role":"user","content":PROMPT}], "temperature":0, "max_tokens":14000}
    req = urllib.request.Request(BASE.rstrip("/")+"/chat/completions", data=json.dumps(body).encode(),
            headers={"Authorization":f"Bearer {KEY}","Content-Type":"application/json"})
    d = None
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req, timeout=600) as r:
                d = json.loads(r.read())
            break
        except Exception as e:
            print(f"[batch{batch_idx//10} retry {attempt+1}] {e}")
            time.sleep(25)
    if d is None:
        print(f"[batch{batch_idx//10}] FAILED"); continue
    m = d["choices"][0]["message"]; c = m.get("content") or m.get("reasoning") or ""
    print(f"[batch{batch_idx//10}] tokens:", d.get("usage",{}).get("total_tokens"))
    out = re.sub(r"^```(json)?|```$","",c.strip(),flags=re.M).strip()
    mm = re.search(r"\{.*\}", out, re.S)
    try:
        data = json.loads(mm.group(0) if mm else out)
        all_results += data["results"]
    except Exception as e:
        print(f"[batch{batch_idx//10}] parse fail: {e}")

data = {"results": all_results, "_note": "pro 검증 (deepseek-v4-pro) 2026-09-16"}
json.dump(data, open(os.path.join(B,"_faq_verify_pro.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
for r in all_results:
    flag = {"OK":"✅","CORRECT":"⚠️","UNVERIFIED":"❓"}.get(r["status"],"•")
    print(f"\n{flag} Q{r['n']}: {r['status']} — {r.get('issue','')[:90]}")
    if r.get("corrected_answer"): print(f"   수정: {r['corrected_answer'][:180]}")
