#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OCR the 33 image-only guide PDFs (no text layer) with RapidOCR, then parse
with DeepSeek V4-Pro. Appends to guides_llm_parsed.jsonl.
"""
import os, re, json, io, urllib.request
import pymupdf, numpy as np
from PIL import Image
from rapidocr_onnxruntime import RapidOCR

BASE = os.path.dirname(os.path.abspath(__file__))
import sys as _sys
_sys.path.insert(0, BASE)
import pipeline_paths as _pp  # ONE library root + ONE data home
import parse_unparsed_pro as _pro  # hardened model path: 32k budget, nudge, safe_json, backoff
UP = str(_pp.drive_root())
# OCR records MUST land in the OCR file: the merge treats guides_llm_parsed.jsonl as
# trusted only when the source PDF has >=1000 chars of text, which image-only PDFs do not.
PARSED = str(_pp.path("parsed_ocr"))
MODEL = "deepseek/deepseek-v4-pro"

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
    # Dedupe by school + level + year, not school alone: an image-only 2027 guide must
    # still be OCR-parsed when the same school already has a 2026 parse.
    parsed_keys = set()
    for _src in (PARSED, str(_pp.path("parsed")), str(_pp.path("parsed_real"))):
        if not os.path.exists(_src):
            continue
        for l in open(_src, encoding="utf-8"):
            if not l.strip():
                continue
            try:
                row = json.loads(l)
                parsed_keys.add((school_from(row.get("school", "")),
                                 (row.get("_prog_hint") or row.get("program") or ""),
                                 str(row.get("_year_hint") or row.get("year") or "")))
            except Exception:
                pass
    out = []
    for prog in ["ba", "ma", "junior", "lang"]:
        for y in ["2026", "2027"]:
            d = os.path.join(UP, "guides", prog, y)
            if not os.path.isdir(d): continue
            for f in os.listdir(d):
                if not f.endswith(".pdf"): continue
                s = school_from(f)
                if (s, prog, y) in parsed_keys or (s, prog, "unknown") in parsed_keys: continue
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
    """Delegate to the hardened parser path in parse_unparsed_pro.

    The local copy used max_tokens 4000 and parsed `reasoning` as the answer, so every
    OCR run failed the same way (reasoning-only reply, invalid JSON) -- 2026-09-29.
    """
    return _pro.call(text, prompt=PROMPT)

def verify_claims(d, text):
    """Drop score claims that do not appear in the OCR text.

    Garbled poster OCR leaves the model free to invent plausible numbers: 경민대 claimed
    TOPIK 2 / IELTS 4.5 while its OCR text showed only "TOPIK ()" (2026-09-29). A claim is
    kept only when the source text carries the number next to the requirement name.
    """
    dropped = []
    for field, pat in (("topik", r"(?:TOPIK|토픽)[^0-9]{0,15}(\d)"),
                       ("ielts", r"(?:IELTS|아이엘츠)[^0-9]{0,15}(\d+(?:\.\d+)?)"),
                       ("toefl", r"(?:TOEFL|토플)[^0-9]{0,15}(\d+)")):
        val = d.get(field)
        if val in (None, "", 0):
            continue
        m = re.search(pat, text or "", re.I)
        src = m.group(1) if m else None
        ok = False
        if src is not None:
            try:
                ok = abs(float(src) - float(val)) < 0.01
            except (TypeError, ValueError):
                ok = str(src) == str(val)
        if not ok:
            d[field] = None
            dropped.append(field)
    if dropped:
        d["_unverified_dropped"] = dropped
    return d


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
                    # Distinguish a broken file from an unreadable one so neither is
                    # silently counted as "no text layer" (2026-09-29).
                    try:
                        _doc = pymupdf.open(path); _pages = _doc.page_count; _doc.close()
                    except Exception:
                        _pages = -1
                    why = "BROKEN(0 pages)" if _pages <= 0 else "OCR부족"
                    print(f"  SKIP({why}): {school}")
                    continue
                resp = call(txt)
                d = _pro.safe_json(resp)
                if d is None:
                    print(f"  FAIL(no json): {school}")
                    continue
                d = verify_claims(d, txt)
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
