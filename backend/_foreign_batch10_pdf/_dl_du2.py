#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests, re, os
requests.packages.urllib3.disable_warnings()
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"}
s = requests.Session(); s.headers.update(UA)
OUT = os.path.dirname(os.path.abspath(__file__))

def get(url, label):
    r = s.get(url, verify=False, timeout=40)
    r.encoding="utf-8"
    print(f"\n===== {label} :: {url}")
    print("http", r.status_code, "len", len(r.text))
    return r.text

def find_downloads(html, limit=30):
    # anchor blocks with text + download url
    seen=[]
    for m in re.finditer(r'<a[^>]+href="([^"]*download\.do[^"]*)"[^>]*>(.*?)</a>', html, re.S):
        href=m.group(1); txt=re.sub(r'<[^>]+>','',m.group(2)).strip()
        if not href.startswith("http"): href="https://enter.du.ac.kr"+href
        seen.append((txt[:80], href))
    # also generic .pdf links
    for m in re.finditer(r'href="([^"]*\.(?:pdf|hwp))"[^>]*>(.*?)</a>', html, re.S):
        href=m.group(1); txt=re.sub(r'<[^>]+>','',m.group(2)).strip()
        if not href.startswith("http"): href="https://enter.du.ac.kr"+href
        seen.append((txt[:80], href))
    for txt,href in dict(seen).items(): print("  *", repr(txt), "=>", href[:160])
    return dict(seen)

# Try the 순수외국인 모집요강 submenu url (menuord=8, 모집요강)
h = get("https://enter.du.ac.kr/submenu.do?menuUrl=xb3PYzpHlMe9%2fKoPQ1rtwA%3d%3d", "순수외국인_모집요강")
# Check where it landed
t=re.search(r'<title>(.*?)</title>', h, re.S)
print("page title:", t.group(1).strip() if t else None)
print("dongseoul?", "동서울" in h)
find_downloads(h)
