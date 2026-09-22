#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OCR the 33 image-only guide PDFs (no text layer) with RapidOCR, then parse
with DeepSeek V4-Pro. Appends to guides_llm_parsed.jsonl.
"""
import os, re, json, io, urllib.request
import pymupdf, numpy as np
from PIL import Image
from rapidocr_onnxruntime import RapidOCR

BASE = r"C:\Users\USER\camnemi-crm\backend"
UP = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project"
PARSED = os.path.join(BASE, "guides_llm_parsed.jsonl")
MODEL = "deepseek/deepseek-v4-pro"

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

PROMPT = """한국 대학 외국인 모집요강 텍스트에서 정보를 추출해 JSON만 출력하세요(설명·마크다운 금지):
{"school":"대학명(한글)", "program":"ba|ma|lang|junior", "year":"2026|2027|unknown",
 "period":"원서접수 기간(문자열)", "topik":TOPIK최소급수 숫자 또는 null, "ielts":IELTS최소 숫자 또는 null,
 "toefl":TOEFL최소 숫자 또는 null, "majors":["모집학과 전체 목록"],
 "tuition_note":"등록금 관련 한 줄 요약",
 "scholarships":[{"name":"장학금명", "condition":"지급조건(TOPIK/IELTS/성적 등)", "benefit":"혜택(수업료 %/금액/기간)"}]}

장학금 추출 규칙: 요강에 나온 모든 장학금 등급/조건/혜택을 배열로 추출. 없으면 [].
중요: OCR 텍스트에 실제 적힌 내용만 추출. 없는 값은 null(추측 금지).

=== 모집요강 텍스트 (OCR) ===
"""

def school_from(f):
    m = re.search(r'([가-힣A-Za-z]+(?:대학교|대학|전문대학|교육원))', f)
    return m.group(1) if m else f

def find_image_pdfs():
    """Find guide PDFs with no text layer (image-only) not yet parsed."""
    parsed_schools = set()
    if os.path.exists(PARSED):
        for l in open(PARSED, encoding="utf-8"):
            if l.strip():
                try: parsed_schools.add(json.loads(l).get("school", ""))
                except Exception: pass
    out = []
    for prog in ["ba", "ma", "junior", "lang"]:
        for y in ["2026", "2027"]:
            d = os.path.join(UP, "guides", prog, y)
            if not os.path.isdir(d): continue
            for f in os.listdir(d):
                if not f.endswith(".pdf"): continue
                s = school_from(f)
                if s in parsed_schools: continue
                path = os.path.join(d, f)
                try:
                    doc = pymupdf.open(path)
                    t = "".join(doc[i].get_text() for i in range(min(len(doc), 3)))
                    doc.close()
                    if len(t.strip()) < 50:  # image-only
                        out.append((path, prog, y, s))
                except Exception:
                    pass
    return out

def ocr_pdf(path, ocr):
    doc = pymupdf.open(path)
    texts = []
    for i in range(min(len(doc), 12)):
        pix = doc[i].get_pixmap(matrix=pymupdf.Matrix(2.5, 2.5))
        img = np.array(Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB"))
        res, _ = ocr(img)
        if res:
            texts.append("\n".join(r[1] for r in res))
    doc.close()
    return "\n".join(texts)

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
    items = find_image_pdfs()
    print(f"이미지 PDF(미파싱): {len(items)}")
    from collections import Counter
    print("레벨별:", Counter(p for _, p, _, _ in items))
    if not items:
        print("없음"); return
    ocr = RapidOCR()
    ok = 0
    with open(PARSED, "a", encoding="utf-8") as out:
        for path, prog, year, school in items:
            try:
                txt = ocr_pdf(path, ocr)
                if len(txt.strip()) < 30:
                    print(f"  SKIP(OCR부족): {school}")
                    continue
                resp = call(txt)
                m = re.search(r'\{.*\}', resp, re.S)
                if not m:
                    print(f"  FAIL(no json): {school}")
                    continue
                d = json.loads(m.group(0))
                d["_file"] = os.path.basename(path)
                d["_prog_hint"] = prog
                d["_year_hint"] = year
                d["_ocr"] = True
                out.write(json.dumps(d, ensure_ascii=False) + "\n")
                ok += 1
                print(f"  OK: {school} [{prog}] OCR {len(txt)}자")
            except Exception as e:
                print(f"  ERR: {school} {type(e).__name__}")
    print(f"완료: {ok}/{len(items)}")

if __name__ == "__main__":
    main()
