import pymupdf, re

p = r"C:\Users\wisew\내 드라이브\02_Crawling_Sheet\University_Project\adiga_2026_대학원_모집요강\경운대학교_대학원_모집요강.pdf"
d = pymupdf.open(p)
t = re.sub(r"[\s\x00-\x1f]+", " ", "\n".join(d[i].get_text() for i in range(len(d))))
d.close()

print("=== 키워드 주변 (일정·전형·등록금·외국인·서류) ===")
for kw in ["모집일정", "전형일정", "원서접수", "지원자격", "전형방법", "선발방법", "등록금", "입학금", "외국인", "제출서류", "전형료", "합격자 발표"]:
    ms = list(re.finditer(re.escape(kw), t))
    for m in ms[:2]:
        seg = t[max(0, m.start()-30):m.start()+260]
        print(f"\n[{kw}] ...{seg}...")
