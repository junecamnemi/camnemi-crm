#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Deep-parse family-invitation financial/GNI requirements from 체류민원 매뉴얼 with deepseek-v4-pro."""
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

MAN = r"C:\Users\USER\camnemi-crm\backend\hikorea_manuals\체류민원_md.txt"
t = open(MAN, encoding="utf-8").read()

# locate family-invitation sections by keywords
anchors = {
    "F-3 동반(활동범위/대상)": "동반(F-3)",
    "D-2 유학생 배우자(F-3)": "유학생(D-2) 배우자(F-3)",
    "F-2-7 동반가족(F-2-71/F-3-18)": "점수제 우수인재(F-2-7)의 배우자",
    "가족초청 소득(주거급여)": "동반가족 초청 소득",
    "후견인(GNI, 21개국)": "후견인",
    "F-5 생계유지(동거가족수)": "생계유지 요건",
    "우수인재 배우자 취업특례": "우수인재 배우자에 대한 자격 외 활동허가의 특례",
}
def find_pos(kw, after=0):
    i = t.find(kw, after)
    return i if i >= 0 else -1

payload = ""
seen = set()
for label, kw in anchors.items():
    pos = find_pos(kw)
    if pos < 0 or pos in seen:
        payload += f"\n\n########## [{label}] [미발견] ##########\n"
        continue
    seen.add(pos)
    chunk = t[pos:pos+12000]
    payload += f"\n\n########## [{label}] ##########\n" + chunk

# also scan for '초청' + '재정/GNI' occurrences elsewhere
payload += "\n\n########## [기타 가족초청·재정 언급] ##########\n"
cnt = 0
for m in re.finditer(r'(가족초청|배우자 및 미성년자녀|동반가족)', t):
    seg = t[max(0,m.start()-120):m.start()+280]
    if ('재정' in seg or '소득' in seg or 'GNI' in seg or '초청' in seg):
        payload += "· " + re.sub(r'[ \t]+',' ', seg)[:340] + "\n"
        cnt += 1
        if cnt >= 40: break

PROMPT = """너는 법무부 「체류민원 자격별 안내매뉴얼 2026.9」 전문가다. 아래는 체류민원 매뉴얼에서 '가족초청·동반가족(F-3/F-2-71/F-3-18/F-5 가족)·재정요건·GNI' 관련 본문 발췌다.
유학생(특히 석사 D-2-3) 상담용으로, 가족초청 재정요건을 구조화 JSON으로 정리하라. 형식:
{"family_invitation_2026":{"by_status":[{"status":"","invitee":"","visa_granted":"","financial_requirement":"","gni_krw":"","docs":[],"caveats":[],"source_section":""}],"gni_2026":52416000,"note":""}}
규칙: (1) 발췌문에 실제로 나온 내용만. (2) 추측·보충 금지. (3) 금액·기간·GNI 배수는 숫자 그대로. (4) '해당 없음/미기재'는 명시. (5) 캄보디아 21개국 해당 여부 표시.
발췌문:
"""

body = {"model": MODEL, "messages":[{"role":"user","content":PROMPT+payload[:65000]}], "temperature":0, "max_tokens":24000}
req = urllib.request.Request(BASE.rstrip("/")+"/chat/completions", data=json.dumps(body).encode(),
        headers={"Authorization":f"Bearer {KEY}","Content-Type":"application/json"})
with urllib.request.urlopen(req, timeout=900) as r:
    d = json.loads(r.read())
m = d["choices"][0]["message"]; c = m.get("content") or m.get("reasoning") or ""
print("model:", d.get("model"), "| finish:", d["choices"][0].get("finish_reason"), "| tokens:", d.get("usage",{}).get("total_tokens"))
out = re.sub(r"^```(json)?|```$","",c.strip(),flags=re.M).strip()
mm = re.search(r"\{.*\}", out, re.S)
data = json.loads(mm.group(0) if mm else out)
OUT = r"C:\Users\USER\camnemi-crm\backend\hikorea_manuals\가족초청_재정요건_pro.json"
json.dump(data, open(OUT,"w",encoding="utf-8"), ensure_ascii=False, indent=1)
print("saved", OUT)
print(json.dumps(data, ensure_ascii=False)[:1500])
