import pymupdf, os

base = r"C:/Users/USER/내 드라이브/02_Crawling_Sheet/University_Project/adiga_2026_외국인_모집요강/외국인"
outdir = r"C:/Users/USER/camnemi-crm/backend/_w2_txt8/png"
os.makedirs(outdir, exist_ok=True)

jobs = {
    "광주여자대학교": "광주여자대학교[본교]_2026_외국인.pdf",
    "송원대학교": "송원대학교[본교]_2026_외국인.pdf",
}
for name, fn in jobs.items():
    path = os.path.join(base, fn)
    doc = pymupdf.open(path)
    print(f"== {name}: {len(doc)} pages")
    for i, page in enumerate(doc):
        t = page.get_text()
        print(f"  p{i+1}: {len(t)} chars")
        # render every page at 150 dpi for vision fallback
        pix = page.get_pixmap(dpi=150)
        pix.save(os.path.join(outdir, f"{name}_p{i+1:02d}.png"))
    doc.close()
