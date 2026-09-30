#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""T2 (deepseek-v4-pro) fill + V2 (qwen, different family) verification of per-department tuition.

Handoff contract: Opus adjudicated the unit conflicts and emitted `tuition_rule_pack.md`.
This script makes Pro CONTINUE at scale, and makes qwen VERIFY every row by quoting the source.

  python _tuition_pro_fill.py --fill   --limit 8     # Pro reads each guide's 등록금 section → rows
  python _tuition_pro_fill.py --verify --limit 8     # qwen must confirm each ₩ value appears verbatim
  python _tuition_pro_fill.py --merge                # verified rows merged into tuition_by_department.json

Rules the model may NOT decide (code does): unit conversion (annual→semester = /2), dropping
어학연수 prices, grad tagging. Pro only reads the table out of the document.
"""
import os, re, json, urllib.request, sys, math

B = os.path.dirname(os.path.abspath(__file__))
PRO_MODEL = "deepseek/deepseek-v4-pro"          # T2 extractor
VER_MODEL = "qwen/qwen3.8-max-0902"             # V2 verifier — different family from deepseek
ROWS_OUT = os.path.join(B, "_tuition_pro_rows.jsonl")
VER_OUT = os.path.join(B, "_tuition_qwen_verify.jsonl")
PACK = os.path.join(B, "tuition_rule_pack.md")


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


def call(model, prompt, max_tokens=None, timeout=480):
    # reasoning models (deepseek-v4-pro, qwen3.8-max) burn the budget on thinking first:
    # give 32k or `content` comes back empty. NEVER parse the `reasoning` field as the answer.
    mt = max_tokens or 32000
    body = {"model": model, "messages": [{"role": "user", "content": prompt}],
            "max_tokens": mt, "temperature": 0}
    req = urllib.request.Request(BASE_URL.rstrip("/") + "/chat/completions",
                                 data=json.dumps(body).encode(),
                                 headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        d = json.loads(r.read())
    m = d["choices"][0]["message"]
    return m.get("content") or ""


def extract_json(text, keys=("rows", "unit", "items", "verdict")):
    """First brace-balanced JSON object that carries one of our keys (greedy regex grabs prose)."""
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


def guide_section(v, name_hint=None, level_hint=None, window=9000):
    """등록금 section of the school's guide PDF.

    Anchor on EVERY 등록금/수업료 mention, not just the first: the first hit is usually
    '등록금 반환규정' / '등록금 납부' prose, while the actual table sits much further down.
    Windowing only on hit #1 made 건국대(GLOCAL) look like it had no table (it has 학기당 등록금).
    """
    path = v.get("guide_effective_pdf") or v.get("guide_pdf") or ""
    p = path if path and os.path.exists(path) else None
    if not p:
        # the KB path is often stale; search the whole library (archive/, wrong level folder/, NNNNNN_ prefix)
        try:
            import _guide_resolver as gr
            p = gr.resolve(v.get("name") or v.get("school") or name_hint, level_hint, path)
        except Exception:
            p = None
    if not p:
        return None, path
    try:
        import pymupdf
        doc = pymupdf.open(p)
        t = "".join(doc[i].get_text() for i in range(len(doc)))
        doc.close()
    except Exception:
        return None, path
    if len(t.strip()) < 200:
        # image-only guide (scanned/rendered): pymupdf yields '' → OCR before giving up.
        try:
            import _guide_resolver as gr
            t = gr.ocr_text(p) or t
        except Exception as e:
            print(f"   OCR skip ({type(e).__name__})")
    if not t.strip():
        return None, path
    offs = [m.start() for m in re.finditer(r"등록금|수업료", t)]
    if not offs:
        return t[:window], path
    spans = []
    for o in offs:
        lo, hi = max(0, o - 350), min(len(t), o + 900)
        if spans and lo < spans[-1][1]:
            spans[-1] = (spans[-1][0], max(spans[-1][1], hi))
        else:
            spans.append((lo, hi))
    digest = "\n…\n".join(t[a:b] for a, b in spans)
    return digest[:24000], path


FILL_PROMPT = """한국 대학 외국인 모집요강의 '등록금' 구간에서 **계열별(또는 학과별) 등록금 표만** 읽어 JSON으로 출력하라.
설명·마크다운 금지. 숫자는 표에 적힌 그대로(반올림·환산 금지). 표의 단위(학기/연간)는 unit 필드에 그대로 적어라.
{"unit":"semester|annual|unknown","admission_fee_included":true|false,
 "rows":[{"college":"표에 적힌 계열/학과명","krw":정수,"note":"수업료1/수업료2 합계 등"}],
 "evidence_quote":"표 헤더나 단위를 알려주는 원문 문장"}
