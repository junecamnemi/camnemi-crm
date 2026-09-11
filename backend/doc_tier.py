#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""doc_tier.py — document quality classifier + text extractor (ARCHITECTURE §2).

Assigns every guide PDF one of five tiers and returns its text:
  A  rich    text >= 5000 chars            -> extract with T1 (flash)
  B  medium  1000..5000                    -> T1, escalate on verify-fail
  C  poor    200..1000  (after OCR try)    -> T2 (pro)
  D  image   < 200      (after OCR try)    -> T2 (pro), discard if OCR < 30
  E  nondoc  screenshot/web-capture        -> REJECT -> re-collect queue

Usage:
  python doc_tier.py <folder-or-file> [--ocr]
"""
import os, re, sys, glob, json, argparse

MIN = {"A": 5000, "B": 1000, "C": 200}
NONDOC_PAT = re.compile(r"렌더|캡처|capture", re.I)
NONDOC_BODY = re.compile(r"jsessionid|AllRightsReserved|Copyright\s*20|https?://[^\s]+\.do", re.I)

_OCR = None
def get_ocr():
    global _OCR
    if _OCR is None:
        from rapidocr_onnxruntime import RapidOCR
        _OCR = RapidOCR()
    return _OCR

def _ocr_pdf(path, dpi=200):
    import pymupdf, numpy as np
    d = pymupdf.open(path)
    ocr = get_ocr()
    parts = []
    for i in range(len(d)):
        pix = d[i].get_pixmap(dpi=dpi)
        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
        if pix.n == 4:
            img = img[:, :, :3]
        res, _ = ocr(img)
        if res:
            parts.append("\n".join(r[1] for r in res))
    d.close()
    return "\n".join(parts)

def classify(path, allow_ocr=True):
    """Return dict: {path, tier, text, text_len, ocr_used, reason}."""
    name = os.path.basename(path)
    if NONDOC_PAT.search(name):
        return {"path": path, "tier": "E", "text": "", "text_len": 0, "ocr_used": False,
                "reason": "filename looks like a web capture (렌더/캡처)"}
    import pymupdf
    try:
        d = pymupdf.open(path)
        text = "\n".join(d[i].get_text() for i in range(len(d)))
        d.close()
    except Exception as e:
        return {"path": path, "tier": "E", "text": "", "text_len": 0, "ocr_used": False,
                "reason": f"unreadable: {e}"}
    clean = re.sub(r"[\s\x00-\x1f]+", " ", text)
    n = len(clean.strip())

    # E: body looks like a web page rather than a guide
    if NONDOC_BODY.search(clean) and n < 6000:
        return {"path": path, "tier": "E", "text": clean, "text_len": n, "ocr_used": False,
                "reason": "body looks like a website capture (url/copyright dominant)"}

    if n >= MIN["A"]:
        return {"path": path, "tier": "A", "text": clean, "text_len": n, "ocr_used": False, "reason": "rich text"}
    if n >= MIN["B"]:
        return {"path": path, "tier": "B", "text": clean, "text_len": n, "ocr_used": False, "reason": "medium text"}

    # low text -> try OCR
    if allow_ocr:
        try:
            ocr_text = re.sub(r"[\s\x00-\x1f]+", " ", _ocr_pdf(path))
            m = len(ocr_text.strip())
            if m >= MIN["B"]:
                return {"path": path, "tier": "B", "text": ocr_text, "text_len": m, "ocr_used": True, "reason": "OCR recovered (medium)"}
            if m >= MIN["C"]:
                return {"path": path, "tier": "C", "text": ocr_text, "text_len": m, "ocr_used": True, "reason": "OCR recovered (poor)"}
            return {"path": path, "tier": "D", "text": ocr_text, "text_len": m, "ocr_used": True, "reason": "image-only; OCR minimal"}
        except Exception as e:
            return {"path": path, "tier": "D", "text": clean, "text_len": n, "ocr_used": False, "reason": f"OCR failed: {e}"}
    tier = "C" if n >= MIN["C"] else "D"
    return {"path": path, "tier": tier, "text": clean, "text_len": n, "ocr_used": False, "reason": "low text (ocr off)"}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target")
    ap.add_argument("--ocr", action="store_true", help="allow OCR for low-text PDFs (slow)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    files = sorted(glob.glob(os.path.join(a.target, "*.pdf"))) if os.path.isdir(a.target) else [a.target]
    rows = [classify(f, allow_ocr=a.ocr) for f in files]
    if a.json:
        print(json.dumps([{k: v for k, v in r.items() if k != "text"} for r in rows], ensure_ascii=False, indent=1))
        return
    from collections import Counter
    c = Counter(r["tier"] for r in rows)
    print(f"총 {len(rows)}개 | 등급 분포: {dict(sorted(c.items()))}")
    for r in rows:
        print(f"  [{r['tier']}] {os.path.basename(r['path'])[:48]:48s} len={r['text_len']:>7} ocr={int(r['ocr_used'])} {r['reason'][:38]}")

if __name__ == "__main__":
    main()
