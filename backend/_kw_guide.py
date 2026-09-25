import pymupdf, re

p = r"C:\Users\wisew\내 드라이브\02_Crawling_Sheet\University_Project\adiga_2026_대학원_모집요강\경운대학교_대학원_모집요강.pdf"
d = pymupdf.open(p)
t = re.sub(r"[\s\x00-\x1f]+", " ", "\n".join(d[i].get_text() for i in range(len(d))))
d.close()
print(f"PDF 총 {len(t)}자\n")
print("=== 머리 (1~2000자) ===")
print(t[:2000])
