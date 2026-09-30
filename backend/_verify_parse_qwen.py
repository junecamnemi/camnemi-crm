# -*- coding: utf-8 -*-
"""Qwen cross-check verifier for parsed guide records (report only — never writes the KB).

Why this shape: a second model that only sees the extracted JSON adds nothing but a second opinion.
The verifier must see the *source text* and may only report discrepancies it can quote from it.
Every quote is checked as a literal substring of the source; a claim whose quote cannot be found is
discarded (`quote_unverified`), which is what keeps a confident hallucination out of the KB.

  python _verify_parse_qwen.py --limit 5              # sample run, prints the report
  python _verify_parse_qwen.py                        # all records, resumable

Output: _verify_qwen_report.json  (per-record findings) and _verify_qwen.jsonl (progress, resumable)
Env:    VERIFY_MODEL (default qwen/qwen3.8-max-0902), VERIFY_WORKERS (default 4)
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import hashlib
import json
import os
import re
import sys
import time
import urllib.request

import doc_tier

BASE = os.path.dirname(os.path.abspath(__file__))
LIB = r"G:/공유 드라이브/Hermes/Camnemi/02_Crawling_Sheet/University_Project/guides"
SRC = os.path.join(BASE, "_parse_library.jsonl")


_PDF_INDEX = None


def pdf_index() -> dict:
    """basename -> full path, built once (walking the network drive per record is too slow)."""
    global _PDF_INDEX
    if _PDF_INDEX is None:
        idx = {}
        for root, _dirs, files in os.walk(LIB):
            for f in files:
                if f.lower().endswith(".pdf"):
                    idx.setdefault(f, os.path.join(root, f))
        _PDF_INDEX = idx
        print(f"guide library indexed: {len(idx)} pdfs")
    return _PDF_INDEX


def resolve_pdf(name: str) -> str:
    """`_file` holds only the basename; resolve it against the guide library."""
    if not name:
        return ""
    if os.path.isabs(name) and os.path.exists(name):
        return name
    return pdf_index().get(os.path.basename(name), "")
REPORT = os.path.join(BASE, "_verify_qwen_report.json")
PROGRESS = os.path.join(BASE, "_verify_qwen.jsonl")
MODEL = os.environ.get("VERIFY_MODEL", "qwen/qwen3.8-max-0902")
WORKERS = int(os.environ.get("VERIFY_WORKERS", "4"))
MAX_CHARS = 60000
FIELDS = ("topik", "ielts", "toefl", "period", "tuition_note", "scholarship_note", "majors")

PROMPT = """You are auditing a machine extraction of a Korean university admission guide.

Below is the SOURCE TEXT of the guide and the EXTRACTED VALUES. Report ONLY discrepancies: a value
that contradicts the source, or a value that is absent from the source entirely (fabricated).

Hard rules:
- Every finding MUST include `source_quote`: an exact character-for-character substring copied from
  the SOURCE TEXT. A finding without a findable quote is discarded, so do not paraphrase quotes.
