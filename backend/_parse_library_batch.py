#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_parse_library_batch.py — parse EVERY current-cycle guide in the G: library.

Library: G:/공유 드라이브/Hermes/Camnemi/02_Crawling_Sheet/University_Project/guides/{level}/{year}
(the old C:/Users/.../내 드라이브/adiga_* folders are EMPTY — do not use them).

Flow per file:
  doc_tier.classify  -> A/B (flash) | C/D (pro + OCR) | E reject
  call model         -> strict JSON, "값 없으면 null" (no hallucination prompt)
  kb_verify.evidence -> every numeric claim must appear in the source text
  write row          -> _parse_library.jsonl (resumable, md5-of-path gated)
  report             -> _library_parse_report.json

Usage:
  python _parse_library_batch.py --inventory           # free: tiers + already-parsed split
  python _parse_library_batch.py --run --workers 6      # parse the remaining files
  python _parse_library_batch.py --run --levels ba      # limit to one level
"""
import os, re, sys, json, glob, time, hashlib, threading, queue, argparse, urllib.request
from collections import Counter

BASE = os.path.dirname(os.path.abspath(__file__))
LIB = r"G:/공유 드라이브/Hermes/Camnemi/02_Crawling_Sheet/University_Project/guides"
OUT = os.path.join(BASE, "_parse_library.jsonl")
REPORT = os.path.join(BASE, "_library_parse_report.json")
EXISTING = [os.path.join(BASE, f) for f in
            ("guides_llm_parsed.jsonl", "guides_llm_parsed_ocr.jsonl", "guides_llm_parsed_real.jsonl")]
CURRENT_DIRS = [("ba", "2027"), ("ma", "2027"), ("junior", "2027"), ("lang", "2027"), ("lang", "2026")]

MODEL_BY_TIER = {"A": "deepseek/deepseek-v4-flash-0731", "B": "deepseek/deepseek-v4-flash-0731",
                 "C": "deepseek/deepseek-v4-pro", "D": "deepseek/deepseek-v4-pro"}
MAXTOK = 24000
PROMPT = """한국 대학 외국인 모집요강 텍스트에서 정보를 추출해 JSON만 출력하세요(설명 금지):
{"school":"대학명(한글)", "program":"ba|ma|lang|junior", "year":"2026|2027|unknown",
 "period":"원서접수 기간", "topik":TOPIK최소급수 또는 null, "ielts":IELTS최소 또는 null,
 "toefl":TOEFL최소 또는 null, "majors":["모집학과 전체"],
 "tuition_note":"등록금 한 줄", "scholarship_note":"장학금 한 줄"}
중요: 텍스트에 실제로 적힌 값만. 없으면 null (추측 금지).
어학연수(lang)는 TOPIK/IELTS 입학요건이 아니므로 topik/ielts/toefl은 반드시 null.

