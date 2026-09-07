#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Render url -> pdf via headless chrome. Args: url outfile. Prints pages+texthead for verify."""
import subprocess, sys, os
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
url, out = sys.argv[1], sys.argv[2]
out = os.path.abspath(out)
cmd = [CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
       "--disable-dev-shm-usage", "--virtual-time-budget=15000",
       "--print-to-pdf-no-header",
       f"--print-to-pdf={out}", url]
r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
size = os.path.getsize(out) if os.path.exists(out) else 0
print(f"URL {url}\nOUT {out}\nsize={size}")
print(r.stderr[-500:] if r.stderr else "")
