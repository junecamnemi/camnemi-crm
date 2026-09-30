import json, re, pathlib, collections
conf = json.load(open("_pg_year_conflicts.json", encoding="utf-8"))
import fitz
for c in conf:
    p = pathlib.Path(c["path"])
    print("=" * 70)
    print(p.name, "| exists:", p.exists(), "| KB says", c["kb_effective_year"], "| file year", c["label_year"])
    if not p.exists():
        continue
    doc = fitz.open(p)
    txt = ""
    for i in range(min(3, doc.page_count)):
        txt += doc[i].get_text()
    hits = collections.Counter(re.findall(r"20\d\d\s*(?:학년도|학년)", txt))
    plain = collections.Counter(re.findall(r"(20\d\d)\.\s*\d{1,2}\.\s*\d{1,2}", txt))
    print("  pages:", doc.page_count, "| text chars(first3):", len(txt))
    print("  '20xx학년도' hits:", dict(hits.most_common(6)))
    print("  date-prefix years:", dict(plain.most_common(5)))
    m = re.search(r"[^\n]{0,60}(?:모집요강|신입생|외국인)[^\n]{0,60}", txt)
    print("  first title-ish line:", (m.group(0).strip()[:110] if m else txt[:110].replace("\n", " ")))
    doc.close()
