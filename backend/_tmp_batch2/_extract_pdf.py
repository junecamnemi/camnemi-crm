import sys, os, re
import pymupdf

files = [
 r"C:\Users\USER\camnemi-crm\guides_all\900046_국립한밭대학교_Hanbat National University (HNU)_MA_2026.pdf",
 r"C:\Users\USER\camnemi-crm\guides_all\900070_덕성여자대학교_Duksung Women's University (DSU)_MA_2026.pdf",
 r"C:\Users\USER\camnemi-crm\guides_all\900167_위덕대학교_Uiduk University (UU)_MA_2026.pdf",
 r"C:\Users\USER\camnemi-crm\guides_all\900193_청주대학교_Cheongju University (CJU)_MA_2026.pdf",
 r"C:\Users\USER\camnemi-crm\guides_all\900194_초당대학교_Chodang University (CDU)_MA_2026.pdf",
 r"C:\Users\USER\camnemi-crm\guides_all\900185_중부대학교_Joongbu University (JBU)_MA_2026.pdf",
 r"C:\Users\USER\camnemi-crm\guides_all\0000203_한양대학교_Hanyang University (HYU)_BA_2027.pdf",
 r"C:\Users\USER\camnemi-crm\guides_all\0000204_한양대학교(ERICA)_Hanyang University ERICA (HYU ERICA)_BA_2027.pdf",
 r"C:\Users\USER\camnemi-crm\guides_all\0000141_숙명여자대학교_Sookmyung Women's University (SMWU)_BA_2027.pdf",
 r"C:\Users\USER\camnemi-crm\guides_all\0000072_가톨릭관동대학교_Catholic Kwandong University (CKU)_BA_2027.pdf",
]

kw = re.compile(r'등록금|수업료|입학금|TOPIK|IELTS|토픽|한국어능력|등 록|수업료|책정')

for f in files:
    if not os.path.exists(f):
        print(f"\n\n########## MISSING: {f}")
        continue
    print(f"\n\n########## FILE: {os.path.basename(f)}")
    try:
        doc = pymupdf.open(f)
    except Exception as e:
        print("OPEN ERROR:", e)
        continue
    for i, page in enumerate(doc):
        t = page.get_text()
        if not t.strip():
            continue
        # only print pages containing keywords OR all pages if short
        if kw.search(t) or len(t) < 50:
            print(f"\n----- PAGE {i+1} -----")
            print(t[:3500])
    doc.close()
