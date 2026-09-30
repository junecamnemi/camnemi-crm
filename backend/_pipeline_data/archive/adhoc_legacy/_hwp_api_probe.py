#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Probe Hangul COM text-extraction signatures on the protected 사증민원 manual."""
import pythoncom, win32com.client as win32, time, os

SRC = r"C:\Users\wisew\camnemi-crm\backend\hikorea_manuals\260901 사증민원 자격별 안내 매뉴얼.hwp"
OUT = r"C:\Users\wisew\camnemi-crm\backend\hikorea_manuals\사증_정부.txt"
def log(*a): print(*a, flush=True)

pythoncom.CoInitialize()
hwp = win32.Dispatch("HWPFrame.HwpObject")
try: hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")
except Exception: pass
try: hwp.SetMessageBoxMode(0x00020000|0x00000002)
except Exception: pass
hwp.XHwpWindows.Item(0).Visible = True
log("open:", hwp.Open(SRC, "HWP", "forceopen:true;versionwarning:false;password:"))

best = ""
# probe InitScan signatures
for label, fn in [
    ("InitScan()",        lambda: hwp.InitScan()),
    ("InitScan(0x0003)",  lambda: hwp.InitScan(0x0003)),
    ("InitScan(0,0,3)",   lambda: hwp.InitScan(0, 0, 3)),
    ("InitScan(3,0)",     lambda: hwp.InitScan(3, 0)),
]:
    try:
        r = fn(); log(f"{label} -> {r}")
        buf=[]; n=0
        while n < 5000:
            g = hwp.GetText(); n+=1
            if isinstance(g, tuple):
                if g[0]==0: break
                if g[1]: buf.append(g[1])
            else:
                if not g: break
                buf.append(str(g))
        txt="".join(buf)
        log(f"   text len={len(txt)}")
        if len(txt) > len(best): best = txt
        try: hwp.ReleaseScan()
        except Exception: pass
    except Exception as e:
        log(f"{label} ERR: {str(e)[:110]}")

# probe page text
for i in range(3):
    try:
        pt = hwp.GetPageText(i+1) if hasattr(hwp,"GetPageText") else ""
        log(f"GetPageText({i+1}) len={len(pt or '')}")
        if pt and len(pt) > len(best): best = pt
    except Exception as e:
        log(f"GetPageText({i+1}) ERR {str(e)[:80]}"); break

log("BEST:", len(best))
if len(best) > 1000:
    open(OUT,"w",encoding="utf-8").write(best); log("saved", OUT)
    log(best[:400])
try: hwp.Clear(1); hwp.Quit()
except Exception: pass
pythoncom.CoUninitialize()
log("done")
