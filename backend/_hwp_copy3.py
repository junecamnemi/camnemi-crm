#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Open 사증민원, wait for full render, SelectAll + Copy -> clipboard (generous waits)."""
import os, sys, time, pythoncom, win32com.client as win32
import win32clipboard, win32con

SRC = r"C:\Users\wisew\camnemi-crm\backend\hikorea_manuals\260901 사증민원 자격별 안내 매뉴얼.hwp"
OUT = r"C:\Users\wisew\camnemi-crm\backend\hikorea_manuals\사증민원_매뉴얼_복사.txt"
def log(*a): print(*a, flush=True)

pythoncom.CoInitialize()
hwp = win32.Dispatch("HWPFrame.HwpObject")
try: hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")
except Exception: pass
try: hwp.SetMessageBoxMode(0x00020000)
except Exception: pass
hwp.XHwpWindows.Item(0).Visible = True
log("open:", hwp.Open(SRC, "HWP", "forceopen:true;versionwarning:false;password:"))
log("waiting for full render...")
time.sleep(6)

# go to very top
try:
    hwp.Run("MoveTop"); time.sleep(1)
except Exception as e:
    log("MoveTop:", str(e)[:60])

best = ""
# 1) SelectAll + Copy with generous wait
try:
    hwp.Run("SelectAll")
    time.sleep(3)
    hwp.Run("Copy")
    time.sleep(4)
    win32clipboard.OpenClipboard()
    try:
        t = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
    finally:
        win32clipboard.CloseClipboard()
    log("clipboard len:", len(t))
    best = t or ""
except Exception as e:
    log("copy err:", str(e)[:120])

# 2) also try GetTextFile / ExportHTML (DRM may allow some exports)
for fmt, ext in [("TXT","txt"), ("HTML","html"), ("HWP","hwp")]:
    try:
        p = OUT.replace(".txt", f"_{fmt}.{ext}")
        r = hwp.SaveAs(p, fmt, "")
        log(f"SaveAs {fmt}:", r, os.path.exists(p))
        if os.path.exists(p) and os.path.getsize(p) > 1000 and not best:
            if fmt in ("TXT","HTML"):
                best = open(p, encoding="utf-8", errors="ignore").read()
    except Exception as e:
        log(f"SaveAs {fmt} err:", str(e)[:70])

if len(best) > 2000:
    open(OUT, "w", encoding="utf-8").write(best); log("SAVED:", OUT, len(best))
    log(best[:500])
else:
    log("best too small:", len(best), "| preview:", best[:300])
try: hwp.Quit()
except Exception: pass
pythoncom.CoUninitialize()
log("done")
