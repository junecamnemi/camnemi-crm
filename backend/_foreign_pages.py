# -*- coding: utf-8 -*-
"""For each school needing a foreigner-only guide, search its guide_url domain for
the 외국인/유학생 admission page, then find the 모집요강 PDF there. Pure curl."""
import json, os, re, subprocess, urllib.parse, time

KB = json.load(open(r"C:\Users\USER\camnemi-crm\backend\verified_kb.json", encoding="utf-8"))
js = KB["junior"]["schools"]
SAVEDIR = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project\adiga_2026_전문대학_모집요강"

def curl(url, timeout=18):
    try:
        return subprocess.run(["curl","-sL","-A","Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120","--max-time",str(timeout),url],capture_output=True).stdout
    except: return b""

def is_pdf(b): return b[:4]==b"%PDF" and len(b)>20000

# load the redo list schools
redo = [r["school"] for r in json.load(open(r"C:\Users\USER\camnemi-crm\backend\_junior_foreign_class.json",encoding="utf-8"))["redownload"]]

# keyword pages to probe on each site
PROBE_PATH = ["/international", "/global", "/ipsi", "/foreign", "/intl",
              "/admission", "/입학", "/유학생", "/oia"]

results={}
for school in redo:
    gu = js.get(school,{}).get("guide_url","")
    if not gu: 
        results[school]={"url":"","note":"no guide_url"}; continue
    base = urllib.parse.urlparse(gu)
    domain = f"{base.scheme}://{base.netloc}"
    # try common foreigner paths
    found_url=None; found_pdf=None
    # first, fetch guide_url and look for 외국인/유학 menu links
    html=curl(gu)
    if html:
        txt=html.decode("utf-8","ignore")
        # find links whose text has 외국인/유학/국제 and pdf links
        for m in re.finditer(r'<a[^>]+href="([^"]+)"[^>]*>([^<]{0,30})</a>', txt):
            href,text=m.group(1),m.group(2)
            if re.search(r'외국인|유학|국제|foreign|intl', text, re.I):
                full=urllib.parse.urljoin(gu,href)
                found_url=full
                break
        # also direct pdf
        for m in re.finditer(r'href="([^"]*\.pdf[^"]*)"', txt, re.I):
            pdf_url=urllib.parse.urljoin(gu,m.group(1))
            pb=curl(pdf_url)
            if is_pdf(pb):
                # check content has foreigner
                import io
                try:
                    import pymupdf
                    doc=pymupdf.open(stream=pb,filetype="pdf")
                    pt=" ".join(doc[i].get_text() for i in range(min(3,len(doc))))
                    doc.close()
                    if re.search(r'외국인|유학',pt):
                        results[school]={"url":gu,"pdf":pdf_url,"size":len(pb)}
                        break
                except: pass
    if school not in results:
        results[school]={"url":found_url or gu,"pdf":None,"note":"foreign page url found but pdf unknown" if found_url else "no foreign page found"}
    time.sleep(0.2)

json.dump(results, open(r"C:\Users\USER\camnemi-crm\backend\_junior_foreign_pages.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
n_pdf=sum(1 for v in results.values() if v.get("pdf"))
print(f"외국인 페이지 처리 {len(results)} | PDF직접확보 {n_pdf}")
for s,v in results.items():
    if v.get("pdf"): print(f"  ✓ {s}: PDF {v['size']}")
    else: print(f"  · {s}: page={v.get('url','')[:60]}")
