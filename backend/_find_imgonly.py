#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Find pages where content may be image-only (missing from text layer) and OCR them."""
import pymupdf, numpy as np, io, os, re
from PIL import Image
from rapidocr_onnxruntime import RapidOCR

PDF = r"C:\Users\USER\camnemi-crm\backend\hikorea_manuals\사증민원_매뉴얼.pdf"
d = pymupdf.open(PDF)
ocr = RapidOCR()
cand = []
for i in range(len(d)):
    pg = d[i]
    t = pg.get_text().strip()
    imgs = pg.get_images(full=True)
    if not imgs:
        continue
    # largest image bbox area vs page area
    pa = pg.rect.width * pg.rect.height
    maxfrac = 0.0
    for im in imgs:
        try:
            for r in pg.get_image_rects(im[0]):
                maxfrac = max(maxfrac, (r.width*r.height)/pa)
        except Exception:
            pass
    # candidate: image covers >40% of page OR (image present and text <250 chars)
    if maxfrac > 0.40 or (imgs and len(t) < 250):
        cand.append((i+1, len(t), len(imgs), round(maxfrac,2)))
print(f"누락 후보 페이지: {len(cand)}")
for c in cand[:60]:
    print("  p%-4d text=%-5d imgs=%d cover=%.2f" % c)
json.dump(cand, open(r"C:\Users\USER\camnemi-crm\backend\_imgonly_pages.json","w"), ensure_ascii=False)
