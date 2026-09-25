import pymupdf, re, json

SRC = r"C:\Users\wisew\내 드라이브\02_Crawling_Sheet\University_Project\adiga_2026_외국인_모집요강\외국인\경운대학교[본교]_2026_외국인.pdf"
d = pymupdf.open(SRC)
t = re.sub(r"[\s\x00-\x1f]+", " ", "\n".join(d[i].get_text() for i in range(len(d))))
d.close()
print(f"학부 PDF 총 {len(t)}자")
print("\n=== 장학금 관련 키워드 존재 여부 ===")
for kw in ["장학", "수업료", "등록금", "100%", "70%", "50%", "20%", "TOPIK 5", "TOPIK 4", "면제"]:
    n = len(re.findall(re.escape(kw), t))
    print(f"  '{kw}': {n}회")
print("\n=== '장학' 주변 문맥 ===")
for m in list(re.finditer("장학", t))[:4]:
    print(f"  ...{t[max(0,m.start()-80):m.start()+140]}...\n")
print("=== KB scholarships_categorized 출처 필드 ===")
kb = json.load(open(r"C:\Users\wisew\camnemi-crm\backend\verified_kb.json", encoding="utf-8"))
v = kb["schools"]["경운대학교"]
print("  guide_curated:", v.get("guide_curated"))
print("  notes_curated:", v.get("notes_curated"))
print("  _llm_parsed:", v.get("_llm_parsed"))
