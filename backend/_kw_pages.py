import pymupdf, re

SRC = r"C:\Users\wisew\내 드라이브\02_Crawling_Sheet\University_Project\adiga_2026_외국인_모집요강\외국인\경운대학교[본교]_2026_외국인.pdf"
d = pymupdf.open(SRC)
print(f"총 {len(d)}페이지")
print(f"{'p':>3} {'text_len':>8} {'imgs':>5}  head")
low = []
for i in range(len(d)):
    t = d[i].get_text()
    imgs = len(d[i].get_images())
    head = re.sub(r"\s+", " ", t)[:60]
    print(f"{i+1:>3} {len(t):>8} {imgs:>5}  {head}")
    if len(t) < 200 or (imgs and len(t) < 600):
        low.append(i)
d.close()
print("\n텍스트 부족/이미지 페이지(0-idx):", low)
