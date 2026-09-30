import json, re, pathlib, collections
import pymupdf as fitz
conf = json.load(open("_pg_year_conflicts.json", encoding="utf-8"))
for c in conf:
    p = pathlib.Path(c["path"])
    print("=" * 72)
    print(p.name)
    if not p.exists():
        print("  MISSING"); continue
    doc = fitz.open(p)
    n = doc.page_count
    full = "".join(doc[i].get_text() for i in range(n))
    doc.close()
    print("  pages:", n, "| total chars:", len(full))
    print("  years seen:", dict(collections.Counter(re.findall(r"20\d\d", full)).most_common(8)))
    for kw in ("학년도", "모집요강", "접수", "마감"):
        m = [x.strip() for x in re.findall(r"[^\n]{0,45}" + kw + r"[^\n]{0,45}", full)][:3]
        if m: print(f"  [{kw}]", " || ".join(m)[:230])
    print("  HEAD:", full[:160].replace("\n", " "))
