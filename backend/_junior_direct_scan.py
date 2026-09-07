# -*- coding: utf-8 -*-
"""Efficient direct crawler: for each junior college lacking a local PDF, hit its
guide_url, find any 외국인 admission PDF link, download. Uses curl via subprocess
(no agent LLM calls -> no rate limit). Logs results."""
import json, os, re, subprocess, time

KB = json.load(open(r"C:\Users\USER\camnemi-crm\backend\verified_kb.json", encoding="utf-8"))
js = KB["junior"]["schools"]
SAVEDIR = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project\adiga_2026_전문대학_모집요강"
os.makedirs(SAVEDIR, exist_ok=True)

# schools we already have
def norm(s): return s.replace("대학교","").replace("대학","").replace("전문대","").replace(" ","")
have = set(norm(os.path.splitext(f)[0].replace("_전문학사_모집요강","")) for f in os.listdir(SAVEDIR) if f.endswith(".pdf"))

def curl(url, timeout=25, referer=None):
    hdr = ["-sL","-A","Mozilla/5.0 (Windows NT 10.0; Win64; x64)"]
    if referer: hdr += ["-e", referer]
    try:
        r = subprocess.run(["curl"]+hdr+["--max-time",str(timeout),url], capture_output=True)
        return r.stdout
    except Exception:
        return b""

targets = []
for n, v in js.items():
    if not v.get("guide_url"): continue
    if norm(n) in have: continue
    targets.append((n, v["guide_url"]))

print(f"누락 처리 대상: {len(targets)}개")
# First: just fetch each guide_url homepage and grep for .pdf / 요강 links
results = {}
for n, u in targets:
    html = curl(u)
    if not html:
        results[n] = {"url": u, "pdfs": [], "file_links": [], "size": 0, "error": "fetch_fail"}
        continue
    txt = html.decode("utf-8","ignore")
    # find pdf links
    pdfs = re.findall(r'(?:href|src|data-url)="([^"]*\.pdf[^"]*)"', txt, re.I)
    # find 요강/fileDown links
    files = re.findall(r'(?:href|src)="([^"]*(?:fileDown|download|모집요강|FileDownload|attach)[^"]*)"', txt, re.I)
    pdfs = [p for p in pdfs if not p.lower().endswith(('.js','.css'))]
    results[n] = {"url": u, "pdfs": pdfs[:6], "file_links": files[:6], "size": len(html)}
    time.sleep(0.3)

json.dump(results, open(r"C:\Users\USER\camnemi-crm\backend\_junior_scan_urls.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
n_pdf = sum(1 for r in results.values() if r.get("pdfs"))
n_file = sum(1 for r in results.values() if r.get("file_links"))
print(f"직접 .pdf 링크 발견: {n_pdf}개 | fileDown/요강 링크: {n_file}개")
