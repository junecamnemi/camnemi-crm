# -*- coding: utf-8 -*-
import json, os, re, sys
import pymupdf  # PyMuPDF

BACK = r"C:/Users/USER/camnemi-crm/backend"

def norm(p):
    p = p.replace("\\\\", "/").replace("\\", "/")
    return p

def load(name):
    with open(os.path.join(BACK, name), encoding="utf-8") as f:
        return json.load(f)

# Each candidate file maps to a dept we are verifying.
groups = {
    "_medcat_dental.json": "치의예과",
    "_medcat_oriental.json": "한의예과",
    "_medcat_vet.json": "수의예과",
}

all_pdf = []
for fn, dept in groups.items():
    for c in load(fn):
        path = norm(c["path"])
        if not os.path.exists(path):
            print("MISSING:", path)
            continue
        all_pdf.append({"school": c["school"], "year": c["year"], "dept": dept, "path": path})

# dedupe by path
seen = {}
for c in all_pdf:
    seen.setdefault(c["path"], c)
print("unique PDFs:", len(seen))

def extract_text(path):
    doc = pymupdf.open(path)
    pages = []
    for pg in doc:
        pages.append(pg.get_text())
    return pages

# Store extracted text per unique pdf
cache = {}
for path, c in seen.items():
    try:
        cache[path] = extract_text(path)
        total = sum(len(t) for t in cache[path])
        print(f"OK pages={len(cache[path])} chars={total} :: {c['school']} {c['year']} {c['dept']}")
    except Exception as e:
        print("ERR", path, e)

# Save text to disk for analysis
os.makedirs(r"C:/Users/USER/camnemi-crm/_curation_tmp/medcat_dentalvet", exist_ok=True)
meta = []
for path, c in seen.items():
    txt = "\n<<<PAGEBREAK>>>\n".join(cache.get(path, []))
    out = os.path.join(r"C:/Users/USER/camnemi-crm/_curation_tmp/medcat_dentalvet", f"{c['school']}_{c['year']}_{c['dept']}.txt")
    with open(out, "w", encoding="utf-8") as f:
        f.write(txt)
    meta.append({"school": c["school"], "year": c["year"], "dept": c["dept"], "path": path, "txt": out})
with open(r"C:/Users/USER/camnemi-crm/_curation_tmp/medcat_dentalvet/_meta.json", "w", encoding="utf-8") as f:
    json.dump(meta, f, ensure_ascii=False, indent=1)
print("done extraction")
