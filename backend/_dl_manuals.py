#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extract and download the HiKorea 사증민원/체류민원 자격별 안내 매뉴얼 HWP files."""
import subprocess, re, os, json, urllib.request, urllib.parse, ssl

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
URL = "https://www.hikorea.go.kr/board/BoardNtcDetailR.pt?BBS_SEQ=1&BBS_GB_CD=BS10&NTCCTT_SEQ=1062&page=1"
OUT = r"C:\Users\wisew\camnemi-crm\backend\hikorea_manuals"
os.makedirs(OUT, exist_ok=True)

r = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
                    "--virtual-time-budget=18000", "--dump-dom", URL],
                   capture_output=True, text=True, encoding="utf-8", errors="ignore", timeout=180)
html = r.stdout or ""
open(os.path.join(OUT, "_page.html"), "w", encoding="utf-8").write(html)
print("DOM:", len(html))

# 1) fnNewFileDownLoad calls (any spec/dir)
calls = re.findall(r"fnNewFileDownLoad\('([^']*)','([^']*)','([^']+)','([^']+)'\)", html)
print("\n=== fnNewFileDownLoad 호출 ===")
for c in calls: print("  ", c)
if not calls:
    calls = re.findall(r"fnNewFileDownLoad\(([^)]{0,200})\)", html)
    print("\n=== raw 호출 ===")
    for c in calls[:12]: print("  ", c[:160])

# 2) direct href to hwp under the board
print("\n=== href hwp/pdf ===")
for h in sorted(set(re.findall(r'href="([^"]+\.(?:hwp|pdf|docx?))"', html))):
    print("  ", h[:160])

# 3) JS file-down functions with board params
print("\n=== fileDown / attach 함수 호출 ===")
for m in sorted(set(re.findall(r"(?:fileDown|FileDown|attachFileDown|downloadFile)\w*\(([^)]{0,180})\)", html)))[:15]:
    print("  ", m[:170])

# 4) the manual file names appear near <a> tags -> find their onclick
for name in ["사증민원 자격별 안내 매뉴얼", "체류민원 자격별 안내 매뉴얼", "수정 이력"]:
    i = html.find(name)
    if i < 0:
        print(f"\n[{name}] 못 찾음"); continue
    seg = html[max(0,i-700):i+200]
    oc = re.findall(r"onclick=\"([^\"]+)\"", seg)
    hr = re.findall(r'href="([^"]+)"', seg)
    print(f"\n=== {name} 주변 ===")
    print("   onclick:", oc[-2:] if oc else "없음")
    print("   href:", hr[-2:] if hr else "없음")
