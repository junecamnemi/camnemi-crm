#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Re-parse OCR'd guide text with DeepSeek V4-Pro (Nous gateway) -> guides_llm_parsed_ocr.jsonl.

Same prompt/model as parse_guides_deepseek.py, but input is the _ocr_text/*.txt files
produced for the low-text PDFs the first pass couldn't read.
"""
import os, sys, json, glob, argparse, time, threading, queue, re, urllib.request

BASE = r"C:\Users\USER\camnemi-crm\backend"
OCR_DIR = os.path.join(BASE, "_ocr_text")
OUT_JSONL = os.path.join(BASE, "guides_llm_parsed_ocr.jsonl")
TRUST = os.path.join(BASE, "_llmparse_trust.json")

def _load_auth():
    """Prefer the freshest token: shared/nous_auth.json (runtime-refreshed) → auth.json agent_key."""
    cands = []
    shared = r"C:\Users\USER\AppData\Local\hermes\shared\nous_auth.json"
    if os.path.exists(shared):
        d = json.load(open(shared, encoding="utf-8"))
        cands.append((d.get("access_token"), d.get("inference_base_url")))
    a = json.load(open(r"C:\Users\USER\AppData\Local\hermes\auth.json", encoding="utf-8"))["providers"]["nous"]
    cands.append((a.get("agent_key"), a.get("inference_base_url")))
    cands.append((a.get("access_token"), a.get("inference_base_url")))
    for tok, base in cands:
        if tok:
            return tok, (base or "https://inference-api.nousresearch.com/v1").rstrip("/")
    raise SystemExit("no token found")

API_KEY, API_BASE = _load_auth()
MODEL = "deepseek/deepseek-v4-pro"

PROMPT = """한국 대학 외국인 모집요강 텍스트에서 정보를 추출해 JSON만 출력하세요(설명·마크다운 금지):
{"school":"대학명(한글)", "program":"ba|ma|lang|junior", "year":"2026|2027|unknown",
 "period":"원서접수 기간(문자열)", "topik":TOPIK최소급수 숫자 또는 null, "ielts":IELTS최소 숫자 또는 null,
 "toefl":TOEFL최소 숫자 또는 null, "majors":["모집학과 전체 목록"],
 "tuition_note":"등록금 관련 한 줄 요약", "scholarship_note":"장학금 관련 한 줄 요약"}

중요: 아래 텍스트에 실제로 적힌 내용만 추출하세요. 텍스트에 없는 값은 null 로 두세요(추측 금지).

=== 모집요강 텍스트 (OCR) ===
"""

def call(text):
    body = {"model": MODEL, "messages": [{"role": "user", "content": PROMPT + text[:14000]}],
            "temperature": 0, "max_tokens": 4000}
    req = urllib.request.Request(API_BASE + "/chat/completions",
        data=json.dumps(body).encode(),
        headers={"Authorization": "Bearer " + API_KEY, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        j = json.loads(r.read().decode())
    return j["choices"][0]["message"]["content"], j.get("usage", {})

def parse_json(s):
    s = re.sub(r"^```(json)?|```$", "", s.strip(), flags=re.M).strip()
    m = re.search(r"\{.*\}", s, re.S)
    return json.loads(m.group(0)) if m else None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    trust = json.load(open(TRUST, encoding="utf-8"))["flagged"]
    meta = {os.path.splitext(i["file"])[0]: i for i in trust}
    files = sorted(glob.glob(os.path.join(OCR_DIR, "*.txt")))
    if args.limit:
        files = files[:args.limit]

    done = set()
    if os.path.exists(OUT_JSONL):
        for l in open(OUT_JSONL, encoding="utf-8"):
            try: done.add(json.loads(l)["_id"])
            except Exception: pass

    q = queue.Queue()
    for f in files:
        if os.path.splitext(os.path.basename(f))[0] not in done:
            q.put(f)
    lock = threading.Lock()
    out = open(OUT_JSONL, "a", encoding="utf-8")

    def worker():
        while True:
            try: f = q.get_nowait()
            except queue.Empty: return
            try:
                txt = open(f, encoding="utf-8").read()
                if len(txt.strip()) < 30:
                    q.task_done(); continue
                content, usage = call(txt)
                d = parse_json(content)
                if d:
                    stem = os.path.splitext(os.path.basename(f))[0]
                    d["_id"] = stem
                    d["_file"] = meta.get(stem, {}).get("file", stem + ".pdf")
                    d["_usage"] = usage
                    d["_source"] = "LLM(pro)-parsed-OCR"
                    with lock:
                        out.write(json.dumps(d, ensure_ascii=False) + "\n"); out.flush()
                    print("  ✓", d.get("school"))
            except Exception as e:
                print("  ✗", os.path.basename(f), str(e)[:80])
            q.task_done()

    ths = [threading.Thread(target=worker, daemon=True) for _ in range(args.workers)]
    for t in ths: t.start()
    for t in ths: t.join()
    out.close()
    print("완료 →", OUT_JSONL)

if __name__ == "__main__":
    main()
