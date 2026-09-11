#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Assess text-length of every source PDF for guides_llm_parsed.jsonl.
Records whose PDF has little/no text layer are UNTRUSTWORTHY (LLM could hallucinate)."""
import json, os, glob, re
import pymupdf

BASE = r"C:\Users\USER\camnemi-crm\backend"
JSONL = os.path.join(BASE, "guides_llm_parsed.jsonl")
UP = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project"

PDF_BY_NAME = {}
for p in glob.glob(os.path.join(UP, "**", "*.pdf"), recursive=True):
    PDF_BY_NAME.setdefault(os.path.basename(p), p)

cache = {}
def tlen(path):
    if path in cache:
        return cache[path]
    try:
        d = pymupdf.open(path)
        n = sum(len(d[i].get_text()) for i in range(len(d)))
        d.close()
    except Exception:
        n = -1
    cache[path] = n
    return n

rows = [json.loads(l) for l in open(JSONL, encoding="utf-8") if l.strip()]
buckets = {"rich(>=5000)": 0, "medium(1000-5000)": 0, "poor(200-1000)": 0, "image(<200)": 0, "no_pdf": 0}
by_prog = {}
flagged = []
for r in rows:
    fn = r.get("_file") or ""
    path = PDF_BY_NAME.get(fn)
    if not path:
        buckets["no_pdf"] += 1
        b = "no_pdf"
    else:
        n = tlen(path)
        if n >= 5000: b = "rich(>=5000)"
        elif n >= 1000: b = "medium(1000-5000)"
        elif n >= 200: b = "poor(200-1000)"
        else: b = "image(<200)"
        buckets[b] += 1
        if b in ("image(<200)", "poor(200-1000)"):
            flagged.append((r.get("school"), r.get("program"), n, fn))
    by_prog.setdefault(r.get("program"), {}).setdefault(b, 0)
    by_prog[r.get("program")][b] += 1

print("=== 소스 PDF 텍스트 길이 분포 (601개) ===")
for k, v in buckets.items():
    print(f"  {k}: {v}")
print("\n=== program별 신뢰도 ===")
for prog, d in by_prog.items():
    print(f"  {prog}: {d}")
print(f"\n⚠️ 신뢰불가(poor/image): {len(flagged)}건 — 이들은 period/majors 재검증 또는 OCR 필요")
for s, pr, n, fn in flagged[:15]:
    print(f"   - {s} ({pr}) text={n} {fn[:40]}")
json.dump({"buckets": buckets, "flagged": [{"school": s, "program": p, "text_len": n, "file": f} for s, p, n, f in flagged]},
          open(os.path.join(BASE, "_llmparse_trust.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
