#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Convert the distribution-protected 사증민원 manual to PDF/text using Hangul (HWPFrame COM)."""
import os, sys, time, pythoncom, win32com.client as win32

SRC = r"C:\Users\USER\camnemi-crm\backend\hikorea_manuals\260901 사증민원 자격별 안내 매뉴얼.hwp"
OUTDIR = r"C:\Users\USER\camnemi-crm\backend\hikorea_manuals"

def main():
    pythoncom.CoInitialize()
    hwp = win32.Dispatch("HWPFrame.HwpObject")
    try:
        hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")
    except Exception as e:
        print("RegisterModule skip:", str(e)[:60])
    try:
        hwp.SetMessageBoxMode(0x00020000)  # suppress dialogs
    except Exception:
        pass
    hwp.XHwpWindows.Item(0).Visible = False
    print("한글 실행 OK")
    ok = hwp.Open(SRC, "HWP", "forceopen:true;versionwarning:false")
    print("Open:", ok)
    if not ok:
        print("열기 실패"); return
    # save as PDF
    pdf = os.path.join(OUTDIR, "사증민원_매뉴얼.pdf")
    r = hwp.SaveAs(pdf, "PDF", "")
    print("SaveAs PDF:", r, os.path.exists(pdf), os.path.getsize(pdf) if os.path.exists(pdf) else 0)
    # save as text
    txt = os.path.join(OUTDIR, "사증민원_매뉴얼.txt")
    try:
        r2 = hwp.SaveAs(txt, "TXT", "")
        print("SaveAs TXT:", r2, os.path.exists(txt))
    except Exception as e:
        print("TXT 실패:", str(e)[:80])
    hwp.Clear(1)
    hwp.Quit()
    pythoncom.CoUninitialize()

if __name__ == "__main__":
    main()
