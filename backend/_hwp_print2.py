#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Print protected 사증민원 to PDF via HAction (set printer + print)."""
import os, sys, time, pythoncom, win32com.client as win32

SRC = r"C:\Users\USER\camnemi-crm\backend\hikorea_manuals\260901 사증민원 자격별 안내 매뉴얼.hwp"
def log(*a): print(*a, flush=True)

pythoncom.CoInitialize()
hwp = win32.Dispatch("HWPFrame.HwpObject")
try: hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")
except Exception: pass
try: hwp.SetMessageBoxMode(0x00020000 | 0x00000002)
except Exception: pass
hwp.XHwpWindows.Item(0).Visible = True
log("open:", hwp.Open(SRC, "HWP", "forceopen:true;versionwarning:false;password:"))

# Print via HAction
for attempt in range(2):
    try:
        act = hwp.CreateAction("Print")
        pset = act.GetDefault("Print")
        log("pset items:", [pset.ItemCount] if hasattr(pset,'ItemCount') else "?")
        try:
            pset.SetItem("Device", "Microsoft Print to PDF")
            log("device set via pset")
        except Exception as e:
            log("set device skip:", str(e)[:60])
        r = act.Execute(pset)
        log("Print execute:", r)
        break
    except Exception as e:
        log(f"attempt{attempt} err:", str(e)[:120]); time.sleep(2)

time.sleep(6)
# print dialog may be open; wait and let GUI handle
log("waiting for dialog...")
time.sleep(8)
try: hwp.Quit()
except Exception: pass
pythoncom.CoUninitialize()
log("done")
