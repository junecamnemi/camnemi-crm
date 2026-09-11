#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OCR the untrusted (poor/image-text) guide PDFs with rapidocr -> _ocr_text/*.txt.
These feed the DeepSeek V4-Pro re-parse (OCR text was invisible to the original pass)."""
import json, os, glob, sys
import pymupdf, numpy as np
from rapidocr_onnxruntime import RapidOCR

BASE = r"C:\Users\USER\camnemi-crm\backend"
TRUST = os.path.join(BASE, "_llmparse_trust.json")
OUTDIR = os.path.join(BASE, "_ocr_text")
os.makedirs(OUTDIR, exist_ok=True)
UP = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project"

PDF_BY_NAME = {}
for p in glob.glob(os.path.join(UP, "**", "*.pdf"), recursive=True):
    PDF_BY_NAME.setdefault(os.path.basename(p), p)

flagged = json.load(open(TRUST, encoding="utf-8"))["flagged"]
print(f"OCR 대상: {len(flagged)}건")

ocr = RapidOCR()
done = 0
for item in flagged:
    fn = item["file"]
    path = PDF_BY_NAME.get(fn)
    if not path:
        print(f"  skip (no pdf): {fn}"); continue
    outpath = os.path.join(OUTDIR, os.path.splitext(fn)[0] + ".txt")
    if os.path.exists(outpath) and os.path.getsize(outpath) > 100:
        done += 1; continue
    try:
        d = pymupdf.open(path)
        parts = []
        for i in range(len(d)):
            pix = d[i].get_pixmap(dpi=200)
            img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
            if pix.n == 4:
                img = img[:, :, :3]
            res, _ = ocr(img)
            if res:
                parts.append("\n".join(r[1] for r in res))
        d.close()
        txt = "\n".join(parts)
        open(outpath, "w", encoding="utf-8").write(txt)
        print(f"  ✓ {fn}: {len(txt)} chars")
        done += 1
    except Exception as e:
        print(f"  ✗ {fn}: {e}")
print(f"\n완료: {done}/{len(flagged)} → {OUTDIR}")
