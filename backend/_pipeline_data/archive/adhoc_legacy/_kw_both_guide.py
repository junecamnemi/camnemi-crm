import pymupdf, re

files = {
    "학부(외국인)": r"C:\Users\wisew\내 드라이브\02_Crawling_Sheet\University_Project\adiga_2026_외국인_모집요강\외국인\경운대학교[본교]_2026_외국인.pdf",
    "대학원": r"C:\Users\wisew\내 드라이브\02_Crawling_Sheet\University_Project\adiga_2026_대학원_모집요강\경운대학교_대학원_모집요강.pdf",
}
for label, p in files.items():
    d = pymupdf.open(p)
    t = re.sub(r"[\s\x00-\x1f]+", " ", "\n".join(d[i].get_text() for i in range(len(d))))
    d.close()
    print(f"===== {label} ({len(t)}자) =====")
    for kw in ["등록금", "장학제도", "장학금명", "행복"]:
        for m in list(re.finditer(re.escape(kw), t))[:2]:
            print(f"  [{kw}] ...{t[max(0,m.start()-60):m.start()+180]}...")
    print()
