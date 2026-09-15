#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Find HiKorea 안내매뉴얼 (manual) pages/files: 사증민원 / 체류민원."""
import subprocess, re, json

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
URLS = [
  "https://www.hikorea.go.kr/board/BoardNtcDetailR.pt?BBS_SEQ=1&BBS_GB_CD=BS10&NTCCTT_SEQ=1062&page=1",
  "https://www.hikorea.go.kr/board/BoardNtcListR.pt?BBS_GB_CD=BS10",
]
for u in URLS:
    print("="*70); print("URL:", u)
    r = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
                        "--virtual-time-budget=15000", "--dump-dom", u],
                       capture_output=True, text=True, encoding="utf-8", errors="ignore", timeout=180)
    html = r.stdout or ""
    print("DOM len:", len(html))
    # download calls
    calls = re.findall(r"fnNewFileDownLoad\('([^']*)','([^']*)','([^']+)','([^']+)'\)", html)
    seen=set()
    for spec,d,apnd,ori in calls:
        if apnd in seen: continue
        seen.add(apnd)
        print(f"   [{spec}/{d}] {ori}  <{apnd}>")
    # any hwp/pdf links
    links = sorted(set(re.findall(r'href="([^"]+\.(?:hwp|pdf|docx?))"', html)))
    for l in links[:20]: print("   LINK:", l[:120])
    if not calls and not links:
        # print titles of notice rows to find manual entries
        titles = re.findall(r'<a[^>]*>([^<]{6,80})</a>', html)
        man = [t.strip() for t in titles if '매뉴얼' in t or '민원' in t]
        print("   관련 제목:", man[:15])
