#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extract protected 사증민원 HWP: per-page text (GetPageText) + render images (CreatePageImage)+OCR."""
import os, sys, time, pythoncom, win32com.client as win32
import numpy as np
from PIL import Image
from rapidocr_onnxruntime import RapidOCR

SRC = r"C:\Users\USER\camnemi-crm\backend\hikorea_manuals\260901 사증민원 자격별 안내 매뉴얼.hwp"
OUTDIR = r"C:\Users\USER\camnemi-crm\backend\hikorea_manuals"
PAGES = os.path.join(OUTDIR, "사증_pages"); os.makedirs(PAGES, exist_ok=True)
def log(*a): print(*a, flush=True)

pythoncom.CoInitialize()
hwp = win32.Dispatch("HWPFrame.HwpObject")
try: hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")
except Exception: pass
try: hwp.SetMessageBoxMode(0x00020000 | 0x00000002)
except Exception: pass
hwp.XHwpWindows.Item(0).Visible = True
log("open:", hwp.Open(SRC, "HWP", "forceopen:true;versionwarning:false;password:"))

try:
    pc = int(hwp.PageCount)
except Exception:
    pc = 0
log("PageCount:", pc)

ocr = RapidOCR()
all_text = []
for p in range(1, pc+1):
    # 1) page text
    t = ""
    try:
        r = hwp.GetPageText(p)
        if r:
            t = r if isinstance(r, str) else "".join(r) if isinstance(r, list) else str(r)
    except Exception as e:
        t = ""
    # 2) render to image
    img_path = os.path.join(PAGES, f"page{p:03d}.png")
    try:
        hwp.CreatePageImage(img_path, 1, 2)  # (path, format, option) guessed
    except Exception as e1:
        try:
            hwp.CreatePageImage(img_path) 
        except Exception as e2:
            img_path = None
    o = ""
    if img_path and os.path.exists(img_path):
        try:
            res, _ = ocr(np.array(Image.open(img_path).convert("RGB")))
            o = "\n".join(r[1] for r in (res or []))
        except Exception as e3:
            o = ""
    all_text.append(f"===== page {p} =====\n{t}\n[OCR]\n{o}")
    log(f"  p{p}: text={len(t)} ocr={len(o)} img={'Y' if img_path and os.path.exists(img_path) else 'N'}")

out = "\n".join(all_text)
dst = os.path.join(OUTDIR, "사증민원_매뉴얼_추출.txt")
open(dst, "w", encoding="utf-8").write(out)
log("총:", len(out), "→", dst)
log(out[:500])
try: hwp.Clear(1); hwp.Quit()
except Exception: pass
pythoncom.CoUninitialize()
log("done")
