#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test real-time trend sources: Naver(실검/뉴스랭킹), YouTube 급상승, TikTok."""
import subprocess, os, re, json, urllib.request
CH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
T = os.environ.get("TEMP","/tmp")
UA = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"}
def chrome(url, budget=12000, tag="t1", t=90):
    r = subprocess.run([CH,"--headless=new","--disable-gpu","--no-sandbox",
        f"--virtual-time-budget={budget}","--user-data-dir="+os.path.join(T,"chr_"+tag),
        "--dump-dom", url], capture_output=True, timeout=t)
    return r.stdout.decode("utf-8","ignore")
def http(url, t=25):
    try:
        req=urllib.request.Request(url, headers=UA)
        return urllib.request.urlopen(req, timeout=t).read().decode("utf-8","ignore")
    except Exception as e:
        return f"ERR:{str(e)[:60]}"
print("=== 1) 네이버 DataLab 실시간 검색어 ===")
h = http("https://datalab.naver.com/keyword/realtimeList.naver")
print("  len:", len(h), "| ERR" if h.startswith("ERR") else "")
if not h.startswith("ERR"):
    kws = re.findall(r'"keyword":"([^"]+)"', h)[:10]
    print("  키워드:", kws)
print("\n=== 2) 네이버 뉴스 랭킹 (많이 본) ===")
h2 = chrome("https://news.naver.com/main/ranking/popularDay.naver", 10000, "nv")
print("  len:", len(h2))
titles = re.findall(r'class="list_title[^"]*"[^>]*>\s*<a[^>]*>([^<]{5,60})</a>', h2)
print("  제목:", titles[:6])
print("\n=== 3) YouTube 급상승 ===")
h3 = chrome("https://www.youtube.com/feed/trending?bp=4gIKGgh0cmVuZGluZ3IKEgYIChABGAc%3D", 12000, "yt")
print("  len:", len(h3))
yt = re.findall(r'"title":\{"runs":\[\{"text":"([^"]{5,80})"', h3)[:10]
print("  영상:", yt[:6])
print("\n=== 4) TikTok 트렌드 ===")
h4 = http("https://www.tiktok.com/discover")
print("  len:", len(h4), "| ERR" if h4.startswith("ERR") else "")