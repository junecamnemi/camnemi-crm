# -*- coding: utf-8 -*-
"""Vision rescue for guides the text pipeline cannot read (tier E: screenshots / image-only pages).

doc_tier marks these PDFs `E` (or low text) and _parse_library_batch.py rejects them, so the schools
end up with no requirements at all. Here the pages are rendered to images and read by a vision model,
using the SAME output schema as the text parser (verified model id from the gateway /models list).

  python _extract_scan_qwen_vl.py --dry            # list the candidates, no API calls
  python _extract_scan_qwen_vl.py --limit 3        # try 3 documents
  python _extract_scan_qwen_vl.py                  # all candidates, resumable

Output: _parse_library_vl.jsonl (same record shape as _parse_library.jsonl, _source="qwen3-vl")
Env:    VL_MODEL (default qwen/qwen3-vl-235b-a22b-instruct), VL_WORKERS (default 2), VL_MAX_PAGES
"""
from __future__ import annotations

import argparse
import base64
import concurrent.futures as cf
import glob
import hashlib
import json
import os
import re
import sys
import time
import urllib.request

import doc_tier
from _parse_library_batch import LIB, PROMPT, parse_json

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "_parse_library_vl.jsonl")
MODEL = os.environ.get("VL_MODEL", "qwen/qwen3-vl-235b-a22b-instruct")
WORKERS = int(os.environ.get("VL_WORKERS", "2"))
MAX_PAGES = int(os.environ.get("VL_MAX_PAGES", "8"))
JPEG_Q = int(os.environ.get("VL_JPEG_Q", "80"))     # PNG pages overflowed the gateway (HTTP 413)
MAXTOK = 24000


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


def render_pages(pdf: str, max_pages: int = MAX_PAGES) -> tuple[list, dict]:
    """Render pages to base64 PNG, skipping blank ones.

    Two real failure modes found here: (a) a guide whose content starts after the cover needs more
    than a handful of pages (한양대: 23 pages, nothing in the first 6); (b) a stub PDF that renders
    nothing at all (중앙대_ba.pdf: 1 page, 0.12% ink) — that must be reported as blank, not as an
    empty extraction, so it goes to re-collection instead of looking like "no requirements".
    """
    import fitz                                   # pymupdf
    from PIL import Image
    import io
    doc = fitz.open(pdf)
    out, ink = [], []
    for i, page in enumerate(list(doc)[:max_pages]):
        pix = page.get_pixmap(dpi=150)
        try:
            im = Image.open(io.BytesIO(pix.tobytes("png")))
            gray = im.convert("L")
            px = list(gray.getdata())
            ratio = sum(1 for v in px if v < 200) / max(1, len(px))
            if im.width > 1400:                   # keep the payload small: 6 PNG pages hit HTTP 413
                im = im.resize((1400, int(im.height * 1400 / im.width)))
            buf = io.BytesIO()
            im.convert("RGB").save(buf, format="JPEG", quality=JPEG_Q)
            data = buf.getvalue()
        except Exception:
            ratio, data = 1.0, pix.tobytes("png")
        ink.append(round(ratio * 100, 2))
        if ratio >= 0.005:                        # blank page: nothing for the model to read
            out.append(base64.b64encode(data).decode())
    doc.close()
    return out, {"pages_total": len(ink), "ink_pct": ink, "pages_sent": len(out)}


