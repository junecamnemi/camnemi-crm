#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Debug: inspect the raw response for a failing file (finish=length)."""
import os, json, re, urllib.request
import pymupdf

def _auth():
    d = json.load(open(r"C:\Users\USER\AppData\Local\hermes\shared\nous_auth.json", encoding="utf-8"))
    return d["access_token"], d["inference_base_url"].rstrip("/")

KEY, BASE = _auth()
F = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project\adiga_2026_전문대학_모집요강\real\국제대학교_전문학사_외국인모집요강.pdf"

d = pymupdf.open(F)
txt = re.sub(r"[\s\x00-\x1f]+", " ", "\n".join(d[i].get_text() for i in range(len(d))))
d.close()
print("text_len:", len(txt))

PROMPT = """한국 대학 외국인 모집요강 텍스트에서 정보를 추출해 JSON만 출력하세요(설명 금지):
{"school":"대학명(한글)", "program":"ba|ma|lang|junior", "year":"2026|2027|unknown",
 "period":"원서접수 기간", "topik":TOPIK최소급수 또는 null, "ielts":IELTS최소 또는 null,
 "toefl":TOEFL최소 또는 null, "majors":["모집학과 전체"],
 "tuition_note":"등록금 한 줄", "scholarship_note":"장학금 한 줄"}
중요: 텍스트에 실제로 적힌 값만. 없으면 null (추측 금지).

=== 모집요강 텍스트 ===
"""
for model, mt in [("deepseek/deepseek-v4-flash-0731", 8000), ("deepseek/deepseek-v4-pro", 20000)]:
    body = {"model": model, "messages": [{"role": "user", "content": PROMPT + txt[:14000]}],
            "temperature": 0, "max_tokens": mt}
    req = urllib.request.Request(BASE + "/chat/completions", data=json.dumps(body).encode(),
        headers={"Authorization": "Bearer " + KEY, "Content-Type": "application/json"})
    try:
        j = json.loads(urllib.request.urlopen(req, timeout=300).read().decode())
        ch = (j.get("choices") or [{}])[0]
        msg = ch.get("message") or {}
        print(f"\n=== {model} (max_tokens={mt}) ===")
        print(" finish_reason:", ch.get("finish_reason"))
        print(" content len:", len(msg.get("content") or ""), "| reasoning len:", len(msg.get("reasoning_content") or ""))
        print(" msg keys:", list(msg.keys()))
        print(" usage:", json.dumps(j.get("usage", {}), ensure_ascii=False)[:250])
        print(" content head:", (msg.get("content") or "")[:200])
    except Exception as e:
        print(f"\n=== {model} ERROR:", str(e)[:150])
