# -*- coding: utf-8 -*-
"""Attempt fileDown/download links for remaining junior schools."""
import json, os, re, subprocess, time

KB = json.load(open(r"C:\Users\USER\camnemi-crm\backend\verified_kb.json", encoding="utf-8"))
js = KB["junior"]["schools"]
SAVEDIR = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project\adiga_2026_전문대학_모집요강"
scan = json.load(open(r"C:\Users\USER\camnemi-crm\backend\_junior_scan_urls.json", encoding="utf-8"))

def norm(s): return s.replace("대학교","").replace("대학","").replace("전문대","").replace(" ","")
have = set(norm(os.path.splitext(f)[0].replace("_전문학사_모집요강","")) for f in os.listdir(SAVEDIR) if f.endswith(".pdf"))

def curl(url, timeout=25):
    try:
        return subprocess.run(["curl","-sL","-A","Mozilla/5.0","--max-time",str(timeout),url],capture_output=True).stdout
    except: return b""

def is_pdf(b): return b[:4]==b"%PDF" and len(b)>30000

results={}
for school, info in scan.items():
    if not isinstance(info, dict): continue
    sn = norm(school)
    if sn in have: continue
    fl = info.get("file_links") or []
    if not fl: continue
    done=False
    for l in fl:
        full = l if l.startswith("http") else (("https:"+l) if l.startswith("//") else (info["url"].rsplit("/",1)[0]+"/"+l))
        b = curl(full)
        if is_pdf(b):
            open(os.path.join(SAVEDIR,f"{school}_전문학사_모집요강.pdf"),"wb").write(b)
            results[school]=f"OK {len(b)}"; have.add(sn); done=True; break
        elif b[:4]==b"%PDF":
            # small pdf - still save but flag
            open(os.path.join(SAVEDIR,f"{school}_전문학사_모집요강.pdf"),"wb").write(b)
            results[school]=f"OK_small {len(b)}"; have.add(sn); done=True; break
    if not done: results[school]="fail"
    time.sleep(0.3)

json.dump(results, open(r"C:\Users\USER\camnemi-crm\backend\_junior_filedown_dl.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
ok=[k for k,v in results.items() if v.startswith("OK")]
print(f"fileDown 성공: {len(ok)}개", ok)
print(f"실패: {[k for k,v in results.items() if v=='fail']}")
