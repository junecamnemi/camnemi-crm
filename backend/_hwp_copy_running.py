#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Connect to the RUNNING Hangul instance (doc open) -> SelectAll + Copy -> clipboard text."""
import os, sys, time, pythoncom, win32com.client as win32
import win32clipboard, win32con

OUT = r"C:\Users\wisew\camnemi-crm\backend\hikorea_manuals\사증민원_매뉴얼_COM2.txt"
def log(*a): print(*a, flush=True)

pythoncom.CoInitialize()
# connect to the running Hangul instance that has the doc open
hwp = win32.GetActiveObject("HWPFrame.HwpObject")
log("connected")

# navigate to start then select all
try:
    hwp.Run("MoveTop")   # go to start
    time.sleep(0.5)
except Exception as e:
    log("MoveTop err:", str(e)[:80])

buf = []
# first try scan-based full text
try:
    hwp.InitScan(3, 0)
    n = 0
    while n < 200000:
        g = hwp.GetText()
        if isinstance(g, tuple):
            if g[0] == 0: break
            if g[1]: buf.append(g[1])
        else:
            if not g: break
            buf.append(str(g))
        n += 1
    hwp.ReleaseScan()
    log("InitScan text:", len("".join(buf)))
except Exception as e:
    log("InitScan err:", str(e)[:120])

# SelectAll + Copy
t2 = ""
try:
    hwp.Run("SelectAll")
    time.sleep(1.0)
    hwp.Run("Copy")
    time.sleep(2.0)
    win32clipboard.OpenClipboard()
    try:
        t2 = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
    finally:
        win32clipboard.CloseClipboard()
    log("clipboard len:", len(t2))
except Exception as e:
    log("copy err:", str(e)[:120])

best = max(["".join(buf), t2 or ""], key=len)
log("BEST:", len(best))
if len(best) > 2000:
    open(OUT, "w", encoding="utf-8").write(best)
    log("SAVED:", OUT)
    log(best[:500])
else:
    log("preview:", best[:300])
pythoncom.CoUninitialize()
log("done")
