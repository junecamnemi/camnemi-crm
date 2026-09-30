#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Render protected 사증민원 HWP pages to images via Hangul COM, then OCR."""
import os, sys, time, pythoncom, win32com.client as win32

SRC = r"C:\Users\wisew\camnemi-crm\backend\hikorea_manuals\260901 사증민원 자격별 안내 매뉴얼.hwp"
OUTDIR = r"C:\Users\wisew\camnemi-crm\backend\hikorea_manuals\사증_pages"
os.makedirs(OUTDIR, exist_ok=True)
def log(*a): print(*a, flush=True)

pythoncom.CoInitialize()
hwp = win32.Dispatch("HWPFrame.HwpObject")
try: hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")
except Exception: pass
try: hwp.SetMessageBoxMode(0x00020000 | 0x00000002)
except Exception: pass
hwp.XHwpWindows.Item(0).Visible = True
log("open:", hwp.Open(SRC, "HWP", "forceopen:true;versionwarning:false;password:"))

# discover available methods
meths = [m for m in dir(hwp) if any(k in m for k in ("Page","Image","Save","Export","Print","Scan","View"))]
log("관련 메서드:", meths)

# try page-count
for attr in ("PageCount","GetPageCount"):
    try:
        log(attr, "=", getattr(hwp, attr)())
    except Exception as e:
        log(attr, "err", str(e)[:50])
