#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Render HiKorea 민원서식 page with Chrome headless and extract real file-download URLs."""
import subprocess, re, json, os

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
URL = "https://www.hikorea.go.kr/board/BoardApplicationListR.pt"

r = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
                    "--virtual-time-budget=15000", "--dump-dom", URL],
                   capture_output=True, text=True, encoding="utf-8", errors="ignore", timeout=180)
html = r.stdout or ""
open(r"C:\Users\wisew\camnemi-crm\backend\_hikorea_dom.html", "w", encoding="utf-8").write(html)
print("DOM len:", len(html))

# find onclick handlers / file links
pat = re.findall(r"(?:onclick|href)\s*=\s*[\"']([^\"']*(?:file|File|download|Download|hwp|pdf)[^\"']*)[\"']", html)
print("\n=== 후보 링크/핸들러 (상위 25) ===")
seen=set()
for p in pat:
    if p in seen: continue
    seen.add(p)
    print("  ", p[:140])
print("총 후보:", len(seen))

# look for function definitions used by the buttons
fn = re.findall(r"function\s+(\w*[Ff]ile\w*|\w*[Dd]ownload\w*)\s*\(", html)
print("\n=== 관련 함수명 ===", sorted(set(fn))[:15])