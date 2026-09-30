#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OCR the 4 candidate pages to recover image-only content missing from the text layer."""
import pymupdf, numpy as np, io, json
from PIL import Image
from rapidocr_onnxruntime import RapidOCR

PDF = r"C:\Users\wisew\camnemi-crm\backend\hikorea_manuals\사증민원_매뉴얼.pdf"
d = pymupdf.open(PDF)
ocr = RapidOCR()
out = {}
for pg in [1, 279, 447, 508]:
    page = d[pg-1]
    pix = page.get_pixmap(matrix=pymupdf.Matrix(2.5, 2.5))
    img = np.array(Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB"))
    res, _ = ocr(img)
    txt = "\n".join(r[1] for r in res) if res else ""
    out[pg] = txt
    print(f"===== p{pg} (텍스트층 {len(page.get_text().strip())}자 → OCR {len(txt)}자) =====")
    print(txt[:600]); print()
json.dump(out, open(r"C:\Users\wisew\camnemi-crm\backend\hikorea_manuals\사증민원_이미지페이지_OCR.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
print("저장됨")
