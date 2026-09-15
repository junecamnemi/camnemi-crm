#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Full deep analysis of the 체류민원 매뉴얼 (39 statuses) via deepseek-v4-pro, chunked + merged."""
import json, os, re, urllib.request, concurrent.futures as cf

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
BASE, KEY = _auth()
MODEL = "deepseek/deepseek-v4-pro"
B = r"C:\Users\USER\camnemi-crm\backend"
t = open(os.path.join(B,"hikorea_manuals","체류민원_md.txt"), encoding="utf-8").read()

# chunk by ~42000 chars on line boundaries
lines = t.split("\n")
chunks, cur, n = [], [], 0
for ln in lines:
    cur.append(ln); n += len(ln)+1
    if n >= 42000:
        chunks.append("\n".join(cur)); cur, n = [], 0
if cur: chunks.append("\n".join(cur))
print("청크:", len(chunks), "개")

PROMPT = """너는 법무부 「외국인체류 안내매뉴얼 2026.9」 전문가다. 아래 발췌에서 등장하는 **각 체류자격**별 정보를 구조화 JSON으로 뽑아라.
형식: {"statuses":[{"code":"","name":"","target":"","duration":"","required_docs":[],"activities":"","notes":""}]}
규칙: (1) 발췌문에 실제 있는 내용만. (2) 추측·일반상식 금지. (3) 자격코드(A-1~H-2 등) 그대로. (4) 서류는 bullet별로 분리. (5) 해당 정보 없으면 빈 문자열/빈 배열. (6) JSON만 출력.
발췌:
"""
def work(idx_chunk):
    idx, ch = idx_chunk
    body = {"model": MODEL, "messages":[{"role":"user","content":PROMPT+ch}], "temperature":0, "max_tokens":24000}
    req = urllib.request.Request(BASE.rstrip("/")+"/chat/completions", data=json.dumps(body).encode(),
            headers={"Authorization":f"Bearer {KEY}","Content-Type":"application/json"})
    try:
        with urllib.request.urlopen(req, timeout=1500) as r:
            d = json.loads(r.read())
        m = d["choices"][0]["message"]; c = m.get("content") or m.get("reasoning") or ""
        o = re.sub(r"^```(json)?|```$","",c.strip(),flags=re.M).strip()
        mm = re.search(r"\{.*\}", o, re.S)
        return idx, json.loads(mm.group(0) if mm else o)
    except Exception as e:
        return idx, {"_err": str(e)[:120]}

res = {}
with cf.ThreadPoolExecutor(max_workers=6) as ex:
    for idx, data in ex.map(work, list(enumerate(chunks))):
        res[idx] = data
        print(f"  chunk {idx+1}/{len(chunks)}: {len(data.get('statuses',[]))} statuses" + (" ERR" if "_err" in data else ""))

# merge by code
merged = {}
for idx in sorted(res):
    for s in res[idx].get("statuses", []):
        code = (s.get("code") or "").strip()
        if not code: continue
        if code not in merged:
            merged[code] = s
        else:
            for dk in ("required_docs","notes"):
                if s.get(dk):
                    if isinstance(merged[code].get(dk), list) and isinstance(s[dk], list):
                        merged[code][dk] = merged[code][dk] + [x for x in s[dk] if x not in merged[code][dk]]
                    elif not merged[code].get(dk):
                        merged[code][dk] = s[dk]
            for f in ("name","target","duration","activities"):
                if not merged[code].get(f) and s.get(f): merged[code][f] = s[f]
out = {"_meta":{"title":"한국 체류자격 전체 심층분석","source":"법무부 외국인체류 안내매뉴얼 2026.9","statuses":len(merged)},
       "statuses":merged}
json.dump(out, open(os.path.join(B,"visa_체류_전체분석_pro.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"\n✅ 병합: {len(merged)}개 자격 → visa_체류_전체분석_pro.json")
print("코드:", sorted(merged.keys()))
