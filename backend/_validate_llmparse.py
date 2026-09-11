#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate guides_llm_parsed.jsonl (DeepSeek V4-Pro parse) against source PDFs.

For a sample, read the source PDF (by filename) and check whether the parsed
period / topik / ielts / majors are actually present in the PDF text.
Deterministic — no LLM. Outputs a per-record PASS/PARTIAL/FAIL + accuracy stats.
"""
import json, os, re, glob, random

BASE = r"C:\Users\USER\camnemi-crm\backend"
JSONL = os.path.join(BASE, "guides_llm_parsed.jsonl")
UP = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project"

# index all PDFs by filename
PDF_BY_NAME = {}
for p in glob.glob(os.path.join(UP, "**", "*.pdf"), recursive=True):
    PDF_BY_NAME.setdefault(os.path.basename(p), p)

def pdf_text(path, cap=400000):
    import pymupdf
    try:
        doc = pymupdf.open(path)
        t = "\n".join(doc[i].get_text() for i in range(len(doc)))
        doc.close()
        return re.sub(r"[\s\x00-\x1f]+", " ", t)[:cap]
    except Exception:
        return ""

def norm(s):
    return re.sub(r"\s+", "", str(s or ""))

def main():
    rows = [json.loads(l) for l in open(JSONL, encoding="utf-8") if l.strip()]
    random.seed(11)
    sample = random.sample(rows, 40)
    results = []
    for r in sample:
        fn = r.get("_file") or ""
        path = PDF_BY_NAME.get(fn)
        rec = {"school": r.get("school"), "program": r.get("program"), "file": fn,
               "pdf_found": bool(path)}
        if not path:
            rec["verdict"] = "NO_PDF"
            results.append(rec); continue
        txt = norm(pdf_text(path))
        checks = {}
        # period: check digits of the month/day tokens present
        per = r.get("period") or ""
        nums = re.findall(r"\d{1,2}", per)[:6]
        checks["period"] = (bool(nums) and sum(1 for n in nums if n in txt) >= max(1, len(nums)//2)) if per else None
        # topik
        tk = r.get("topik")
        checks["topik"] = (None if tk is None else (f"{tk}" in re.findall(r"(?:TOPIK|한국어능력)[^\d]{0,8}(\d)", txt) or str(tk) in txt))
        # ielts
        ie = r.get("ielts")
        checks["ielts"] = (None if ie is None else (str(ie) in txt))
        # majors: fraction present
        maj = [m for m in (r.get("majors") or []) if m]
        if maj:
            present = sum(1 for m in maj if norm(m) and norm(m) in txt)
            checks["majors"] = (present, len(maj), round(present/len(maj), 2))
        else:
            checks["majors"] = None
        vals = [v for k, v in checks.items() if isinstance(v, bool) and v is not None]
        rec["checks"] = checks
        if checks.get("majors") and isinstance(checks["majors"], tuple):
            mfrac = checks["majors"][2]
        else:
            mfrac = None
        n_ok = sum(1 for v in vals if v)
        n_tot = len(vals)
        if n_tot == 0 and mfrac is None:
            rec["verdict"] = "NO_FIELDS"
        elif (n_tot and n_ok == n_tot) and (mfrac is None or mfrac >= 0.6):
            rec["verdict"] = "PASS"
        elif (n_tot and n_ok >= 1) or (mfrac is not None and mfrac >= 0.3):
            rec["verdict"] = "PARTIAL"
        else:
            rec["verdict"] = "FAIL"
        results.append(rec)

    from collections import Counter
    c = Counter(x["verdict"] for x in results)
    print("=== 샘플 검증 (40개) ===")
    print(dict(c))
    print()
    for x in results:
        print(f"[{x['verdict']}] {x['school']} ({x['program']}) {x.get('file','')[:40]}")
        if x.get("checks"):
            print("    ", {k: v for k, v in x["checks"].items() if v is not None})
    json.dump(results, open(os.path.join(BASE, "_llmparse_validation.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

if __name__ == "__main__":
    main()
