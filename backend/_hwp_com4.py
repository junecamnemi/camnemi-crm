#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extract text from protected 사증민원 HWP via Hangul COM: SelectAll+Copy -> clipboard."""
import os, sys, time, pythoncom, win32com.client as win32
import win32clipboard, win32con

SRC = r"C:\Users\USER\camnemi-crm\backend\hikorea_manuals\260901 사증민원 자격별 안내 매뉴얼.hwp"
OUT = r"C:\Users\USER\camnemi-crm\backend\hikorea_manuals\사증민원_매뉴얼_COM.txt"
def log(*a): print(*a, flush=True)

pythoncom.CoInitialize()
hwp = win32.Dispatch("HWPFrame.HwpObject")
try: hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")
except Exception: pass
try: hwp.SetMessageBoxMode(0x00020000 | 0x00000002)
except Exception: pass
hwp.XHwpWindows.Item(0).Visible = True

log("open...")
if not hwp.Open(SRC, "HWP", "forceopen:true;versionwarning:false;password:"):
    log("open fail"); sys.exit(1)
log("open ok")

# 1) InitScan with proper args
try:
    hwp.InitScan(0x0003, 0)
    buf = []
    while True:
        r = hwp.GetText()
        if isinstance(r, tuple):
            st, txt = r[0], r[1]
            if st == 0: break
            if txt: buf.append(txt)
        else:
            if not r: break
            buf.append(r)
    hwp.ReleaseScan()
    t1 = "".join(buf)
    log("InitScan(0x0003,0) len:", len(t1))
except Exception as e:
    log("InitScan err:", str(e)[:120]); t1 = ""

# 2) SelectAll + Copy -> clipboard
t2 = ""
try:
    hwp.Run("SelectAll")
    time.sleep(0.6)
    hwp.Run("Copy")
    time.sleep(1.2)
    win32clipboard.OpenClipboard()
    try:
        t2 = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
    finally:
        win32clipboard.CloseClipboard()
    log("clipboard len:", len(t2))
except Exception as e:
    log("copy err:", str(e)[:120])

best = max([t1, t2], key=len)
log("best len:", len(best))
if len(best) > 2000:
    open(OUT, "w", encoding="utf-8").write(best)
    log("SAVED:", OUT)
    log(best[:500])
else:
    log("preview:", best[:300])
try: hwp.Clear(1); hwp.Quit()
except Exception: pass
pythoncom.CoUninitialize()
log("done")