=== 모집요강 텍스트 ===
"""


def load_auth():
    for p in (r"C:\Users\wisew\AppData\Local\hermes\shared\nous_auth.json",
              r"C:\Users\wisew\AppData\Local\hermes\auth.json"):
        if not os.path.exists(p):
            continue
        d = json.load(open(p, encoding="utf-8"))
        if "providers" in d:
            d = d["providers"]["nous"]
        tok = d.get("access_token") or d.get("agent_key")
        base = (d.get("inference_base_url") or "https://inference-api.nousresearch.com/v1").rstrip("/")
        if tok:
            return tok, base
    raise RuntimeError("no nous auth")


def call(text, model, retries=3):
    body = {"model": model, "messages": [{"role": "user", "content": PROMPT + text[:14000]}],
            "temperature": 0, "max_tokens": MAXTOK}
    last = None
    for k in range(retries):
        tok, base = load_auth()          # re-read every call: Nous tokens live 1h
        try:
            req = urllib.request.Request(base + "/chat/completions", data=json.dumps(body).encode(),
                                         headers={"Authorization": "Bearer " + tok, "Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=420) as r:
                j = json.loads(r.read().decode())
            msg = (j.get("choices") or [{}])[0].get("message") or {}
            content = msg.get("content") or msg.get("reasoning") or msg.get("reasoning_content") or ""
            if content.strip():
                return content, j.get("usage", {})
            last = "empty content (finish=%s)" % (j.get("choices") or [{}])[0].get("finish_reason")
        except Exception as e:
            last = "%s: %s" % (type(e).__name__, str(e)[:120])
        time.sleep(3 + 3 * k)
    raise RuntimeError("no content [%s]: %s" % (model, last))


def parse_json(s):
    if not s:
        return None
    s = re.sub(r"^```(json)?|```$", "", str(s).strip(), flags=re.M).strip()
    try:
        return json.loads(s)
    except Exception:
        pass
    dec = json.JSONDecoder()
    for m in re.finditer(r"\{", s):
        try:
            obj, _ = dec.raw_decode(s[m.start():])
            if isinstance(obj, dict) and obj.get("school"):
                return obj
        except Exception:
            continue
    return None


def school_from_name(fn):
    n = re.sub(r"^\d+_", "", fn)
    n = re.sub(r"\[(본교|분교)\]", "", n)
    n = re.sub(r"\.pdf$", "", n, flags=re.I)
    n = n.split("_")[0].strip()
    return n


def norm(s):
    return re.sub(r"\s+", "", str(s or "")).replace("대학교", "").replace("대학", "")


def library_files(levels=None):
    out = []
    for lv, yr in CURRENT_DIRS:
        if levels and lv not in levels:
            continue
        d = os.path.join(LIB, lv, yr)
        for f in sorted(glob.glob(os.path.join(d, "*.pdf"))):
            out.append((lv, yr, f))
    return out


def existing_index():
    idx = {}
    for p in EXISTING:
        if not os.path.exists(p):
            continue
        for line in open(p, encoding="utf-8"):
            try:
                r = json.loads(line)
            except Exception:
                continue
            k = (norm(r.get("school")), r.get("program"))
            if k[0]:
                idx.setdefault(k, r)
    return idx


def done_index():
    done = {}
    if os.path.exists(OUT):
        for line in open(OUT, encoding="utf-8"):
            try:
                r = json.loads(line)
            except Exception:
                continue
            done[r.get("_file")] = r
    return done


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inventory", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--levels", nargs="*")
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--ocr", action="store_true", help="allow OCR for low-text PDFs")
    a = ap.parse_args()

    sys.path.insert(0, BASE)
    files = library_files(a.levels)
    ex = existing_index()
    done = done_index()
    todo = []
    for lv, yr, f in files:
        fn = os.path.basename(f)
        sch = school_from_name(fn)
        if fn in done or (norm(sch), lv) in ex:
            continue
        todo.append((lv, yr, f, sch))
    print("library current-cycle files: %d | already parsed: %d | TODO: %d"
          % (len(files), len(files) - len(todo), len(todo)))

    if a.inventory:
        from doc_tier import classify
        rows = []
        for lv, yr, f, sch in todo:
            tb = classify(f, allow_ocr=False)
            rows.append({"level": lv, "year": yr, "file": os.path.basename(f), "school": sch,
                         "tier": tb["tier"], "text_len": tb["text_len"], "reason": tb["reason"]})
        print("tier dist:", dict(sorted(Counter(r["tier"] for r in rows).items())))
        print("by level:", {lv: dict(sorted(Counter(r["tier"] for r in rows if r["level"] == lv).items()))
                            for lv in sorted({r["level"] for r in rows})})
        json.dump(rows, open(REPORT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        for r in rows[:40]:
            print("  [%s] %-6s %-50s len=%7d" % (r["tier"], r["level"], r["file"][:50], r["text_len"]))
        return

    if not a.run:
        print("nothing to do (use --inventory or --run)")
        return

    from doc_tier import classify
    q = queue.Queue()
    for item in todo:
        q.put(item)
    lock = threading.Lock()
    out = open(OUT, "a", encoding="utf-8")
    stats = Counter()
    log = []

    def worker():
        while True:
            try:
                lv, yr, f, sch = q.get_nowait()
            except queue.Empty:
                return
            fn = os.path.basename(f)
            try:
                tb = classify(f, allow_ocr=True)
                tier = tb["tier"]
                if tier == "E":
                    stats["E_reject"] += 1
                    log.append({"file": fn, "level": lv, "status": "E_reject", "reason": tb["reason"]})
                    print("  ⊘ E:", fn[:60])
                    q.task_done(); continue
                if tb["text_len"] < 30:
                    stats["too_short"] += 1
                    log.append({"file": fn, "level": lv, "status": "too_short", "len": tb["text_len"]})
                    print("  ⊘ short:", fn[:60], tb["text_len"])
                    q.task_done(); continue
                model = MODEL_BY_TIER.get(tier, "deepseek/deepseek-v4-flash-0731")
                content, usage = call(tb["text"], model)
                r = parse_json(content)
                if not r:
                    stats["bad_json"] += 1
                    log.append({"file": fn, "level": lv, "status": "bad_json"})
                    print("  ✗ json:", fn[:60])
                    q.task_done(); continue
                # §5 schema normalisation
                r.setdefault("program", lv)
                if r.get("program") not in ("ba", "ma", "lang", "junior"):
                    r["program"] = lv
                if lv == "lang":                     # invariant: lang has no language req
                    r["topik"] = r["ielts"] = r["toefl"] = None
                    # the vision/LLM pass sometimes puts the program name (한국어교육원/한국어학당)
                    # into `majors`; a language course has no majors, so force it empty
                    r["majors"] = []
                # evidence check
                sys.path.insert(0, BASE)
                from kb_verify import evidence_in_text
                ev = evidence_in_text(r, tb["text"])
                r["_file"] = fn
                r["_level"] = lv
                r["_source"] = "LLM-parsed-LIBRARY(router)"
                r["_meta"] = {"tier": tier, "text_len": tb["text_len"], "ocr": tb.get("ocr_used"),
                              "model": model, "prompt_ver": "v4-lib", "evidence": ev,
                              "parsed_at": time.strftime("%Y-%m-%dT%H:%M:%S")}
                r["_usage"] = usage
                with lock:
                    out.write(json.dumps(r, ensure_ascii=False) + "\n"); out.flush()
                    stats["ok_" + tier] += 1
                    log.append({"file": fn, "level": lv, "status": "ok", "tier": tier,
                                "school": r.get("school"), "majors": len(r.get("majors") or []),
                                "period": r.get("period"), "topik": r.get("topik"), "ielts": r.get("ielts")})
                print("  ✓ [%s] %-40s %-16s time=%s ev=%s" % (tier, fn[:40], r.get("school"), r.get("period"), ev))
            except Exception as e:
                stats["error"] += 1
                log.append({"file": fn, "level": lv, "status": "error", "err": str(e)[:200]})
                print("  ✗", fn[:60], str(e)[:100])
            q.task_done()

    ths = [threading.Thread(target=worker, daemon=True) for _ in range(a.workers)]
    for t in ths:
        t.start()
    for t in ths:
        t.join()
    out.close()
    print("stats:", dict(stats))
    json.dump({"stats": dict(stats), "log": log, "ran_at": time.strftime("%Y-%m-%dT%H:%M:%S")},
              open(REPORT if not a.inventory else REPORT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("→", OUT, "|", REPORT)


if __name__ == "__main__":
    main()
