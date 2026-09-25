#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extract embedded images from the protected 사증민원 HWP and OCR them."""
import olefile, os, io
import numpy as np
from PIL import Image
from rapidocr_onnxruntime import RapidOCR

SRC = r"C:\Users\wisew\camnemi-crm\backend\hikorea_manuals\260901 사증민원 자격별 안내 매뉴얼.hwp"
OUTDIR = r"C:\Users\wisew\camnemi-crm\backend\hikorea_manuals\사증_images"
os.makedirs(OUTDIR, exist_ok=True)

f = olefile.OleFileIO(SRC)
streams = ["/".join(s) for s in f.listdir()]
bins = [s for s in streams if s.startswith("BinData")]
print("이미지 스트림:", len(bins))

ocr = RapidOCR()
all_text = []
for s in sorted(bins):
    try:
        b = f.openstream(s).read()
        ext = os.path.splitext(s)[1].lower()
        if ext in (".bmp", ".png", ".jpg", ".jpeg"):
            img = Image.open(io.BytesIO(b)).convert("RGB")
        elif ext == ".tmp":
            img = Image.open(io.BytesIO(b)).convert("RGB")
        else:
            continue
        w, h = img.size
        path = os.path.join(OUTDIR, os.path.basename(s).replace("/", "_"))
        img.save(path)
        res, _ = ocr(np.array(img))
        txt = "\n".join(r[1] for r in (res or []))
        all_text.append(f"\n### {s} ({w}x{h})\n{txt}")
        print(f"  {s}: {w}x{h} → OCR {len(txt)}자")
    except Exception as e:
        print(f"  {s}: ERR {str(e)[:60]}")

out = "\n".join(all_text)
dst = os.path.join(os.path.dirname(OUTDIR), "사증민원_매뉴얼_OCR.txt")
open(dst, "w", encoding="utf-8").write(out)
print("\n총 OCR:", len(out), "→", dst)
print(out[:600])
