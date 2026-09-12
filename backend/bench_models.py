#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""bench_models.py — benchmark candidate models on the Golden Set (ARCHITECTURE §3/§8).

Runs the SAME extraction prompt over N golden-set PDFs (which have a baseline) and
compares, per model: JSON success, latency, tokens, cost, majors Jaccard vs baseline,
period match, and schema validity.

Usage: python bench_models.py [--n 15] [--models a,b,c] [--out bench.json]
"""
import os, re, json, glob, argparse, time, urllib.request
import pymupdf

BASE = r"C:\Users\USER\camnemi-crm\backend"
GS = os.path.join(BASE, "golden_set.json")
UP = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project"

def _auth():
    d = json.load(open(r"C:\Users\USER\AppData\Local\hermes\shared\nous_auth.json", encoding="utf-8"))
    return d["access_token"], d["inference_base_url"].rstrip("/")

KEY, BASEURL = _auth()

DEFAULT_MODELS = [
    "deepseek/deepseek-v4-flash-0731",   # current T1 (reasoning)
    "z-ai/glm-5.3-flash",                # candidate (non-reasoning)
    "google/gemini-3.7-flash",           # candidate
    "qwen/qwen3.8-flash",                # candidate
]
MAXTOK = 24000  # generous headroom for reasoning models

PROMPT = """한국 대학 외국인 모집요강 텍스트에서 정보를 추출해 JSON만 출력하세요(설명 금지):
{"school":"대학명(한글)", "program":"ba|ma|lang|junior", "year":"2026|2027|unknown",
 "period":"원서접수 기간", "topik":TOPIK최소급수 또는 null, "ielts":IELTS최소 또는 null,
 "toefl":TOEFL최소 또는 null, "majors":["모집학과 전체"],
 "tuition_note":"등록금 한 줄", "scholarship_note":"장학금 한 줄"}
중요: 텍스트에 실제로 적힌 값만. 없으면 null (추측 금지).

=== 모집요강 텍스트 ===
"""

def norm(s):
    return re.sub(r"\s+", "", str(s or ""))

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

def call(model, text):
    body = {"model": model, "messages": [{"role": "user", "content": PROMPT + text[:14000]}],
            "temperature": 0, "max_tokens": MAXTOK}
    req = urllib.request.Request(BASEURL + "/chat/completions", data=json.dumps(body).encode(),
        headers={"Authorization": "Bearer " + KEY, "Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=300) as r:
        j = json.loads(r.read().decode())
    dt = time.time() - t0
    ch = (j.get("choices") or [{}])[0]
    msg = ch.get("message") or {}
    content = msg.get("content") or msg.get("reasoning") or msg.get("reasoning_content") or ""
    return content, j.get("usage", {}), dt, ch.get("finish_reason")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=15)
    ap.add_argument("--models")
    ap.add_argument("--out", default=os.path.join(BASE, "model_bench.json"))
    a = ap.parse_args()
    models = a.models.split(",") if a.models else DEFAULT_MODELS

    gs = json.load(open(GS, encoding="utf-8"))
    items = [x for x in gs["files"] if x.get("baseline")][:a.n]
    pdfs = {}
    for p in glob.glob(os.path.join(UP, "**", "*.pdf"), recursive=True):
        pdfs.setdefault(os.path.basename(p), p)
    print(f"벤치마크: {len(items)}개 PDF × {len(models)} 모델\n")

    results = {}
    for model in models:
        m = {"ok": 0, "json_fail": 0, "trunc": 0, "err": 0, "ms": [], "tokens": 0, "cost": 0.0,
             "jac": [], "period_ok": 0, "period_n": 0}
        for it in items:
            p = pdfs.get(it["file"])
            if not p:
                continue
            try:
                d = pymupdf.open(p)
                txt = re.sub(r"[\s\x00-\x1f]+", " ", "\n".join(d[i].get_text() for i in range(len(d))))
                d.close()
                if len(txt.strip()) < 50:
                    continue
                content, usage, dt, fin = call(model, txt)
                m["ms"].append(round(dt, 1))
                m["tokens"] += usage.get("total_tokens", 0)
                m["cost"] += float(usage.get("cost") or 0)
                if fin == "length":
                    m["trunc"] += 1
                r = parse_json(content)
                if not r:
                    m["json_fail"] += 1; continue
                m["ok"] += 1
                base = it["baseline"]
                bm, cm = set(map(norm, base.get("majors") or [])), set(map(norm, r.get("majors") or []))
                if bm or cm:
                    m["jac"].append(len(bm & cm) / len(bm | cm))
                if base.get("period") is not None:
                    m["period_n"] += 1
                    m["period_ok"] += int(str(base.get("period")) == str(r.get("period")))
            except Exception as e:
                m["err"] += 1
        results[model] = m
        jm = sum(m["jac"]) / len(m["jac"]) if m["jac"] else 0
        ms = sum(m["ms"]) / len(m["ms"]) if m["ms"] else 0
        print(f"  {model.split('/')[-1]:28s} ok={m['ok']:2d} fail={m['json_fail']} trunc={m['trunc']} err={m['err']} "
              f"| {ms:5.1f}s | {m['tokens']:>7,}tok | ${m['cost']:.4f} | jaccard={jm:.2f} "
              f"| period={m['period_ok']}/{m['period_n']}")

    # summary table
    print("\n=== 요약 (정확도 × 비용) ===")
    print(f"{'model':30s} {'json성공':>7} {'평균s':>7} {'총비용$':>9} {'jaccard':>8} {'period':>8}")
    for model, m in results.items():
        jm = sum(m["jac"]) / len(m["jac"]) if m["jac"] else 0
        ms = sum(m["ms"]) / len(m["ms"]) if m["ms"] else 0
        per = f"{m['period_ok']}/{m['period_n']}" if m["period_n"] else "-"
        print(f"{model:30s} {m['ok']:>3}/{m['ok']+m['json_fail']+m['trunc']:>3} {ms:>7.1f} {m['cost']:>9.4f} {jm:>8.2f} {per:>8}")
    json.dump(results, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("\n저장:", a.out)

if __name__ == "__main__":
    main()
