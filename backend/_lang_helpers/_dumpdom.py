#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Given url + name, dump rendered DOM text via headless chrome to a file."""
import subprocess, sys, os, re
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
name, url, out = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(os.path.dirname(out), exist_ok=True)
# Use headless chrome --dump-dom to get post-JS DOM html
cmd = [CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
       "--disable-dev-shm-usage", "--virtual-time-budget=10000",
       "--dump-dom", url]
r = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
html = r.stdout or ""
# Also collect text
text = re.sub(r"<script[\s\S]*?</script>|<style[\s\S]*?</style>", " ", html)
text = re.sub(r"<[^>]+>", " ", text)
text = re.sub(r"\s+", " ", text)
with open(out + ".html", "w", encoding="utf-8") as f:
    f.write(html)
with open(out + ".txt", "w", encoding="utf-8") as f:
    f.write(text)
# print links containing pdf or korean keywords
links = re.findall(r'<a[^>]+href="([^"]+)"[^>]*>([\s\S]{0,80}?)</a>', html)
print(f"== {name} == domlen={len(html)} txtlen={len(text)}")
for h, t in links:
    tl = re.sub(r"<[^>]+>|\s+", "", t)
    if 'pdf' in h.lower() or any(k in tl for k in ('모집','요강','입학','교육','한국어','어학','download','다운','첨부','서류','학비','수업료','등록')):
        print("  LINK:", h, "|", tl)
