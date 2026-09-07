# -*- coding: utf-8 -*-
"""Identify junior colleges whose 'acquired' PDF is NOT a foreigner-specific guide.
For each, find the proper 외국인/유학생 admission page and note it for redownload.
Save a needs-redo list + the correct foreigner admission URL if discoverable."""
import pymupdf, os, re, json, subprocess, urllib.parse

KB = json.load(open(r"C:\Users\USER\camnemi-crm\backend\verified_kb.json", encoding="utf-8"))
js = KB["junior"]["schools"]
SAVEDIR = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project\adiga_2026_전문대학_모집요강"

FOREIGN_KW = re.compile(r'외국인|유학생|순수외국인|재외국민|international|foreign|D-4|D4|유학')

def curl(url, timeout=20):
    try:
        return subprocess.run(["curl","-sL","-A","Mozilla/5.0","--max-time",str(timeout),url],capture_output=True).stdout
    except: return b""

# For each school that has a render PDF lacking foreigner keyword, find the foreigner page
redo = []
for fn in sorted(os.listdir(SAVEDIR)):
    if not fn.endswith(".pdf"): continue
    school = re.sub(r"_전문학사_.*", "", fn)
    # check content
    try:
        d=pymupdf.open(os.path.join(SAVEDIR,fn))
        t=' '.join(d[i].get_text() for i in range(min(6,len(d))))
        d.close()
    except: continue
    if FOREIGN_KW.search(t): continue  # already foreigner-focused
    # has foreigner keyword in KB topik etc but PDF is generic
    v = js.get(school,{})
    gu = v.get("guide_url","")
    redo.append({"school": school, "file": fn, "guide_url": gu, "text_len": len(t.strip())})

json.dump(redo, open(r"C:\Users\USER\camnemi-crm\backend\_junior_need_foreign.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"외국인 전형 아닌(재확보 필요) PDF: {len(redo)}")
for r in redo:
    print(f"  {r['school']} | {r['file']}")
