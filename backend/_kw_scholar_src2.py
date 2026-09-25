import pymupdf, re, json, glob, os

# 1) 대학원 요강에 장학 티어가 있나?
grad = r"C:\Users\wisew\내 드라이브\02_Crawling_Sheet\University_Project\adiga_2026_대학원_모집요강\경운대학교_대학원_모집요강.pdf"
d = pymupdf.open(grad)
tg = re.sub(r"[\s\x00-\x1f]+", " ", "\n".join(d[i].get_text() for i in range(len(d))))
d.close()
print("=== 대학원 요강 장학 키워드 ===")
for kw in ["수업료", "장학", "100%", "70%", "50%", "20%", "TOPIK 5", "TOPIK 4", "외국인 신입"]:
    print(f"  '{kw}': {len(re.findall(re.escape(kw), tg))}회")
m = re.search(r"외국인 신입.{0,400}", tg)
print("\n' 외국인 신입' 문맥:", m.group(0) if m else "없음")

# 2) 어학연수 요강
lang = r"C:\Users\wisew\내 드라이브\02_Crawling_Sheet\University_Project\adiga_2026_어학연수_모집요강\경운대_한국어교육원.pdf"
if os.path.exists(lang):
    d = pymupdf.open(lang)
    tl = re.sub(r"[\s\x00-\x1f]+", " ", "\n".join(d[i].get_text() for i in range(len(d))))
    d.close()
    print(f"\n=== 어학연수 요강 ({len(tl)}자) 장학 키워드 ===")
    for kw in ["수업료", "장학", "100%", "TOPIK 5", "TOPIK 4"]:
        print(f"  '{kw}': {len(re.findall(re.escape(kw), tl))}회")

# 3) KB에 장학금 출처 필드가 있나?
kb = json.load(open(r"C:\Users\wisew\camnemi-crm\backend\verified_kb.json", encoding="utf-8"))
v = kb["schools"]["경운대학교"]
print("\n=== KB 경운대 학부 필드 중 '출처' 관련 ===")
for k in v:
    if any(t in k.lower() for t in ["source", "src", "url", "guide", "curated", "verified"]):
        print(f"  {k}: {json.dumps(v[k], ensure_ascii=False)[:200]}")
