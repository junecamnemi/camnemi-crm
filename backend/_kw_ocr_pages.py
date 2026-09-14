import pymupdf, numpy as np, re
from rapidocr_onnxruntime import RapidOCR

SRC = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project\adiga_2026_외국인_모집요강\외국인\경운대학교[본교]_2026_외국인.pdf"
d = pymupdf.open(SRC)
ocr = RapidOCR()
targets = [0, 1, 2, 3, 4, 5, 6, 12]  # low-text pages
for i in targets:
    pix = d[i].get_pixmap(dpi=170)
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
    if pix.n == 4:
        img = img[:, :, :3]
    res, _ = ocr(img)
    txt = "\n".join(r[1] for r in res) if res else ""
    txt = re.sub(r"\s+", " ", txt)
    flag = "★장학" if re.search(r"장학|수업료|등록금|100%|70%|50%|20%", txt) else ""
    print(f"--- p{i+1} ({len(txt)}자) {flag} ---")
    print(txt[:700])
    print()
d.close()
