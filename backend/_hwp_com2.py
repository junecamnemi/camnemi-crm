#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hangul COM: open protected 사증민원 HWP -> save PDF + TXT (with progress logging)."""
import os, sys, time, pythoncom, win32com.client as win32

SRC = r"C:\Users\USER\camnemi-crm\backend\hikorea_manuals\260901 사증민원 자격별 안내 매뉴얼.hwp"
OUTDIR = r"C:\Users\USER\camnemi-crm\backend\hikorea_manuals"

def log(*a):
    print(*a, flush=True)

log("start")
pythoncom.CoInitialize()
log("com init")
try:
    hwp = win32.Dispatch("HWPFrame.HwpObject")
    log("dispatch ok")
except Exception as e:
    log("dispatch FAIL", str(e)[:120]); sys.exit(1)

for attempt in range(2):
    try:
        hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")
        log("register ok"); break
    except Exception as e:
        log("register retry", str(e)[:80]); time.sleep(1)

try:
    hwp.SetMessageBoxMode(0x00020000 | 0x00000002)
    log("msgbox mode set")
except Exception as e:
    log("msgbox skip", str(e)[:60])

try:
    hwp.XHwpWindows.Item(0).Visible = True
    log("visible set")
except Exception as e:
    log("visible skip", str(e)[:60])

log("opening...")
ok = hwp.Open(SRC, "HWP", "forceopen:true;versionwarning:false;password:")
log("Open result:", ok)
if not ok:
    log("OPEN FAILED"); hwp.Quit(); sys.exit(2)

pdf = os.path.join(OUTDIR, "사증민원_매뉴얼.pdf")
r = hwp.SaveAs(pdf, "PDF", "")
log("PDF:", r, os.path.exists(pdf), (os.path.getsize(pdf) if os.path.exists(pdf) else 0))

txt = os.path.join(OUTDIR, "사증민원_매뉴얼.txt")
try:
    r2 = hwp.SaveAs(txt, "TXT", "")
    log("TXT:", r2, os.path.exists(txt), (os.path.getsize(txt) if os.path.exists(txt) else 0))
except Exception as e:
    log("TXT fail", str(e)[:100])

try:
    hwp.Clear(1); hwp.Quit()
except Exception:
    pass
pythoncom.CoUninitialize()
log("done")