def call_vl(images: list, prompt: str) -> tuple[str, dict]:
    tok, base = load_auth()                        # tokens live 1h: re-read every call
    content = [{"type": "text", "text": prompt}]
    for b64 in images:
        content.append({"type": "image_url",
                        "image_url": {"url": "data:image/jpeg;base64," + b64}})
    body = {"model": MODEL, "messages": [{"role": "user", "content": content}],
            "temperature": 0, "max_tokens": MAXTOK}
    req = urllib.request.Request(base + "/chat/completions", data=json.dumps(body).encode(),
                                 headers={"Authorization": "Bearer " + tok,
                                          "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as r:
        j = json.loads(r.read().decode())
    msg = (j.get("choices") or [{}])[0].get("message") or {}
    return (msg.get("content") or msg.get("reasoning") or ""), j.get("usage", {})


def candidates() -> list:
    """PDFs the text pipeline could not read (tier E or almost no text)."""
    out = []
    for lvl in ("ba", "ma", "junior", "lang"):
        for p in sorted(glob.glob(os.path.join(LIB, lvl, "*", "*.pdf"))):
            info = doc_tier.classify(p, allow_ocr=False)
            if info.get("tier") == "E" or info.get("text_len", 0) < 300:
                out.append((p, lvl, info.get("tier"), info.get("text_len")))
    return out


# ---- deterministic school-name check -----------------------------------------------------------
# The vision model can misread a school name (a 청주대학교 guide came back as "경상대학교"), so the
# name is validated against the canonical school list and the filename token, and corrected by rule.
_CANON = None


def canon_names() -> list:
    global _CANON
    if _CANON is None:
        out = []
        path = os.path.join(BASE, "canonical", "schools.jsonl")
        if os.path.exists(path):
            for line in open(path, encoding="utf-8"):
                try:
                    d = json.loads(line)
                except Exception:
                    continue
                nm = d.get("school") or d.get("name")
                if nm and not str(nm).startswith("_"):
                    out.append(nm)
        _CANON = out
        print(f"canonical school names: {len(out)}")
    return _CANON


def fold(name: str) -> str:
    s = str(name or "").lower()
    for ch in "()[]{}·,.-_ ":
        s = s.replace(ch, "")
    for suf in ("대학교", "대학원", "대학", "대"):
        if s.endswith(suf) and len(s) > len(suf):
            return s[: -len(suf)]
    return s


def name_from_filename(pdf: str) -> str:
    b = os.path.basename(pdf)
    b = re.sub(r"^\d+_", "", b)                  # 0000179_ prefix
    b = re.sub(r"\.pdf$", "", b, flags=re.I)
    b = re.sub(r"\[[^\]]*\]", "", b)            # [본교] [분교]
    b = re.sub(r"\([^)]*\)", "", b)             # (글로컬) (ERICA)
    b = b.split("_")[0]                          # drop _BA_2027 / _외국인 tails
    return b.strip()


def fix_school_name(rec: dict, pdf: str) -> None:
    expected = name_from_filename(pdf)
    got = str(rec.get("school") or "")
    pool = canon_names()
    exp_fold = fold(expected)
    match = None
    for nm in pool:
        if fold(nm) == exp_fold:
            match = nm
            break
    if match and fold(got) != exp_fold:
        rec["_school_raw"] = got
        rec["school"] = match
        rec["_school_corrected"] = True


def extract_one(item: tuple) -> dict:
    pdf, lvl, tier, tlen = item
    rec = {"_file": os.path.basename(pdf), "_level": lvl, "_prog_hint": lvl,
           "_source": "qwen3-vl", "_vision": True, "_trusted": False,   # vision != text layer
           "_tier": tier, "_text_len": tlen}
    try:
        images, meta = render_pages(pdf)
        rec["_render"] = meta
        if not images:
            rec["_error"] = "blank_render"        # stub/broken PDF -> needs re-collection
            return rec
        content = ""
        for attempt in range(3):
            try:
                content, usage = call_vl(images, PROMPT)
                rec["_usage"] = usage
                break
            except Exception as e:
                if attempt == 2:
                    rec["_error"] = f"{type(e).__name__}: {e}"
                    return rec
                time.sleep(5 * (attempt + 1))
        data = parse_json(content)
        if not data:
            rec["_error"] = "bad_json"
            rec["_raw"] = content[:400]
            return rec
        rec.update(data)
        fix_school_name(rec, pdf)                 # rules, not the model, decide the school name
        rec["_pages"] = len(images)
        # nothing usable -> retry once with the whole document (the info may sit after the cover)
        if not (rec.get("majors") or rec.get("topik") or rec.get("ielts") or rec.get("period")):
            wide, meta2 = render_pages(pdf, max_pages=min(24, max(meta["pages_total"], 12)))
            if wide and len(wide) > len(images):
                content2, usage2 = call_vl(wide, PROMPT)
                data2 = parse_json(content2)
                if data2:
                    rec.update({k: v for k, v in data2.items() if v not in (None, "", [], {})})
                    fix_school_name(rec, pdf)
                    rec["_render_retry"] = meta2
                    rec["_pages"] = len(wide)
                    rec["_usage"] = usage2
        rec["year"] = str(rec.get("year") or "unknown")
        # the lang invariant holds for the vision path too
        if rec.get("program") == "lang":
            for k in ("topik", "ielts", "toefl"):
                rec[k] = None
            rec["majors"] = []        # a language course has no majors (program name is not a major)
        return rec
    except Exception as e:
        rec["_error"] = f"{type(e).__name__}: {e}"
        return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    cand = candidates()
    print(f"unreadable guides: {len(cand)}")
    for p, lvl, tier, tlen in cand[:12]:
        print(f"  [{tier}] {lvl:>6} text={tlen:<6} {os.path.basename(p)}")
    if args.dry:
        return
    done = set()
    if os.path.exists(OUT):
        for l in open(OUT, encoding="utf-8"):
            try:
                done.add(json.loads(l)["_file"])
            except Exception:
                pass
    todo = [c for c in cand if c[0].split(os.sep)[-1] not in done]
    if args.limit:
        todo = todo[: args.limit]
    print(f"already done: {len(done)} | todo: {len(todo)} | model: {MODEL}")
    if not todo:
        return

    with cf.ThreadPoolExecutor(max_workers=WORKERS) as ex:
        for i, rec in enumerate(ex.map(extract_one, todo), 1):
            with open(OUT, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            flag = "ERR " + str(rec.get("_error")) if rec.get("_error") else "ok"
            print(f"  {i}/{len(todo)} {rec['_file'][:52]} -> {flag}")
    ok = sum(1 for l in open(OUT, encoding="utf-8")
             if l.strip() and "_error" not in json.loads(l))
    print(f"\nwrote {OUT} | usable records: {ok}")


if __name__ == "__main__":
    sys.exit(main())