- The source often contains SEVERAL look-alike clauses (e.g. 장학금 tables split by "본교 한국어과정
  이수자" vs "이수하지 않은 자", or per-college/​per-campus tables). Before reporting a mismatch,
  check whether a *different* clause in the source matches the extracted value. If the extracted value
  matches any other clause, use verdict "ambiguous_multi_clause" instead of "mismatch" and quote the
  clause that actually matches the extracted value.
- A quote proves the text exists, NOT that it is the clause the value came from. Only report
  "mismatch" when no clause in the source supports the extracted value.
- If the source does not state something, the correct extracted value is null. "null from nothing"
  is NOT a discrepancy. Only flag extracting a *value* that the source does not support.
- Do not rewrite or improve the values. You are not correcting, only reporting.
- Scoring notes: TOPIK is 1-6 급. IELTS is 0-9. TOEFL iBT was 0-120, but guides for 2026+ may use the
  new 1-6 scale ("TOEFL iBT 4.0, 기존 80점 이상"). A small TOEFL number with such wording is NOT an
  error - report it as `scale_note`.

Return JSON only:
{"findings": [{"field": "<one of: %s>", "extracted_value": "...", "source_quote": "...",
"verdict": "mismatch"|"fabricated"|"scale_note", "note": "one short sentence"}]}
Use an empty findings list when everything matches.

--- SOURCE TEXT (truncated to %d chars) ---
%s

--- EXTRACTED VALUES ---
%s
"""


def load_auth():
    for p in (r"C:\Users\wisew\AppData\Local\hermes\shared\nous_auth.json",
              r"C:\Users\wisew\AppData\Local\hermes\auth.json"):
        if not os.path.exists(p):
            continue
        d = json.load(open(p, encoding="utf-8"))
        tok = d.get("access_token") or d.get("agent_key")
        base = (d.get("inference_base_url") or "https://inference-api.nousresearch.com/v1").rstrip("/")
        if tok:
            return tok, base
    raise RuntimeError("no nous auth")


def call(model: str, prompt: str, max_tokens: int = 16000) -> str:
    tok, base = load_auth()                       # re-read every call: nous tokens live 1h
    body = {"model": model, "messages": [{"role": "user", "content": prompt}],
            "temperature": 0, "max_tokens": max_tokens}
    req = urllib.request.Request(base + "/chat/completions", data=json.dumps(body).encode(),
                                 headers={"Authorization": "Bearer " + tok,
                                          "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=420) as r:
        j = json.loads(r.read().decode())
    msg = (j.get("choices") or [{}])[0].get("message") or {}
    return msg.get("content") or ""


def slim(text: str) -> str:
    return re.sub(r"[ \t]+", " ", text)


def verify_one(rec: dict) -> dict:
    pdf = resolve_pdf(rec.get("_file"))
    out = {"school": rec.get("school"), "level": rec.get("_level"), "file": pdf,
           "year": rec.get("year"), "findings": [], "status": "ok"}
    if not pdf or not os.path.exists(pdf):
        out["status"] = "no_pdf"
        return out
    info = doc_tier.classify(pdf)
    text = slim(info.get("text") or "")
    if len(text) < 300:
        out["status"] = "no_text"                  # scanned/low-text: needs the VL path
        return out
    text = text[:MAX_CHARS]
    extracted = {k: rec.get(k) for k in FIELDS if rec.get(k) not in (None, "", [], {})}
    if not extracted:
        out["status"] = "nothing_extracted"
        return out
    prompt = PROMPT % ("|".join(FIELDS), MAX_CHARS, text,
                       json.dumps(extracted, ensure_ascii=False, indent=1))
    for attempt in range(3):
        try:
            raw = call(MODEL, prompt)
            break
        except Exception as e:                     # 503/429/timeout -> retry
            if attempt == 2:
                out["status"] = f"error:{type(e).__name__}"
                return out
            time.sleep(4 * (attempt + 1))
    m = re.search(r"\{.*\}", raw, re.S)
    if not m:
        out["status"] = "bad_json"
        out["raw"] = raw[:400]
        return out
    try:
        payload = json.loads(m.group(0))
    except Exception:
        out["status"] = "bad_json"
        out["raw"] = m.group(0)[:400]
        return out

    flat = re.sub(r"\s+", "", text)
    for f in payload.get("findings") or []:
        q = str(f.get("source_quote") or "")
        q_flat = re.sub(r"\s+", "", q)
        # the quote is the evidence: unverifiable quotes are dropped, not trusted
        f["quote_verified"] = bool(q_flat) and q_flat in flat
        out["findings"].append(f)
    verified = [f for f in out["findings"] if f.get("quote_verified")]
    unverified = [f for f in out["findings"] if not f.get("quote_verified")]
    out["verified_findings"] = verified
    out["unverified_findings"] = unverified
    if not out["findings"]:
        out["status"] = "clean"
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--only-school", default="")
    args = ap.parse_args()

    records = [json.loads(l) for l in open(SRC, encoding="utf-8") if l.strip()]
    if args.only_school:
        records = [r for r in records if args.only_school in str(r.get("school"))]
    done = set()
    if os.path.exists(PROGRESS):
        for l in open(PROGRESS, encoding="utf-8"):
            try:
                d = json.loads(l)
                done.add(hashlib.md5((str(d.get("file")) + str(d.get("level"))).encode()).hexdigest())
            except Exception:
                pass
    todo = [r for r in records
            if hashlib.md5((str(r.get("_file")) + str(r.get("_level"))).encode()).hexdigest() not in done]
    if args.limit:
        todo = todo[: args.limit]
    print(f"records={len(records)} already_done={len(done)} todo={len(todo)} model={MODEL}")

    results = []
    with cf.ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = {ex.submit(verify_one, r): r for r in todo}
        for i, fut in enumerate(cf.as_completed(futs), 1):
            res = fut.result()
            results.append(res)
            with open(PROGRESS, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(res, ensure_ascii=False) + "\n")
            if i % 10 == 0 or i == len(todo):
                print(f"  {i}/{len(todo)} verified")

    old = []
    if os.path.exists(REPORT):
        try:
            old = json.load(open(REPORT, encoding="utf-8"))
        except Exception:
            old = []
    merged = {f"{r.get('file')}|{r.get('level')}": r for r in old}
    for r in results:
        merged[f"{r.get('file')}|{r.get('level')}"] = r
    allr = list(merged.values())
    json.dump(allr, open(REPORT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    from collections import Counter
    st = Counter(r.get("status") for r in allr)
    verified = sum(len(r.get("verified_findings") or []) for r in allr)
    unverified = sum(len(r.get("unverified_findings") or []) for r in allr)
    print("\nstatus:", dict(st))
    print(f"verified discrepancies: {verified} | unverifiable claims dropped: {unverified}")
    print(f"report -> {os.path.basename(REPORT)}")
    for r in allr[:3]:
        if r.get("verified_findings"):
            print("\n", r["school"], r["level"])
            for f in r["verified_findings"][:3]:
                print("   ", f.get("verdict"), f.get("field"), "=", str(f.get("extracted_value"))[:40],
                      "| quote:", str(f.get("source_quote"))[:60])


if __name__ == "__main__":
    sys.exit(main())
