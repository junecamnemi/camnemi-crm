import sys, os, json, warnings
warnings.filterwarnings("ignore")
import pymupdf

BATCH = [
    {"name": "가톨릭대", "path": r"C:/Users/USER/내 드라이브/02_Crawling_Sheet/University_Project/adiga_2026_대학원_모집요강/가톨릭대_2026후기1차_일반대학원.pdf"},
    {"name": "국민대", "path": r"C:/Users/USER/내 드라이브/02_Crawling_Sheet/University_Project/adiga_2026_대학원_모집요강/국민대_2026전기_일반대학원_국문.pdf"},
    {"name": "인제대", "path": r"C:/Users/USER/내 드라이브/02_Crawling_Sheet/University_Project/adiga_2026_대학원_모집요강/인제대_대학원_모집요강.pdf"},
    {"name": "전주대", "path": r"C:/Users/USER/내 드라이브/02_Crawling_Sheet/University_Project/adiga_2026_대학원_모집요강/전주대_대학원_모집요강.pdf"},
    {"name": "제주국제대", "path": r"C:/Users/USER/내 드라이브/02_Crawling_Sheet/University_Project/adiga_2026_대학원_모집요강/제주국제대_대학원_모집요강.pdf"},
    {"name": "조선대", "path": r"C:/Users/USER/내 드라이브/02_Crawling_Sheet/University_Project/adiga_2026_대학원_모집요강/조선대_대학원_모집요강.pdf"},
    {"name": "중부대", "path": r"C:/Users/USER/내 드라이브/02_Crawling_Sheet/University_Project/adiga_2026_대학원_모집요강/중부대_대학원_모집요강.pdf"},
    {"name": "창신대", "path": r"C:/Users/USER/내 드라이브/02_Crawling_Sheet/University_Project/adiga_2026_대학원_모집요강/창신대_대학원_모집요강.pdf"},
]

os.makedirs("backend/_curation_ma_txt", exist_ok=True)
for s in BATCH:
    name = s["name"]
    try:
        doc = pymupdf.open(s["path"])
        out = []
        for i, page in enumerate(doc):
            out.append(f"\n===== PAGE {i+1} =====\n")
            out.append(page.get_text("text"))
        text = "".join(out)
        fn = f"backend/_curation_ma_txt/{name}.txt"
        with open(fn, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"{name}: {len(doc)} pages, {len(text)} chars -> {fn}")
    except Exception as e:
        print(f"{name}: ERROR {e}")