- 어학연수/한국어교육원/어학당 수강료는 **제외**한다.
- 대학원/석사/박사 행은 level:"grad" 로 표시해 포함한다.
- 등록금 표가 없으면 {"unit":"unknown","rows":[],"evidence_quote":"표 없음"}.

__PACK__

=== 요강 등록금 구간 ===
"""

VER_PROMPT = """아래 [원문]에 [추출값]의 각 금액이 **그대로 등장하는지**만 검사하라. 추측 금지.
JSON만 출력: {"items":[{"college":"...","krw":정수,"found":true|false,"quote":"원문에서 그 금액이 나온 문장"}],
 "unsupported":[금액...],"verdict":"ok|mismatch"}
원문에 없는 금액은 found=false 로 하고 unsupported 에 넣어라.
주의: 원문은 PDF에서 뽑아 콤마 위치가 깨져 있을 수 있다(예: 5,907000 = 5,907,000).
**숫자열이 같으면 found=true** 로 판정하라. 콤마 위치만 다른 것은 불일치가 아니다.
추출값이 **입학금 + 수업료의 합계**일 수 있다: 원문에서 같은 계열의 두 금액을 더해 그 값이 나오면
found=true 로 하고 quote 에 "'입학금 X + 수업료 Y = Z'" 형태로 근거를 적어라.

=== [원문] ===
__SRC__

