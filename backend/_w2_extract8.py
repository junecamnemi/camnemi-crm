import pymupdf, json, os, re, sys

base = r"C:/Users/USER/내 드라이브/02_Crawling_Sheet/University_Project/adiga_2026_외국인_모집요강/외국인"
files = {
    "인천대학교": "0002660_인천대학교[본교]_2026_외국인.pdf",
    "신한대학교": "0002800_신한대학교[제2캠퍼스]_2026_외국인.pdf",
    "상명대학교": "0002959_상명대학교[제2캠퍼스]_2026_외국인.pdf",
    "영산대학교(본교)": "0003193_영산대학교[본교]_2026_외국인.pdf",
    "영산대학교(제2캠퍼스)": "0003194_영산대학교[제2캠퍼스]_2026_외국인.pdf",
    "경운대학교": "경운대학교[본교]_2026_외국인.pdf",
    "광주여자대학교": "광주여자대학교[본교]_2026_외국인.pdf",
    "국립금오공과대학교": "국립금오공과대학교[본교]_2026_외국인.pdf",
    "송원대학교": "송원대학교[본교]_2026_외국인.pdf",
}

outdir = r"C:/Users/USER/camnemi-crm/backend/_w2_txt8"
os.makedirs(outdir, exist_ok=True)
report = {}
for name, fn in files.items():
    path = os.path.join(base, fn)
    if not os.path.exists(path):
        report[name] = {"exists": False, "pages": 0, "chars": 0}
        print(f"MISSING: {name} -> {path}")
        continue
    doc = pymupdf.open(path)
    pages_text = []
    total = 0
    for i, page in enumerate(doc):
        t = page.get_text()
        pages_text.append(t)
        total += len(t)
    txt = "\n\n===PAGE_BREAK===\n\n".join(pages_text)
    safe = re.sub(r'[\\/:*?"<>|]', "_", name)
    with open(os.path.join(outdir, safe + ".txt"), "w", encoding="utf-8") as f:
        f.write(txt)
    report[name] = {"exists": True, "pages": len(doc), "chars": total, "txtfile": safe + ".txt"}
    print(f"{name}: pages={len(doc)}, chars={total}")
    doc.close()

with open(os.path.join(outdir, "_report.json"), "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=1)
