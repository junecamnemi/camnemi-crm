# -*- coding: utf-8 -*-
"""Which KB-referenced guide_pdf files are NOT real PDFs (HTML/HWP/churn)?"""
import json, os, collections
HERE = os.path.dirname(os.path.abspath(__file__))
kb = json.load(open(os.path.join(HERE, "verified_kb.json"), encoding="utf-8"))
SEC = {"ba": kb.get("schools", {}), "ma": kb.get("master", {}).get("schools", {}),
       "junior": kb.get("junior", {}).get("schools", {}),
       "lang": kb.get("lang_programs", {}).get("schools", {})}
HTML = (b"<!DO", b"<!do", b"<html", b"<HTML", b"<?xm")
out = []
for lv, sec in SEC.items():
    c = collections.Counter()
    for name, v in sec.items():
        if not isinstance(v, dict):
            continue
        p = None
        for k in ("guide_effective_pdf", "guide_pdf"):
            x = v.get(k)
            if isinstance(x, str) and x.lower().endswith((".pdf", ".hwp")):
                p = x
                break
        if not p or not os.path.exists(p):
            c["missing_file"] += 1
            continue
        try:
            head = open(p, "rb").read(8)
        except Exception:
            c["unreadable"] += 1
            continue
        if head[:4] == b"%PDF":
            c["real_pdf"] += 1
        elif head[:4] == b"\xd0\xcf\x11\xe0":
            c["hwp"] += 1
            out.append({"school": name, "level": lv, "path": p, "kind": "hwp"})
        else:
            c["fake_pdf_html"] += 1
            out.append({"school": name, "level": lv, "path": p, "kind": "html_as_pdf"})
    print("%-7s %s" % (lv, dict(c)))
print("\ntotal non-PDF guide files:", len(out))
json.dump(out, open(os.path.join(HERE, "_fake_pdf_files.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
for r in out[:25]:
    print("  ", r["level"], r["school"], r["kind"], os.path.basename(r["path"])[:60])