=== [추출값] ===
__ROWS__
"""


def load_kb():
    kb = json.load(open(os.path.join(B, "verified_kb.json"), encoding="utf-8"))
    idx = {}
    for lvl, (sec, key) in (("BA", ("schools", None)), ("MA", ("master", "schools")), ("전문학사", ("junior", "schools"))):
        d = kb[sec]; d = d.get(key, {}) if key else d
        for n, v in d.items():
            if v.get("excluded") or v.get("recommend_exclude"):
                continue
            idx[(n, lvl)] = v
    return idx


def pending_targets(limit=None, names=None, targets_file=None):
    """schools with NO per-college rows in tuition_by_department.json."""
    tbd = json.load(open(os.path.join(B, "tuition_by_department.json"), encoding="utf-8"))["schools"]
    out = [(n, lvl) for n, lv in tbd.items() for lvl, e in lv.items() if not e.get("rows")]
    if targets_file:
        want = {(t["school"], t["level"]) for t in json.load(open(targets_file, encoding="utf-8"))}
        out = [t for t in out if t in want]
    if names:
        out = [t for t in out if any(nm in t[0] for nm in names)]
    return out[:limit] if limit else out


def apply_unit(unit, krw):
    """CODE converts units — never the model."""
    if unit == "annual":
        return int(round(krw / 2))
    return int(krw)


def done_set(path):
    if not os.path.exists(path):
        return set()
    s = set()
    for l in open(path, encoding="utf-8"):
        if l.strip():
            d = json.loads(l)
            s.add((d.get("school"), d.get("level")))
    return s


def _fill_one(name, lvl, pack, idx, lock, out):
    v = idx.get((name, lvl), {})
    sec, path = guide_section(v, name, lvl)
    if not sec:
        return f"  SKIP {name} [{lvl}] no local guide"
    try:
        raw = call(PRO_MODEL, FILL_PROMPT.replace("__PACK__", pack) + sec)
        d = extract_json(raw, ("rows", "unit"))
        if not d:
            return f"  NO-JSON {name}"
        rows = []
        for r in d.get("rows", []):
            k = r.get("krw")
            if not isinstance(k, (int, float)) or k < 300_000 or k > 15_000_000:
                continue
            rows.append({"college": r.get("college"), "krw": apply_unit(d.get("unit"), int(k)),
                         "krw_raw": int(k), "level": r.get("level") or "undergrad", "note": r.get("note")})
        rec = {"school": name, "level": lvl, "unit": d.get("unit"),
               "admission_fee_included": d.get("admission_fee_included"),
               "rows": rows, "evidence_quote": (d.get("evidence_quote") or "")[:300],
               "guide_file": os.path.basename(path or ""), "model": PRO_MODEL}
        with lock:
            out.write(json.dumps(rec, ensure_ascii=False) + "\n")
            out.flush()
        return f"  ✔ {name} [{lvl}] unit={d.get('unit')} rows={len(rows)}"
    except Exception as e:
        return f"  ERR {name} [{lvl}] {type(e).__name__}: {e}"


def fill(limit, names=None, workers=1, targets_file=None):
    pack = open(PACK, encoding="utf-8").read()[:4000] if os.path.exists(PACK) else ""
    idx = load_kb()
    done = done_set(ROWS_OUT)
    todo = [t for t in pending_targets(None, names, targets_file) if t not in done]
    if limit:
        todo = todo[:limit]
    print(f"Pro fill targets: {len(todo)} | workers={workers}")
    if not todo:
        return
    ok = 0
    import threading
    lock = threading.Lock()
    with open(ROWS_OUT, "a", encoding="utf-8") as out:
        if workers <= 1:
            for name, lvl in todo:
                msg = _fill_one(name, lvl, pack, idx, lock, out)
                print(msg, flush=True)
                ok += 1 if msg.startswith("  ✔") else 0
        else:
            from concurrent.futures import ThreadPoolExecutor, as_completed
            with ThreadPoolExecutor(max_workers=workers) as ex:
                futs = {ex.submit(_fill_one, n, l, pack, idx, lock, out): (n, l) for n, l in todo}
                for f in as_completed(futs):
                    msg = f.result()
                    print(msg, flush=True)
                    ok += 1 if msg.startswith("  ✔") else 0
    print(f"filled {ok}/{len(todo)}")


def verify_cheap(limit=None):
    """Deterministic first pass: does the exact ₩ amount appear verbatim in the source text?
    Zero tokens, catches hallucinated numbers instantly. Run this BEFORE any model verifier."""
    idx = load_kb()
    recs = [json.loads(l) for l in open(ROWS_OUT, encoding="utf-8") if l.strip()] if os.path.exists(ROWS_OUT) else []
    out = []
    for r in recs:
        if not r.get("rows"):
            continue
        v = idx.get((r["school"], r["level"]), {})
        src, path = guide_section(v, r["school"], r["level"])
        if not src:
            print(f"  SKIP {r['school']} no source"); continue
        norm = src.replace(" ", "")
        digits = re.sub(r"\D", "", src)
        # every integer in the digest, so a 합계 (= 입학금 + 수업료) can be checked arithmetically
        nums = [int(x.replace(",", "")) for x in re.findall(r"\d{1,3}(?:,\d{3})+", src)]
        bad = []
        for row in r["rows"]:
            k = row["krw_raw"]
            # the SOURCE's comma placement is often broken (건국대 prints 5,907000) — compare
            # digit strings as well, or a document typo turns into a fake "hallucination".
            ok = (f"{k:,}" in src) or (f"{k:,}" in norm) or (str(k) in norm) or (str(k) in digits)
            if not ok:
                # a printed 합계 column is often missing from the extracted text while its parts are
                # present (국민대 아시아올림픽학과: 입학금 1,029,000 + 수업료 6,897,000 = 7,926,000).
                ok = any((k - a) in nums for a in nums if 100_000 <= a <= 3_000_000)
                if ok:
                    row["verify_note"] = "sum_of_admission_fee_and_tuition"
            if not ok:
                bad.append(row["college"] + f" {k:,}")
        rec = {"school": r["school"], "level": r["level"], "check": "verbatim_amount",
               "rows": len(r["rows"]), "unsupported": bad, "verdict": "ok" if not bad else "mismatch"}
        out.append(rec)
        print(f"  {'✔' if not bad else '⚠'} {r['school']} [{r['level']}] {len(r['rows'])-len(bad)}/{len(r['rows'])} amounts found verbatim"
              + (f" | unsupported: {bad[:5]}" if bad else ""))
    if out:
        p = os.path.join(B, "_tuition_verbatim_check.json")
        json.dump({"method": "substring of comma-formatted amount in guide text", "results": out},
                  open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("WROTE", p)


def _verify_one(r, idx, lock, out):
    v = idx.get((r["school"], r["level"]), {})
    src, _ = guide_section(v, r["school"], r["level"])
    if not src:
        return f"  SKIP {r['school']} no source text"
    try:
        offs = [src.find(f"{x['krw_raw']:,}") for x in r["rows"]]
        offs = [o for o in offs if o >= 0]
        if offs:
            lo = max(0, min(offs) - 1500)
            hi = min(len(src), max(offs) + 2000)
            win = src[lo:hi][:14000]
        else:
            win = src[:14000]
        compact = "\n".join(f"{x['college']}: {x['krw_raw']:,}" for x in r["rows"])
        raw = call(VER_MODEL, VER_PROMPT.replace("__SRC__", win)
                   .replace("__ROWS__", compact[:4000]), timeout=1200)
        d = extract_json(raw, ("items", "verdict"))
        if not d:
            return f"  NO-JSON {r['school']}"
        rec = {"school": r["school"], "level": r["level"], "verdict": d.get("verdict"),
               "unsupported": d.get("unsupported"), "items": d.get("items"),
               "verified_by": VER_MODEL, "extracted_by": r.get("model"),
               "extractor_family": (r.get("model") or "").split("/")[0]}
        with lock:
            out.write(json.dumps(rec, ensure_ascii=False) + "\n")
            out.flush()
        bad = d.get("unsupported") or []
        return f"  {'✔' if not bad else '⚠'} {r['school']} [{r['level']}] {d.get('verdict')} unsupported={bad[:4]}"
    except Exception as e:
        return f"  ERR {r['school']} {type(e).__name__}: {str(e)[:120]}"


def verify(limit, workers=1):
    idx = load_kb()
    done = done_set(VER_OUT)
    recs = [json.loads(l) for l in open(ROWS_OUT, encoding="utf-8") if l.strip()] if os.path.exists(ROWS_OUT) else []
    # records with rows, newest per school, not yet verified, and needing a verifier from
    # a DIFFERENT family than the extractor (V2: never same-family verify)
    bykey = {}
    for r in recs:
        if r.get("rows"):
            bykey[(r["school"], r["level"])] = r
    todo = [r for k, r in bykey.items() if k not in done
            and not (r.get("model") or "").startswith(VER_MODEL.split("/")[0])]
    if limit:
        todo = todo[:limit]
    print(f"qwen verify targets: {len(todo)} | workers={workers}")
    if not todo:
        return
    import threading
    lock = threading.Lock()
    ok = 0
    with open(VER_OUT, "a", encoding="utf-8") as out:
        if workers <= 1:
            for r in todo:
                msg = _verify_one(r, idx, lock, out); print(msg, flush=True)
                ok += 1 if msg.startswith("  ✔") else 0
        else:
            from concurrent.futures import ThreadPoolExecutor, as_completed
            with ThreadPoolExecutor(max_workers=workers) as ex:
                for f in as_completed([ex.submit(_verify_one, r, idx, lock, out) for r in todo]):
                    msg = f.result(); print(msg, flush=True)
                    ok += 1 if msg.startswith("  ✔") else 0
    print(f"verified {ok}/{len(todo)}")


def merge():
    """Merge qwen-verified rows into tuition_by_department.json (only verdict==ok)."""
    if not os.path.exists(VER_OUT):
        print("no verification output"); return
    vers = {(d["school"], d["level"]): d for d in (json.loads(l) for l in open(VER_OUT, encoding="utf-8") if l.strip())}
    rows = {(d["school"], d["level"]): d for d in (json.loads(l) for l in open(ROWS_OUT, encoding="utf-8") if l.strip())}
    tbd_path = os.path.join(B, "tuition_by_department.json")
    tbd = json.load(open(tbd_path, encoding="utf-8"))
    added = 0
    for key, v in vers.items():
        if v.get("verdict") != "ok":
            continue
        rec = rows.get(key)
        if not rec or not rec.get("rows"):
            continue
        name, lvl = key
        e = (tbd["schools"].get(name) or {}).get(lvl)
        if not e:
            continue
        if e.get("rows"):
            continue  # never overwrite an existing college table
        e["rows"] = rec["rows"]
        e["source"] = f"pro_extract+{VER_MODEL.split('/')[0]}_verified"
        ug = sorted({r["krw"] for r in rec["rows"] if r["level"] == "undergrad"})
        if ug:
            e["undergrad_range"] = {"min": ug[0], "max": ug[-1]}
            e["undergrad_usd"] = (f"${math.ceil(ug[0]/1400/100)*100:,}" if ug[0] == ug[-1]
                                  else f"${math.ceil(ug[0]/1400/100)*100:,}~${math.ceil(ug[-1]/1400/100)*100:,}")
        added += 1
    json.dump(tbd, open(tbd_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"merged {added} verified school-level tables into tuition_by_department.json")
    remain = sum(1 for n, lv in tbd["schools"].items() for e in lv.values() if not e.get("rows"))
    print("entries still without per-college rows:", remain)


if __name__ == "__main__":
    BASE_URL, KEY = _auth()
    lim = None
    names = None
    workers = 1
    targets_file = None
    if "--limit" in sys.argv:
        lim = int(sys.argv[sys.argv.index("--limit") + 1])
    if "--workers" in sys.argv:
        workers = int(sys.argv[sys.argv.index("--workers") + 1])
    if "--targets" in sys.argv:
        targets_file = sys.argv[sys.argv.index("--targets") + 1]
    if "--names" in sys.argv:
        i = sys.argv.index("--names")
        names = [x.strip() for x in sys.argv[i + 1].split(",") if x.strip()]
    if "--fill" in sys.argv:
        fill(lim, names, workers, targets_file)
    elif "--verify-cheap" in sys.argv:
        verify_cheap(lim)
    elif "--verify" in sys.argv:
        verify(lim, workers)
    elif "--merge" in sys.argv:
        merge()
    elif "--pending" in sys.argv:
        p = pending_targets(lim, names, targets_file)
        print(f"{len(p)} entries pending:", p[:15])