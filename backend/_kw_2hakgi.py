import pymupdf, re, os

p = os.path.join(os.environ.get("LOCALAPPDATA", r"C:\Users\USER\AppData\Local"), "Temp", "kw_2hakgi.pdf")
d = pymupdf.open(p)
t = re.sub(r"[\s\x00-\x1f]+", " ", "\n".join(d[i].get_text() for i in range(len(d))))
n = len(d)
d.close()
print(f"후기 요강: {n}페이지, {len(t)}자")
print("\n=== 장학/등록금 키워드 ===")
for kw in ["장학", "수업료", "등록금", "100%", "70%", "50%", "20%", "TOPIK 5", "TOPIK 4", "면제", "행복"]:
    print(f"  '{kw}': {len(re.findall(re.escape(kw), t))}회")
print("\n=== '장학' 문맥 ===")
for m in list(re.finditer("장학", t))[:5]:
    print(f"  ...{t[max(0,m.start()-70):m.start()+200]}...\n")
