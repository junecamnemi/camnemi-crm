#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Opus scholarship enrichment: for each parsed guide, Opus extracts the FULL
scholarship details (tiers, conditions, benefits) from the source text, replacing
Pro's thin scholarship_note. Output: _opus_scholarships.jsonl
{school, program, year, scholarships: [ {name, condition, benefit} ]}
"""
import os, re, json, urllib.request

BASE = r"C:\Users\USER\camnemi-crm\backend"
PARSED = os.path.join(BASE, "guides_llm_parsed.jsonl")
OUT = os.path.join(BASE, "_opus_scholarships.jsonl")
MODEL = "anthropic/claude-opus-5"

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
BASE_URL, KEY = _auth()

PROMPT = """너는 한국 대학 외국인 모집요강의 장학금 전문 분석가다. 아래 요강 텍스트에서 **장학금 정보만** 추출해 JSON 배열로 출력하라(설명·마크다운 금지):
{"scholarships":[{"name":"장학금명", "condition":"지급조건(TOPIK/IELTS/성적 등)", "benefit":"혜택(수업료 %/금액/기간)"}]}
장학금이 없으면 {"scholarships":[]}. 모든 등급/조건을 빠짐없이 포함하라.

=== 요강 텍스트 ===
"""

def extract_text(path):
    import pymupdf
    doc = pymupdf.open(path)
    t = "".join(doc[i].get_text() for i in range(min(len(doc), 12)))
    doc.close()
    return t

def call(text):
    body = {"model": MODEL, "messages": [{"role": "user", "content": PROMPT + text[:14000]}],
            "max_tokens": 4000, "temperature": 0}
    req = urllib.request.Request(BASE_URL.rstrip("/") + "/chat/completions",
                                 data=json.dumps(body).encode(),
                                 headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        d = json.loads(r.read())
    m = d["choices"][0]["message"]
    return m.get("content") or m.get("reasoning") or ""

def main():
    # read parsed guides that have a source file
    items = []
    for l in open(PARSED, encoding="utf-8"):
        if not l.strip(): continue
        d = json.loads(l)
        f = d.get("_file", "")
        if f:
            items.append(d)
    print(f"장학금 보강 대상: {len(items)}")
    ok = 0
    with open(OUT, "a", encoding="utf-8") as out:
        for d in items:
            f = d.get("_file", "")
            # find the actual path
            path = None
            for prog in ["ba", "ma", "junior", "lang"]:
                for y in ["2026", "2027"]:
                    p = os.path.join(r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project\guides", prog, y, f)
                    if os.path.exists(p):
                        path = p; break
                if path: break
            if not path:
                continue
            try:
                txt = extract_text(path)
                resp = call(txt)
                m = re.search(r'\{.*\}', resp, re.S)
                if not m: continue
                sch = json.loads(m.group(0))
                rec = {"school": d.get("school"), "program": d.get("program"),
                       "year": d.get("year"), "scholarships": sch.get("scholarships", [])}
                out.write(json.dumps(rec, ensure_ascii=False) + "\n")
                ok += 1
            except Exception as e:
                print(f"  ERR: {d.get('school')} {type(e).__name__}")
    print(f"완료: {ok}/{len(items)} 장학금 보강")

if __name__ == "__main__":
    main()
