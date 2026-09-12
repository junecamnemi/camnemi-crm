import pymupdf, re, json, os

p = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project\adiga_2026_대학원_모집요강\동의대학교_대학원_모집요강.pdf"
d = pymupdf.open(p)
t = re.sub(r"[\s\x00-\x1f]+", " ", "\n".join(d[i].get_text() for i in range(len(d))))
d.close()
print("=== 동의대 대학원 요강 주요 구문 ===")
for kw in ["지원자격", "TOPIK", "한국어능력", "순수외국인", "외국인 전형", "어학성적"]:
    for m in list(re.finditer(kw, t))[:2]:
        print(f"[{kw}] ...{t[max(0, m.start()-60):m.start()+160]}...")
    print()

print("=== KB 재외국민 언급 위치 ===")
kb = json.load(open(r"C:\Users\USER\camnemi-crm\backend\verified_kb.json", encoding="utf-8"))
def walk(o, path=""):
    if isinstance(o, dict):
        for k, v in o.items():
            walk(v, path + "/" + str(k))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            if isinstance(v, str) and "재외국민" in v:
                print(f"  {path}[{i}]: {v[:150]}")
    elif isinstance(o, str) and "재외국민" in o:
        print(f"  {path}: {o[:150]}")
walk(kb)
