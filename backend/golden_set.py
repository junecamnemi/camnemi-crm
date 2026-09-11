#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""golden_set.py — regression harness for the extraction pipeline (ARCHITECTURE §8.3).

A golden set = a FIXED sample of guide PDFs + their baseline extraction, so that changing
the model / prompt / router can be measured rather than guessed.

Commands:
  build [--n 50]        pick a deterministic sample (A/B-tier), store filename+tier in golden_set.json
  baseline <jsonl>      attach a baseline extraction (per-file) from an existing parse jsonl
  run <jsonl>           compare a NEW parse against the baseline -> drift report
  list                  show the golden set

Comparison metrics per file:
  majors_jaccard   overlap of extracted majors vs baseline (0..1)
  period_same      exact period match
  req_delta        count of changed topik/ielts/toefl values
Verdict per file: MATCH / DRIFT / MISSING. Overall pass = MATCH ratio >= 0.8
"""
import os, re, json, glob, argparse, random

BASE = r"C:\Users\USER\camnemi-crm\backend"
GS = os.path.join(BASE, "golden_set.json")
UP = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project"
TIER_A, TIER_B = 5000, 1000

def norm(s):
    return re.sub(r"\s+", "", str(s or ""))

def pdf_index():
    idx = {}
    for p in glob.glob(os.path.join(UP, "**", "*.pdf"), recursive=True):
        idx.setdefault(os.path.basename(p), p)
    return idx

def tier_of(path):
    import pymupdf
    try:
        d = pymupdf.open(path)
        n = len("\n".join(d[i].get_text() for i in range(len(d))))
        d.close()
    except Exception:
        return "E", 0
    if n >= TIER_A: return "A", n
    if n >= TIER_B: return "B", n
    if n >= 200:    return "C", n
    return "D", n

def cmd_build(args):
    idx = pdf_index()
    rows = []
    for fn, p in sorted(idx.items()):
        t, n = tier_of(p)
        if t in ("A", "B"):
            rows.append({"file": fn, "tier": t, "text_len": n})
    random.seed(7)
    sample = random.sample(rows, min(args.n, len(rows)))
    json.dump({"n": len(sample), "files": sample},
              open(GS, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    from collections import Counter
    print(f"golden set 구축: {len(sample)}개 | tier {dict(Counter(x['tier'] for x in sample))} → {GS}")

def load_parse(jsonl):
    out = {}
    for l in open(jsonl, encoding="utf-8"):
        if not l.strip(): continue
        r = json.loads(l)
        fn = str(r.get("_file") or r.get("_id") or "")
        if fn: out[os.path.basename(fn)] = r
    return out

def cmd_baseline(args):
    gs = json.load(open(GS, encoding="utf-8"))
    parse = load_parse(args.jsonl)
    hit = 0
    for it in gs["files"]:
        r = parse.get(it["file"])
        if r:
            it["baseline"] = {"majors": r.get("majors") or [], "period": r.get("period"),
                              "topik": r.get("topik"), "ielts": r.get("ielts"), "toefl": r.get("toefl")}
            hit += 1
    json.dump(gs, open(GS, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"baseline 부착: {hit}/{len(gs['files'])}")

def cmd_run(args):
    gs = json.load(open(GS, encoding="utf-8"))
    parse = load_parse(args.jsonl)
    n_match = n_drift = n_missing = 0
    rows = []
    for it in gs["files"]:
        base = it.get("baseline")
        cur = parse.get(it["file"])
        if not base:
            continue
        if not cur:
            n_missing += 1; rows.append((it["file"], "MISSING", {}, )); continue
        bm, cm = set(map(norm, base.get("majors") or [])), set(map(norm, cur.get("majors") or []))
        jac = (len(bm & cm) / len(bm | cm)) if (bm | cm) else 1.0
        period_same = (str(base.get("period")) == str(cur.get("period")))
        req_delta = sum(1 for f in ("topik", "ielts", "toefl") if str(base.get(f)) != str(cur.get(f)))
        ok = (jac >= 0.7) and period_same and req_delta == 0
        (rows.append((it["file"], "MATCH" if ok else "DRIFT", {"jaccard": round(jac, 2), "period_same": period_same, "req_delta": req_delta})))
        n_match += int(ok); n_drift += int(not ok)
    tot = n_match + n_drift + n_missing
    print(f"=== Golden Set 회귀 ({tot}개) ===")
    print(f"  MATCH {n_match} | DRIFT {n_drift} | MISSING {n_missing}")
    if tot:
        print(f"  통과율 {n_match/tot:.0%} (기준 80%) → {'PASS' if n_match/tot>=0.8 else 'FAIL'}")
    for f, v, d in rows:
        if v != "MATCH":
            print(f"   ⚠ [{v}] {f[:48]} {d}")
    return 0 if (tot and n_match / tot >= 0.8) else 1

def cmd_list(args):
    gs = json.load(open(GS, encoding="utf-8"))
    print(f"golden set: {gs['n']}개")
    for it in gs["files"][:20]:
        print(f"  [{it['tier']}] {it['file'][:52]:52s} base={'O' if it.get('baseline') else 'X'}")

def main():
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build"); b.add_argument("--n", type=int, default=50); b.set_defaults(fn=cmd_build)
    bl = sub.add_parser("baseline"); bl.add_argument("jsonl"); bl.set_defaults(fn=cmd_baseline)
    r = sub.add_parser("run"); r.add_argument("jsonl"); r.set_defaults(fn=cmd_run)
    l = sub.add_parser("list"); l.set_defaults(fn=cmd_list)
    a = ap.parse_args(); raise SystemExit(a.fn(a) or 0)

if __name__ == "__main__":
    main()
