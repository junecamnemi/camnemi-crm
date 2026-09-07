# -*- coding: utf-8 -*-
"""Download the direct .pdf links found in _junior_scan_urls.json, verify, save as
{school}_전문학사_모집요강.pdf. Also attempt fileDown links."""
import json, os, re, subprocess, time

KB = json.load(open(r"C:\Users\USER\camnemi-crm\backend\verified_kb.json", encoding="utf-8"))
js = KB["junior"]["schools"]
SAVEDIR = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project\adiga_2026_전문대학_모집요강"
scan = json.load(open(r"C:\Users\USER\camnemi-crm\backend\_junior_scan_urls.json", encoding="utf-8"))

def norm(s): return s.replace("대학교","").replace("대학","").replace("전문대","").replace(" ","")
have = set(norm(os.path.splitext(f)[0].replace("_전문학사_모집요강","")) for f in os.listdir(SAVEDIR) if f.endswith(".pdf"))

def curl(url, timeout=30):
    try:
        return subprocess.run(["curl","-sL","-A","Mozilla/5.0","--max-time",str(timeout),url],capture_output=True).stdout
    except: return b""

def is_pdf(b): return b[:4]==b"%PDF" and len(b)>50000

results = {}
# attempt direct pdf links first
for school, info in scan.items():
    if isinstance(info, dict) and info.get("pdfs"):
        sn = norm(school)
        if sn in have: continue
        done=False
        for plink in info["pdfs"]:
            full = plink if plink.startswith("http") else (info["url"].rsplit("/",1)[0] + "/" + plink if not plink.startswith("//") else "https:"+plink)
            b = curl(full)
            if is_pdf(b):
                fn = os.path.join(SAVEDIR, f"{school}_전문학사_모집요강.pdf")
                open(fn,"wb").write(b)
                results[school] = f"PDF_OK {len(b)}"
                have.add(sn)
                done=True; break
        if not done:
            results[school] = "pdf_link_fail"

json.dump(results, open(r"C:\Users\USER\camnemi-crm\backend\_junior_direct_dl.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
ok=[k for k,v in results.items() if v.startswith("PDF_OK")]
print(f"직접 PDF 다운로드 성공: {len(ok)}개")
for k in ok: print("  ✓",k)
print(f"실패: {[k for k,v in results.items() if not v.startswith('PDF_OK')]}")
