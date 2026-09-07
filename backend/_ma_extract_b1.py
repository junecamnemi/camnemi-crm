# -*- coding: utf-8 -*-
import fitz, json, os

jobs = [
    ("청주대", "C:/Users/USER/내 드라이브/02_Crawling_Sheet/University_Project/adiga_2026_대학원_모집요강/청주대_대학원_모집요강.pdf"),
    ("초당대", "C:/Users/USER/내 드라이브/02_Crawling_Sheet/University_Project/adiga_2026_대학원_모집요강/초당대_대학원_모집요강.pdf"),
    ("충북대", "C:/Users/USER/내 드라이브/02_Crawling_Sheet/University_Project/adiga_2026_대학원_모집요강/충북대_대학원_모집요강.pdf"),
]
os.makedirs("backend/_ma_batch1_txt", exist_ok=True)
for name, p in jobs:
    try:
        doc = fitz.open(p)
        txt = "\n".join("===PAGE %d===\n%s" % (i + 1, pg.get_text()) for i, pg in enumerate(doc))
        out = "backend/_ma_batch1_txt/" + name + ".txt"
        open(out, "w", encoding="utf-8").write(txt)
        print(name, len(doc), "pages", len(txt), "chars")
    except Exception as ex:
        print(name, "ERROR", repr(ex))
