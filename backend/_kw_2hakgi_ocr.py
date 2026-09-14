import pymupdf, numpy as np, re, os
from rapidocr_onnxruntime import RapidOCR

p = os.path.join(os.environ.get("LOCALAPPDATA", r"C:\Users\USER\AppData\Local"), "Temp", "kw_2hakgi.pdf")
d = pymupdf.open(p)
print("페이지별 텍스트/이미지:")
low = []
for i in range(len(d)):
    t = d[i].get_text()
    imgs = len(d[i].get_images())
    print(f"  p{i+1}: text={len(t)} imgs={imgs}  {re.sub(r'  +',' ',t)[:50]!r}")
    if len(t) < 400:
        low.append(i)
print("\n저텍스트 페이지:", [i+1 for i in low])

if low:
    ocr = RapidOCR()
    for i in low:
        pix = d[i].get_pixmap(dpi=150)
        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
        if pix.n == 4: img = img[:, :, :3]
        res, _ = ocr(img)
        txt = re.sub(r"\s+", " ", "\n".join(r[1] for r in res) if res else "")
        flag = "★장학" if re.search(r"장학|수업료|100%|70%|50%|20%", txt) else ""
        print(f"\n--- p{i+1} OCR ({len(txt)}자) {flag} ---")
        print(txt[:800])
d.close()
