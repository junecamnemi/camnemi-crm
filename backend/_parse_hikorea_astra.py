#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Parse the HiKorea 민원서식 page with openai/gpt-6-astra-pro into a structured form catalog."""
import json, os, re, urllib.request

def _auth():
    for p in [r"C:\Users\USER\AppData\Local\hermes\shared\nous_auth.json",
              r"C:\Users\USER\AppData\Local\hermes\auth.json"]:
        if not os.path.exists(p):
            continue
        d = json.load(open(p, encoding="utf-8"))
        if isinstance(d, dict) and d.get("access_token"):
            return d.get("inference_base_url") or "https://inference-api.nousresearch.com/v1", d["access_token"]
        n = (d.get("providers") or {}).get("nous") or {}
        if n.get("agent_key"):
            return n.get("inference_base_url") or "https://inference-api.nousresearch.com/v1", n["agent_key"]
    raise SystemExit("no auth")

BASE, KEY = _auth()
MODEL = "openai/gpt-6-astra-pro"

PAGE = r"C:\Users\USER\AppData\Local\hermes\profiles\univ\cache\web\www.hikorea.go.kr-2eccf79a99.md"
raw = open(PAGE, encoding="utf-8").read()
# strip the markdown image/link noise -> keep the form names
txt = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", raw)
txt = re.sub(r"\(https?://[^)]*#this\)", "", txt)
txt = re.sub(r"\n{2,}", "\n", txt)

PROMPT = """다음은 하이코리아(HiKorea) '민원서식' 페이지 텍스트다.
서식 목록을 정확히 추출해 JSON으로만 답하라. 형식:
{"forms":[{"name":"서식명","category":"체류/사증/취업/유학/기타","filetypes":["hwp","pdf"],"note":""}]}

규칙:
- 페이지에 실제로 나온 서식만 (추측 금지)
- filetypes는 서식명 옆에 붙은 확장자 아이콘(hwp/pdf/doc/docx)만
- category는 페이지 구분(체류 관련 등) 또는 서식 성격으로
- 유학/어학연수 관련 서식은 note에 표시

페이지 텍스트:
"""

body = {"model": MODEL, "messages": [{"role": "user", "content": PROMPT + txt[:60000]}],
        "temperature": 0, "max_tokens": 16000}
req = urllib.request.Request(BASE.rstrip("/") + "/chat/completions",
                            data=json.dumps(body).encode(),
                            headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
with urllib.request.urlopen(req, timeout=600) as r:
    d = json.loads(r.read())
msg = d["choices"][0]["message"]
content = msg.get("content") or msg.get("reasoning") or ""
usage = d.get("usage", {})
print("model:", d.get("model"), "| finish:", d["choices"][0].get("finish_reason"), "| tokens:", usage.get("total_tokens"))
out = re.sub(r"^```(json)?|```$", "", content.strip(), flags=re.M).strip()
m = re.search(r"\{.*\}", out, re.S)
data = json.loads(m.group(0) if m else out)
json.dump(data, open(os.path.join(os.path.dirname(PAGE).replace("web","web"), "..", "..", "..", "hikorea_forms.json") if False else r"C:\Users\USER\camnemi-crm\backend\hikorea_forms.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("서식 수:", len(data.get("forms", [])))
for f in data.get("forms", [])[:40]:
    print(f"  [{f.get('category','?')}] {f['name']}  {f.get('filetypes')}")
