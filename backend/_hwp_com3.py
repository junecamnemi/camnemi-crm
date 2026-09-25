#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extract text from the protected 사증민원 HWP via Hangul COM GetText (bypass SaveAs/DRM)."""
import os, sys, time, pythoncom, win32com.client as win32

SRC = r"C:\Users\wisew\camnemi-crm\backend\hikorea_manuals\260901 사증민원 자격별 안내 매뉴얼.hwp"
OUT = r"C:\Users\wisew\camnemi-crm\backend\hikorea_manuals\사증민원_매뉴얼_COM.txt"

def log(*a): print(*a, flush=True)

pythoncom.CoInitialize()
hwp = win32.Dispatch("HWPFrame.HwpObject")
try: hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")
except Exception: pass
try: hwp.SetMessageBoxMode(0x00020000 | 0x00000002)
except Exception: pass
hwp.XHwpWindows.Item(0).Visible = True

log("opening...")
ok = hwp.Open(SRC, "HWP", "forceopen:true;versionwarning:false;password:")
log("Open:", ok)
if not ok:
    log("fail"); hwp.Quit(); sys.exit(1)

# 1) try InitScan/GetText
texts = []
for method in range(3):
    try:
        if method == 0:
            # scan-based extraction
            hwp.InitScan()
            buf = []
            while True:
                st, txt = hwp.GetText()
                if st == 0: break
                if txt: buf.append(txt)
            hwp.ReleaseScan()
            texts.append("".join(buf)); log("InitScan len:", len(texts[-1]))
        elif method == 1:
            t = hwp.GetTextFile("TXT", "")   # some versions
            texts.append(t or ""); log("GetTextFile len:", len(texts[-1] or ""))
        else:
            # MovePos / head/ctrl loops — skip
            pass
    except Exception as e:
        log(f"method{method} err:", str(e)[:120])

# also try SaveAs with explicit format enum via SaveAsEx / different names
for fmt in ["TXT", "HTML", "UNICODE"]:
    try:
        p = OUT.replace("_COM.txt", f"_{fmt}.out")
        r = hwp.SaveAs(p, fmt, "")
        log(f"SaveAs {fmt}:", r, os.path.exists(p))
    except Exception as e:
        log(f"SaveAs {fmt} err:", str(e)[:100])

best = max(texts, key=len) if texts else ""
log("총 텍스트:", len(best))
if len(best) > 2000:
    open(OUT, "w", encoding="utf-8").write(best)
    log("saved:", OUT)
    log("preview:", best[:400])
try: hwp.Clear(1); hwp.Quit()
except Exception: pass
pythoncom.CoUninitialize()
log("done")
