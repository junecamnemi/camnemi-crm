#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Vision (V tier) extraction for image-only guides that OCR cannot read.

Why: the image-only guides are the ENGLISH-language editions (우송대 "WOOSONG UNIVERSITY GRADUATE
SCHOOL ADMISSIONS GUIDELINE", 한양대 "ADMISSION GUIDELINES FOR INTERNATIONAL STUDENTS"). RapidOCR
returns their Latin text but garbles Korean into noise (正品, 号官H是), so no tuition table survives
OCR. A vision model reads the rendered page directly.

  python _tuition_vision.py --list                 # which entries are image-only
  python _tuition_vision.py --extract --limit 3    # render pages → qwen3-vl → rows

Writes _tuition_pro_rows.jsonl in the SAME shape as the Pro path, so --verify-cheap / --merge work.
Verification differs: with no text layer the deterministic check cannot run, so each record carries
`needs_vision_verify: true` and merge() refuses it until a second, different-family pass confirms.
"""
import os, re, json, sys, base64, io, urllib.request

B = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, B)
V_MODEL = "qwen/qwen3-vl-235b-a22b-instruct"
ROWS_OUT = os.path.join(B, "_tuition_pro_rows.jsonl")
PACK = os.path.join(B, "tuition_rule_pack.md")
PACK_TXT = ""
if os.path.exists(PACK):
    PACK_TXT = open(PACK, encoding="utf-8").read()[:2500]


def _auth():
    for p in [r"C:\Users\wisew\AppData\Local\hermes\shared\nous_auth.json",
              r"C:\Users\wisew\AppData\Local\hermes\auth.json"]:
        if not os.path.exists(p):
            continue
        d = json.load(open(p, encoding="utf-8"))
        if isinstance(d, dict) and d.get("access_token"):
            return d.get("inference_base_url") or "https://inference-api.nousresearch.com/v1", d["access_token"]
        n = (d.get("providers") or {}).get("nous") or {}
        if n.get("agent_key"):
            return n.get("inference_base_url") or "https://inference-api.nousresearch.com/v1", n["agent_key"]
    raise SystemExit("no auth")


def call_vision(images_b64, prompt, timeout=1200):
    content = [{"type": "text", "text": prompt}]
    for b in images_b64:
        content.append({"type": "image_url", "image_url": {"url": "data:image/png;base64," + b}})
    body = {"model": V_MODEL, "messages": [{"role": "user", "content": content}],
            "max_tokens": 32000, "temperature": 0}
    req = urllib.request.Request(BASE_URL.rstrip("/") + "/chat/completions",
                                 data=json.dumps(body).encode(),
                                 headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        d = json.loads(r.read())
    return d["choices"][0]["message"].get("content") or ""


def extract_json(text, keys=("rows", "unit")):
    if not text:
        return None
    dec = json.JSONDecoder()
    for i, ch in enumerate(text):
        if ch != "{":
            continue
        try:
            obj, _ = dec.raw_decode(text[i:])
        except Exception:
            continue
        if isinstance(obj, dict) and any(k in obj for k in keys):
            return obj
    return None


V_PROMPT = """첨부한 한국 대학 외국인 모집요강 페이지 이미지에서 **등록금(수업료) 표**를 읽어 JSON만 출력하라.
설명·마크다운 금지. 이미지에 적힌 숫자를 그대로 읽어라(환산·반올림 금지).
{"unit":"semester|annual|unknown","admission_fee_included":true|false,
 "rows":[{"college":"표에 적힌 학과/계열명","krw":정수,"note":"첫학기/2학기 이후 등"}],
 "evidence_quote":"표 제목이나 단위를 보여주는 문구","currency_if_not_krw":"USD|KRW"}
- 어학연수/한국어교육원 수강료는 제외. 대학원/석사/박사 행은 level:"grad".
- 등록금 표가 없으면 {"unit":"unknown","rows":[],"evidence_quote":"표 없음"}.
- 이 요강은 영문판일 수 있다. 금액이 USD면 currency_if_not_krw 에 USD 를 적고 krw 에는 달러 숫자를 그대로 써라.

__PACK__
"""


def image_only_targets():
    """Pending entries whose resolved guide has no text layer (OCR-unreadable)."""
    import importlib.util
    argv = sys.argv[:]          # importing tpf resets sys.argv — restore it or --list/--limit vanish
    spec = importlib.util.spec_from_file_location("tpf", os.path.join(B, "_tuition_pro_fill.py"))
    tpf = importlib.util.module_from_spec(spec)
    sys.argv = ["x"]
    try:
        spec.loader.exec_module(tpf)
    except SystemExit:
        pass
    sys.argv = argv
    import _guide_resolver as gr
    tbd = json.load(open(os.path.join(B, "tuition_by_department.json"), encoding="utf-8"))["schools"]
    idx = tpf.load_kb()
    out = []
    for n, lv in [(n, lvl) for n, lv in tbd.items() for lvl, e in lv.items() if not e.get("rows")]:
        v = idx.get((n, lv), {})
        p = (v.get("guide_effective_pdf") or v.get("guide_pdf") or "")
        if not (p and os.path.exists(p)):
            p = gr.resolve(n, lv, p)
        if not p or not os.path.exists(p):
            continue
        t = gr.read_text(p) or ""
        if len(t.strip()) < 200:
            out.append({"school": n, "level": lv, "path": p})
    return out, tpf


def render(path, max_pages=30, scale=1.7, max_side=1400):
    """All pages, small: 12 pages at 2.0x blew the request size (HTTP 413 Payload Too Large)."""
    import pymupdf
    doc = pymupdf.open(path)
    imgs = []
    for i in range(min(len(doc), max_pages)):
        pix = doc[i].get_pixmap(matrix=pymupdf.Matrix(scale, scale))
        b = pix.tobytes("png")
        if max(pix.width, pix.height) > max_side:
            try:
                from PIL import Image
                im = Image.open(io.BytesIO(b))
                im.thumbnail((max_side, max_side))
                buf = io.BytesIO(); im.save(buf, "PNG"); b = buf.getvalue()
            except Exception:
                pass
        imgs.append(base64.b64encode(b).decode())
    doc.close()
    return imgs


def upsert(rec):
    """One record per (school, level) — keep the LAST. Re-runs were appending duplicates."""
    rows = []
    if os.path.exists(ROWS_OUT):
        for l in open(ROWS_OUT, encoding="utf-8"):
            if l.strip():
                rows.append(json.loads(l))
    rows = [r for r in rows if (r.get("school"), r.get("level")) != (rec["school"], rec["level"])]
    rows.append(rec)
    with open(ROWS_OUT, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def extract_doc(path):
    """Chunked vision: 4 images per call. A single call with 12 pages returned HTTP 413, and a
    12-page cap also missed the tuition table when it sits late in a 23-page guide."""
    imgs = render(path)
    rows, unit, quote, cur, fee = [], None, None, None, None
    for i in range(0, len(imgs), 4):
        chunk = imgs[i:i + 4]
        hint = f"\n(이 이미지는 전체 {len(imgs)}페이지 중 {i+1}~{i+len(chunk)}페이지다.)"
        try:
            raw = call_vision(chunk, V_PROMPT.replace("__PACK__", PACK_TXT) + hint)
        except Exception as e:
            print(f"      chunk {i//4} err {type(e).__name__}"); continue
        d = extract_json(raw)
        if not d:
            continue
        rows += (d.get("rows") or [])
        if unit in (None, "unknown") and d.get("unit") not in (None, "unknown"):
            unit = d.get("unit")
        if not quote and (d.get("evidence_quote") or "").strip() not in ("", "표 없음"):
            quote = d.get("evidence_quote")
        if not cur and d.get("currency_if_not_krw"):
            cur = d.get("currency_if_not_krw")
        if fee is None and d.get("admission_fee_included") is not None:
            fee = d.get("admission_fee_included")
    seen, uniq = set(), []
    for r in rows:
        k = r.get("krw")
        if not isinstance(k, (int, float)):
            continue
        key = (str(r.get("college")), int(k))
        if key in seen:
            continue
        seen.add(key)
        uniq.append({"college": r.get("college"), "krw": int(k), "krw_raw": int(k),
                     "level": r.get("level") or "undergrad", "note": r.get("note")})
    return {"unit": unit or "unknown", "admission_fee_included": fee, "rows": uniq,
            "evidence_quote": (quote or "표 없음")[:300], "currency_if_not_krw": cur}


def main():
    targets, tpf = image_only_targets()
    if "--list" in sys.argv or not targets:
        print(f"image-only pending entries: {len(targets)}")
        for t in targets:
            print("   ", t["school"], t["level"], os.path.basename(t["path"]))
        return
    have_rows = set()
    if os.path.exists(ROWS_OUT):
        for l in open(ROWS_OUT, encoding="utf-8"):
            if l.strip():
                d = json.loads(l)
                if d.get("rows"):
                    have_rows.add((d["school"], d["level"]))
    todo = [t for t in targets if (t["school"], t["level"]) not in have_rows]
    if "--limit" in sys.argv:
        todo = todo[:int(sys.argv[sys.argv.index("--limit") + 1])]
    workers = int(sys.argv[sys.argv.index("--workers") + 1]) if "--workers" in sys.argv else 1
    print(f"vision targets: {len(todo)} | workers={workers}")

    def one(t):
        try:
            d = extract_doc(t["path"])
            rec = {"school": t["school"], "level": t["level"], "unit": d["unit"],
                   "admission_fee_included": d["admission_fee_included"], "rows": d["rows"],
                   "evidence_quote": d["evidence_quote"], "guide_file": os.path.basename(t["path"]),
                   "model": V_MODEL, "currency_if_not_krw": d["currency_if_not_krw"],
                   "needs_vision_verify": True}
            upsert(rec)
            return f"  {'✔' if d['rows'] else '·'} {t['school']} [{t['level']}] unit={d['unit']} rows={len(d['rows'])}"
        except Exception as e:
            return f"  ERR {t['school']} {type(e).__name__}: {str(e)[:150]}"

    if workers > 1:
        import threading
        from concurrent.futures import ThreadPoolExecutor, as_completed
        lock = threading.Lock()

        def locked(t):
            with lock:
                return one(t)
        with ThreadPoolExecutor(max_workers=workers) as ex:
            for f in as_completed([ex.submit(locked, t) for t in todo]):
                print(f.result(), flush=True)
    else:
        for t in todo:
            print(one(t), flush=True)
    print("done")


if __name__ == "__main__":
    BASE_URL, KEY = _auth()
    main()