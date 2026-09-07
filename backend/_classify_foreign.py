# -*- coding: utf-8 -*-
"""For each 'suspect' PDF (no foreigner keyword in first pages), do a FULL-text scan
for 외국인 admission section. Real full 요강 PDFs may have foreigner section deeper.
Separate: (a) genuinely non-foreigner renders -> must redownload foreigner page,
(b) full guides that DO contain a foreigner section -> keep but extract section."""
import pymupdf, os, re, json

SAVEDIR = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project\adiga_2026_전문대학_모집요강"
suspects = json.load(open(r"C:\Users\USER\camnemi-crm\backend\_junior_need_foreign.json", encoding="utf-8"))

FOREIGN_STRONG = re.compile(r'순수외국인|외국인\s*전형|외국인\s*특별|재외국민과\s*외국인|외국인\s*모집|유학생\s*모집|외국인\s*유학생', re.I)
FOREIGN_WEAK = re.compile(r'외국인|유학', re.I)

redownload=[]   # truly no foreigner content -> need foreigner page
keep_with_sec=[] # has foreigner section deeper
for r in suspects:
    fn = r["file"]
    fp = os.path.join(SAVEDIR, fn)
    try:
        d=pymupdf.open(fp)
        # full text + find foreigner section context
        pages=[d[i].get_text() for i in range(len(d))]
        d.close()
        full="\n".join(pages)
    except Exception as e:
        redownload.append({**r,"reason":"unreadable"})
        continue
    is_render = "렌더" in fn
    strong = FOREIGN_STRONG.search(full)
    weak = FOREIGN_WEAK.search(full)
    if is_render:
        # render must have clear foreigner admission; else redownload
        if strong or (weak and len(re.findall(r'외국인|유학',full))>=2):
            keep_with_sec.append({**r,"section":"render-with-foreign","count":len(re.findall(r'외국인|유학',full))})
        else:
            redownload.append({**r,"reason":"render-no-foreign"})
    else:
        # real guide: keep if any foreigner mention (full guide likely has 석사/외국인 section)
        if weak:
            keep_with_sec.append({**r,"section":"guide-has-foreign","count":len(re.findall(r'외국인|유학',full))})
        else:
            redownload.append({**r,"reason":"guide-no-foreign-at-all"})

json.dump({"redownload":redownload,"keep":keep_with_sec}, open(r"C:\Users\USER\camnemi-crm\backend\_junior_foreign_class.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"재확보 필요(외국인 없음): {len(redownload)}")
for r in redownload: print(f"  ✗ {r['school']} ({r['reason']})")
print(f"\n유지(외국인 포함): {len(keep_with_sec)}")
