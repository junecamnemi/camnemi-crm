import pymupdf, re, os

SRC = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project\adiga_2026_대학원_모집요강\경운대학교_대학원_모집요강.pdf"
OUT = r"C:\Users\USER\camnemi-crm\backend\경운대_대학원_외국인전형_요약.pdf"

doc = pymupdf.open(SRC)
# find pages mentioning 외국인/이중언어/영어Track/정원외
hit = []
for i in range(len(doc)):
    t = doc[i].get_text()
    if re.search(r"외국인전형|외국인 전형|정원외|이중언어|영어Track|중국어Track|부모 모두 외국", t):
        hit.append(i)
print("외국인 관련 페이지(0-index):", hit)

if not hit:
    print("관련 페이지 없음 — 외국인 내용이 별도 문서일 수 있음")
else:
    new = pymupdf.open()
    for i in hit:
        new.insert_pdf(doc, from_page=i, to_page=i)
    new.save(OUT)
    new.close()
    sz = os.path.getsize(OUT)
    print(f"저장: {OUT} ({sz/1024/1024:.1f} MB), {len(hit)}페이지")
