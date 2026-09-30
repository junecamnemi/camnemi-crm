import os
from pypdf import PdfReader
names=["남부대","남서울대","단국대","대구가톨릭대","대구대","대구한의대","대신대","대전대","대진대","덕성여자대","동국대","동덕여자대","동명대"]
d=os.getcwd()
for n in names:
    f=f"{n}_한국어교육원.pdf"
    p=os.path.join(d,f)
    if not os.path.exists(p):
        print(f"{n}: MISSING"); continue
    head=open(p,'rb').read(5)
    try:
        r=PdfReader(p)
        npg=len(r.pages)
        txt=""
        for pg in r.pages:
            try: txt+=(pg.extract_text() or "")
            except: pass
        t=txt.strip().replace("\n"," ")[:150]
        print(f"{n}: valid={head==b'%PDF-'} pages={npg} size={os.path.getsize(p)} chars={len(txt.strip())} | {t!r}")
    except Exception as e:
        print(f"{n}: ERROR {type(e).__name__}: {e}")
