import json, os, re, sys
sys.path.insert(0, r"C:/Users/USER/camnemi-crm")
import pymupdf

d = json.load(open(r"C:/Users/USER/camnemi-crm/backend/_medcat_nurse0.json", encoding='utf-8'))
outdir = r"C:/Users/USER/camnemi-crm/backend/_curation_tmp/nurse0_pages"
os.makedirs(outdir, exist_ok=True)

KW = ['간호']

for e in d:
    school = e['school']; year = e['year']; path = e['path']
    doc = pymupdf.open(path)
    hits = []
    for i, page in enumerate(doc):
        t = page.get_text()
        if '간호' in t:
            hits.append((i, t))
    fname = outdir + f"/{school}_{year}.txt"
    with open(fname, 'w', encoding='utf-8') as f:
        f.write(f"### {school} {year} | total pages {len(doc)} | pages mentioning 간호: {len(hits)}\n\n")
        for i, t in hits:
            f.write(f"----- PAGE {i+1} -----\n{t}\n")
    print(f"{school} {year}: {len(hits)} pages w/ 간호 out of {len(doc)}")
    doc.close()
