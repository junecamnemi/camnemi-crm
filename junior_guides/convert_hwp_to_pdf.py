#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Convert HWP admission-guide files to PDF.
Uses pyhwp (hwp5html -> XHTML) + headless Chrome (--print-to-pdf).

Usage:
    python convert_hwp_to_pdf.py <input.hwp> [output.pdf]

If output.pdf is omitted, writes alongside the input with a .pdf extension.
"""
import os, sys, shutil, subprocess

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
TMP = os.path.join(os.environ.get("TEMP", "/tmp"), "hwp2pdf_work")


def hwp_to_html(hwp_path, out_dir):
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir)
    os.makedirs(out_dir)
    sys.argv = ["hwp5html", "--output", out_dir, hwp_path]
    from hwp5.hwp5html import main
    try:
        main()
    except SystemExit:
        pass
    idx = os.path.join(out_dir, "index.xhtml")
    return idx if os.path.exists(idx) else None


def html_to_pdf(xhtml_path, pdf_path):
    url = "file:///" + xhtml_path.replace("\\", "/")
    cmd = [CHROME, "--headless", "--disable-gpu", "--no-sandbox",
           f"--user-data-dir={TMP}\\chrome_profile",
           f"--print-to-pdf={pdf_path}", "--no-pdf-header-footer", url]
    subprocess.run(cmd, capture_output=True, timeout=180)
    if os.path.exists(pdf_path):
        with open(pdf_path, "rb") as f:
            return f.read(5) == b"%PDF-"
    return False


def convert(hwp_path, pdf_path=None):
    if not pdf_path:
        pdf_path = os.path.splitext(hwp_path)[0] + ".pdf"
    base = os.path.splitext(os.path.basename(hwp_path))[0]
    out_dir = os.path.join(TMP, base)
    try:
        xhtml = hwp_to_html(hwp_path, out_dir)
        if not xhtml:
            print(f"  {base}: HTML conversion failed")
            return None
        if html_to_pdf(xhtml, pdf_path):
            size = os.path.getsize(pdf_path)
            print(f"  {base}: OK ({size} bytes) -> {pdf_path}")
            return pdf_path
        print(f"  {base}: Chrome render failed")
        return None
    except Exception as e:
        print(f"  {base}: ERROR {e}")
        return None
    finally:
        shutil.rmtree(out_dir, ignore_errors=True)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    inp = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else None
    result = convert(inp, out)
    sys.exit(0 if result else 1)
