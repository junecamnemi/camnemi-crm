#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OCR the 8 image-only lang PDFs via rapidocr -> save text per school."""
import pymupdf, os, numpy as np
from rapidocr_onnxruntime import RapidOCR
D = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project\adiga_2026_어학연수_모집요강"
OUT = r"C:\Users\USER\camnemi-crm\backend\_lang_ocr"
os.makedirs(OUT, exist_ok=True)
files = ["국립금오공과대학교_한국어교육원.pdf","나사렛대학교_한국어교육원.pdf","부산대_한국어교육원.pdf",
         "서울시립대_한국어교육원.pdf","서울신학대_한국어교육원.pdf","서일대학교_한국어교육원.pdf",
         "총신대_한국어교육원.pdf","한성대학교_한국어교육원.pdf"]
ocr = RapidOCR()
for fn in files:
    base = fn.replace("_한국어교육원.pdf","")
    d = pymupdf.open(os.path.join(D, fn))
    out_lines = []
    for i in range(len(d)):
        pix = d[i].get_pixmap(dpi=150)
        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
        if pix.n == 4: img = img[:,:,:3]
        try:
            res, _ = ocr(img)
        except Exception as e:
            res = None
        if res:
            out_lines.append(f"\n===== {base} PAGE {i+1} =====")
            for box, text, conf in res:
                out_lines.append(text)
    d.close()
    txt = "\n".join(out_lines)
    open(os.path.join(OUT, f"{base}.ocr.txt"), "w", encoding="utf-8").write(txt)
    print(f"{base}: {len(txt)} 자 OCR")
print("done")
