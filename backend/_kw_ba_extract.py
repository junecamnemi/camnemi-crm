import pymupdf, os

SRC = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project\adiga_2026_외국인_모집요강\외국인\경운대학교[본교]_2026_외국인.pdf"
OUT = r"C:\Users\USER\camnemi-crm\backend\경운대_학부_외국인전형_요약.pdf"

doc = pymupdf.open(SRC)
new = pymupdf.open()
# 전형안내: PDF p13~p19 (0-index 12..18)
for i in range(12, min(19, len(doc))):
    new.insert_pdf(doc, from_page=i, to_page=i)
new.save(OUT)
new.close(); doc.close()
print(f"저장: {OUT} ({os.path.getsize(OUT)/1024/1024:.2f} MB)")
