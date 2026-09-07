
import pymupdf, sys, json
path = sys.argv[1]
doc = pymupdf.open(path)
pages = []
for i, p in enumerate(doc):
    t = p.get_text()
    pages.append({"page": i+1, "chars": len(t), "text": t})
print(json.dumps(pages, ensure_ascii=False))
