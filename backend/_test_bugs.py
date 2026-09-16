#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test Bugs K-POP idol chart scraping (idol-only chart for students)."""
import subprocess, os, re, json
CH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"; T=os.environ.get("TEMP","/tmp")
def chrome(url, budget=12000, tag="bg", t=90):
    r = subprocess.run([CH,"--headless=new","--disable-gpu","--no-sandbox","--lang=ko-KR",
        f"--virtual-time-budget={budget}","--user-data-dir="+os.path.join(T,"chr_"+tag),
        "--dump-dom", url], capture_output=True, timeout=t)
    return r.stdout.decode("utf-8","ignore")
url="https://music.bugs.co.kr/genre/chart/kpop/idol/total/day"
h=chrome(url, 12000, "bugs")
print("len:", len(h))
# song titles: Bugs uses <p class="title"><a ...>TITLE</a>
titles = re.findall(r'<p class="title"[^>]*>\s*<a[^>]*>([^<]{2,80})</a>', h)
artists = re.findall(r'<p class="artist"[^>]*>\s*<a[^>]*>([^<]{2,60})</a>', h)
if not titles:
    titles = re.findall(r'class="trackTitle"[^>]*>([^<]{2,80})<', h)
print("곡:", len(titles), titles[:8])
print("아티스트:", len(artists), artists[:8])
# fallback patterns
if not titles:
    for pat in [r'"trackTitle":"([^"]{2,60})"', r'"artistName":"([^"]{2,40})"', r'<strong>([^<]{2,60})</strong>']:
        m=re.findall(pat,h); print(f"[{pat[:24]}] {len(m)}", m[:5])