#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate a polished visa-manual PDF via gpt-6-astra (content) + pymupdf (render)."""
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

# load extracted knowledge
pro = json.load(open(r"C:\Users\USER\camnemi-crm\backend\hikorea_manuals\체류민원_D2D4D10E7_pro.json", encoding="utf-8"))
toc = open(r"C:\Users\USER\camnemi-crm\backend\hikorea_manuals\260901 사증민원 자격별 안내 매뉴얼.txt", encoding="utf-8").read()[:1500] if os.path.exists(r"C:\Users\USER\camnemi-crm\backend\hikorea_manuals\260901 사증민원 자격별 안내 매뉴얼.txt") else "(목차 미확보)"

knowledge = f"[사증민원 매뉴얼 목차]\n{toc}\n\n[체류민원 매뉴얼 pro 분석 (D-2/D-4/D-10/E-7)]\n{json.dumps(pro, ensure_ascii=False)[:12000]}"

PROMPT = f"""너는 법무부 출입국·외국인정책본부의 비자 안내 전문가다. 아래 지식을 바탕으로 **유학생·취업자를 위한 한국 체류/사증 민원 안내**를 마크다운 문서로 작성하라.
문서는 상담원(캄보디아 유학생 상담)이 바로 쓰는 실무 가이드여야 한다.
표와 불릿을 적극 사용하고, 3~4페이지 분량으로.
마지막에 "최종 판단은 출입국·외국인청(1345) 확인 필요" 명시.

지식:
{knowledge}

마크다운 문서만 출력:"""
body = {"model": "openai/gpt-6-astra-pro", "messages":[{"role":"user","content":PROMPT}], "temperature":0.3, "max_tokens":20000}
req = urllib.request.Request(BASE.rstrip("/")+"/chat/completions", data=json.dumps(body).encode(),
        headers={"Authorization":f"Bearer {KEY}","Content-Type":"application/json"})
with urllib.request.urlopen(req, timeout=900) as r:
    d = json.loads(r.read())
m = d["choices"][0]["message"]; md = m.get("content") or m.get("reasoning") or ""
print("model:", d.get("model"), "| tokens:", d.get("usage",{}).get("total_tokens"), "| len:", len(md))

# render to PDF
import pymupdf
doc = pymupdf.open()
page = doc.new_page(width=595, height=842)
KFONT = r"C:\Windows\Fonts\malgun.ttf"
page.insert_font(fontname="KR", fontfile=KFONT)
y = 40
first = True
for line in md.split("\n"):
    s = line.rstrip()
    if not s.strip():
        y += 8; continue
    size, bold, color = 10, False, (0,0,0)
    if s.startswith("## "): size, bold, color = 15, True, (0,0,120)
    elif s.startswith("### "): size, bold, color = 13, True, (0,0,120)
    elif s.startswith("#### "): size, bold, color = 12, True, (0,0,0)
    elif s.startswith("- ") or s.startswith("* "): size = 10
    if first:
        page.insert_text((40, 40), "Camnemi Visa Guide - 사증·체류 민원 안내 (법무부 기준 2026.9)", fontname="KR", fontsize=16, color=(0,0,120))
        y = 68; first = False
    tw = pymupdf.get_text_length(s, fontname="KR", fontsize=size) if hasattr(pymupdf,"get_text_length") else size*len(s)
    if tw > 515:
        words = s.split(" ")
        line2 = ""; 
        for w in words:
            test = (line2+" "+w).strip()
            if pymupdf.get_text_length(test, fontname="KR", fontsize=size) > 515:
                page.insert_text((40, y), line2, fontname="KR", fontsize=size, color=color); y += size+3
                line2 = w
            else:
                line2 = test
        if line2: page.insert_text((40, y), line2, fontname="KR", fontsize=size, color=color); y += size+3
    else:
        page.insert_text((40, y), s, fontname="KR", fontsize=size, color=color); y += size+3
    if y > 800:
        page = doc.new_page(width=595, height=842); page.insert_font(fontname="KR", fontfile=KFONT); y = 40
OUT = r"C:\Users\USER\camnemi-crm\backend\hikorea_manuals\사증체류_민원_안내_astra.pdf"
doc.save(OUT)
print("PDF:", OUT, os.path.getsize(OUT), "bytes,", len(doc), "pages")
