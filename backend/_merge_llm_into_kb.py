#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Merge LLM(pro)-parsed guides into verified_kb.json (fill-only, source-tagged).

Sources:
  guides_llm_parsed.jsonl      -> keep only records whose source PDF had >=1000 chars text (trusted)
  guides_llm_parsed_ocr.jsonl  -> OCR-based re-parse (pro), trusted (OCR text)
Fill rules: never overwrite an existing KB value. Add majors when absent. Tag every
touched field's origin in `_llm_parsed` so it stays auditable.

Usage: python _merge_llm_into_kb.py [--write]
"""
import json, os, glob, re, argparse, shutil, datetime

BASE = r"C:\Users\USER\camnemi-crm\backend"
KB = os.path.join(BASE, "verified_kb.json")
J1 = os.path.join(BASE, "guides_llm_parsed.jsonl")
J2 = os.path.join(BASE, "guides_llm_parsed_ocr.jsonl")
TRUST = os.path.join(BASE, "_llmparse_trust.json")
UP = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project"

PDF_BY_NAME = {}
for p in glob.glob(os.path.join(UP, "**", "*.pdf"), recursive=True):
    PDF_BY_NAME.setdefault(os.path.basename(p), p)

def tlen(path):
    import pymupdf
    try:
        d = pymupdf.open(path); n = sum(len(d[i].get_text()) for i in range(len(d))); d.close(); return n
    except Exception:
        return -1

def norm(s):
    return re.sub(r"[^가-힣a-zA-Z0-9]", "", str(s or "")).replace("대학교", "").replace("대학", "")

def load(path):
    if not os.path.exists(path): return []
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--write", action="store_true"); args = ap.parse_args()
    kb = json.load(open(KB, encoding="utf-8"))
    sections = {"ba": ("schools", None), "ma": ("master", "schools"), "lang": ("lang_programs", "schools"), "junior": ("junior", "schools")}

    def section_dict(sec):
        a, b = sections[sec]
        return kb[a][b] if b else kb[a]

    # build key index per section
    idx = {s: {norm(k): k for k in section_dict(s)} for s in sections}

    recs = []
    for r in load(J1):
        fn = r.get("_file") or ""
        p = PDF_BY_NAME.get(fn)
        if p and tlen(p) >= 1000:
            r["_trusted"] = True; recs.append(r)
    recs += load(J2)
    print(f"병합 대상: {len(recs)} (trusted {sum(1 for r in recs if r.get('_trusted'))} + OCR {sum(1 for r in recs if not r.get('_trusted'))})")

    stats = {"matched": 0, "unmatched": 0, "majors_added": 0, "period_filled": 0, "lang_filled": 0}
    unmatched = set()
    for r in recs:
        sec = (r.get("program") or "ba").strip()
        if sec not in sections: sec = "ba"
        d = section_dict(sec)
        key = norm(r.get("school"))
        if not key:
            stats["unmatched"] += 1; continue
        real = idx[sec].get(key)
        if not real:
            # try containment within the same section
            for k2, orig in idx[sec].items():
                if key and (key in k2 or k2 in key):
                    real = orig; break
        if not real:
            # FALLBACK: search every other section (program hint may be wrong/'unknown')
            for alt in sections:
                if alt == sec:
                    continue
                real = idx[alt].get(key)
                if not real:
                    for k2, orig in idx[alt].items():
                        if key and (key in k2 or k2 in key):
                            real = orig; break
                if real:
                    sec = alt
                    break
        if not real:
            stats["unmatched"] += 1; unmatched.add(r.get("school")); continue
        stats["matched"] += 1
        v = section_dict(sec)[real]
        majors = [m for m in (r.get("majors") or []) if m]
        if majors and sec != "lang":
            field = {"ba": "majors", "ma": "majors", "junior": "majors_sample"}.get(sec, "majors")
            if not v.get(field):
                v[field] = majors; stats["majors_added"] += 1
                v.setdefault("_llm_parsed", {})[field] = "LLM(pro)"
            # also keep a fuller list for junior
            if sec == "junior" and not v.get("majors_full"):
                v["majors_full"] = majors
                v.setdefault("_llm_parsed", {})["majors_full"] = "LLM(pro)"
        for f, kbk in (("period", "period"), ("topik", "topik_req"), ("ielts", "ielts_req"), ("toefl", "toefl_req")):
            val = r.get(f)
            if val not in (None, "", "unknown") and not v.get(kbk):
                v[kbk] = val; stats["period_filled" if f == "period" else "lang_filled"] += 1
                v.setdefault("_llm_parsed", {})[kbk] = "LLM(pro)"

    print("stats:", stats)
    print("unmatched schools:", sorted(list(unmatched))[:20])
    if args.write:
        shutil.copy(KB, KB.replace(".json", f"_bak_llmmerge_{datetime.date.today()}.json"))
        json.dump(kb, open(KB, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print("저장 완료:", KB)

if __name__ == "__main__":
    main()
