# -*- coding: utf-8 -*-
"""Deep direct scan: for remaining junior colleges, check if guide_url itself is a
PDF; else fetch and crawl depth-1 links looking for 외국인/모집/요강 PDFs.
Pure curl, no LLM -> no rate limit."""
import json, os, re, subprocess, time, urllib.parse

KB = json.load(open(r"C:\Users\USER\camnemi-crm\backend\verified_kb.json", encoding="utf-8"))
js = KB["junior"]["schools"]
SAVEDIR = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project\adiga_2026_전문대학_모집요강"

def norm(s): return s.replace("대학교","").replace("대학","").replace("전문대","").replace(" ","")
have = set(norm(os.path.splitext(f)[0].replace("_전문학사_모집요강","")) for f in os.listdir(SAVEDIR) if f.endswith(".pdf"))

def curl(url, timeout=20):
    try:
        return subprocess.run(["curl","-sL","-A","Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120","--max-time",str(timeout),url],capture_output=True).stdout
    except: return b""

def is_pdf(b): return b[:4]==b"%PDF"

targets=[(n,v["guide_url"]) for n,v in js.items() if v.get("guide_url") and norm(n) not in have]
print(f"남은 처리: {len(targets)}")

KEY_PDF = re.compile(r'(?:외국인|유학|순수|재외국민|모집|요강|입학|foreign|intl|international)[^"\')\s]*(?:\.pdf|FileDown|download\.do)[^"\')\s]*', re.I)
ANY_PDF = re.compile(r'href="([^"]*\.pdf[^"]*)"', re.I)

saved=[]; failed=[]
for n, u in targets:
    sn=norm(n)
    if sn in have: continue
    # 1) guide_url itself a PDF?
    b = curl(u)
    if is_pdf(b) and len(b)>30000:
        open(os.path.join(SAVEDIR,f"{n}_전문학사_모집요강.pdf"),"wb").write(b)
        saved.append((n,"guide_url_pdf",len(b))); have.add(sn); continue
    txt = b.decode("utf-8","ignore")
    # 2) find candidate pdf/file links in page (priority 외국인)
    cands = []
    for m in KEY_PDF.finditer(txt):
        href = m.group(0)
        # extract actual url-ish
        href2 = re.search(r'(?:href|src)="?([^"\s>]+)', href)
        val = href2.group(1) if href2 else href
        val = val.strip('"').strip("'")
        if val and val.lower().endswith(('.pdf','.do')) or 'download' in val.lower() or 'fileDown' in val.lower():
            cands.append(val)
    for m in ANY_PDF.finditer(txt):
        if m.group(1) not in cands: cands.append(m.group(1))
    # resolve relative
    got=False
    for c in cands[:8]:
        full = c if c.startswith("http") else (urllib.parse.urljoin(u,c))
        cb = curl(full)
        if is_pdf(cb) and len(cb)>30000:
            open(os.path.join(SAVEDIR,f"{n}_전문학사_모집요강.pdf"),"wb").write(cb)
            saved.append((n,"page_pdf",len(cb))); have.add(sn); got=True; break
    if not got: failed.append(n)
    time.sleep(0.2)

print(f"\n저장 성공: {len(saved)}")
for n,m,sz in saved: print(f"  ✓ {n} ({m}, {sz})")
print(f"\n실패(수동 필요): {len(failed)}")
print("  ", failed)
json.dump({"saved":saved,"failed":failed}, open(r"C:\Users\USER\camnemi-crm\backend\_junior_deepscan.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
