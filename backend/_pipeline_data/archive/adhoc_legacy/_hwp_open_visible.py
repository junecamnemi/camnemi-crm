#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Open the protected 사증민원 manual via Hangul COM and keep it VISIBLE for GUI control."""
import os, sys, time, pythoncom, win32com.client as win32

SRC = r"C:\Users\wisew\camnemi-crm\backend\hikorea_manuals\260901 사증민원 자격별 안내 매뉴얼.hwp"
pythoncom.CoInitialize()
hwp = win32.Dispatch("HWPFrame.HwpObject")
try: hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")
except Exception: pass
try: hwp.SetMessageBoxMode(0x00020000)
except Exception: pass
hwp.XHwpWindows.Item(0).Visible = True
print("opening...", flush=True)
ok = hwp.Open(SRC, "HWP", "forceopen:true;versionwarning:false;password:")
print("open:", ok, flush=True)
# keep alive so GUI can operate; user/GUI drives it
print("READY - hold open 300s", flush=True)
try:
    time.sleep(300)
except KeyboardInterrupt:
    pass
try: hwp.Quit()
except Exception: pass
pythoncom.CoUninitialize()
print("closed", flush=True)
