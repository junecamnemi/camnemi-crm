#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Print the protected 사증민원 HWP to PDF via Microsoft Print to PDF (DRM allows printing)."""
import os, sys, time, pythoncom, win32com.client as win32

SRC = r"C:\Users\wisew\camnemi-crm\backend\hikorea_manuals\260901 사증민원 자격별 안내 매뉴얼.hwp"
PDF = r"C:\Users\wisew\camnemi-crm\backend\hikorea_manuals\사증민원_매뉴얼.pdf"
def log(*a): print(*a, flush=True)

pythoncom.CoInitialize()
hwp = win32.Dispatch("HWPFrame.HwpObject")
try: hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")
except Exception: pass
try: hwp.SetMessageBoxMode(0x00020000 | 0x00000002)
except Exception: pass
hwp.XHwpWindows.Item(0).Visible = True
log("open:", hwp.Open(SRC, "HWP", "forceopen:true;versionwarning:false;password:"))

# set printer device
try:
    hwp.PrintDevice = "Microsoft Print to PDF"
    log("print device set:", hwp.PrintDevice)
except Exception as e:
    log("set device err:", str(e)[:80])

# print all pages
try:
    r = hwp.Print(0)   # 0 = all pages? may prompt for PDF filename
    log("Print(0):", r)
except Exception as e:
    log("Print err:", str(e)[:120])

time.sleep(5)
log("PDF exists:", os.path.exists(PDF))
try: hwp.Quit()
except Exception: pass
pythoncom.CoUninitialize()
log("done")
