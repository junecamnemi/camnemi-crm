#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Parse the newly-collected REAL guide PDFs (real/ folders) with DeepSeek V4-Pro."""
import os, sys, json, glob, threading, queue, re, time, urllib.request
import pymupdf

BASE = r"C:\Users\USER\camnemi-crm\backend"
UP = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project"
OUT = os.path.join(BASE, "guides_llm_parsed_real.jsonl")
DIRS = [os.path.join(UP, "adiga_2026_전문대학_모집요강", "real"),
        os.path.join(UP, "adiga_2026_어학연수_모집요강", "real"),
        os.path.join(UP, "adiga_2027_어학연수_모집요강", "real")]

def _load_auth():
    shared = r"C:\Users\USER\AppData\Local\hermes\shared\nous_auth.json"
    if os.path.exists(shared):
        d = json.load(open(shared, encoding="utf-8"))
        if d.get("access_token"):
            return d["access_token"], d["inference_base_url"].rstrip("/")
    a = json.load(open(r"C:\Users\USER\AppData\Local\hermes\auth.json", encoding="utf-8"))["providers"]["nous"]
    return (a.get("agent_key") or a.get("access_token")), a["inference_base_url"].rstrip("/")

API_KEY, API_BASE = _load_auth()

# ARCHITECTURE §3 model ladder: cheap model for clean text (A/B), reasoning model for hard (C/D)
MODEL_BY_TIER = {"A": "deepseek/deepseek-v4-flash-0731", "B": "deepseek/deepseek-v4-flash-0731",
                 "C": "deepseek/deepseek-v4-pro", "D": "deepseek/deepseek-v4-pro"}
MAXTOK = {"deepseek/deepseek-v4-flash-0731": 24000, "deepseek/deepseek-v4-pro": 24000}
DEFAULT_MODEL = "deepseek/deepseek-v4-flash-0731"
PROMPT = """한국 대학 외국인 모집요강 텍스트에서 정보를 추출해 JSON만 출력하세요(설명 금지):
{"school":"대학명(한글)", "program":"ba|ma|lang|junior", "year":"2026|2027|unknown",
 "period":"원서접수 기간", "topik":TOPIK최소급수 또는 null, "ielts":IELTS최소 또는 null,
 "toefl":TOEFL최소 또는 null, "majors":["모집학과 전체"],
 "tuition_note":"등록금 한 줄", "scholarship_note":"장학금 한 줄"}
중요: 텍스트에 실제로 적힌 값만. 없으면 null (추측 금지).

=== 모집요강 텍스트 ===
"""

def call(text, model=None, retries=3):
    model = model or DEFAULT_MODEL
    mt = MAXTOK.get(model, 8000)
    body = {"model": model, "messages": [{"role": "user", "content": PROMPT + text[:14000]}],
            "temperature": 0, "max_tokens": mt}
    last = None
    for k in range(retries):
        try:
            req = urllib.request.Request(API_BASE + "/chat/completions", data=json.dumps(body).encode(),
                headers={"Authorization": "Bearer " + API_KEY, "Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=300) as r:
                j = json.loads(r.read().decode())
            msg = (j.get("choices") or [{}])[0].get("message") or {}
            content = msg.get("content") or msg.get("reasoning") or msg.get("reasoning_content") or ""
            if content and content.strip():
                return content, {**j.get("usage", {}), "_model": model}
            last = f"empty content (finish={(j.get('choices') or [{}])[0].get('finish_reason')})"
        except Exception as e:
            last = str(e)[:100]
        time.sleep(2)
    raise RuntimeError(f"no content [{model}]: {last}")

def parse_json(s):
    if s is None:
        return None
    s = re.sub(r"^```(json)?|```$", "", str(s).strip(), flags=re.M).strip()
    m = re.search(r"\{.*\}", s, re.S)
    return json.loads(m.group(0)) if m else None

_OCR = None
def _get_ocr():
    global _OCR
    if _OCR is None:
        from rapidocr_onnxruntime import RapidOCR
        _OCR = RapidOCR()
    return _OCR

def main():
    files = []
    for d in DIRS:
        files += sorted(glob.glob(os.path.join(d, "*.pdf")))
    done = set()
    if os.path.exists(OUT):
        for l in open(OUT, encoding="utf-8"):
            try: done.add(json.loads(l)["_id"])
            except Exception: pass
    q = queue.Queue()
    for f in files:
        if os.path.basename(f) not in done:
            q.put(f)
    print(f"대상 PDF: {len(files)} | 신규: {q.qsize()}")
    lock = threading.Lock(); out = open(OUT, "a", encoding="utf-8")

    def pdf_text(f):
        d = pymupdf.open(f)
        txt = "\n".join(d[i].get_text() for i in range(len(d)))
        if len(txt.strip()) < 50:
            # image-only → OCR fallback
            try:
                import numpy as np
                from rapidocr_onnxruntime import RapidOCR
                ocr = _get_ocr()
                parts = []
                for i in range(len(d)):
                    pix = d[i].get_pixmap(dpi=200)
                    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
                    if pix.n == 4: img = img[:, :, :3]
                    res, _ = ocr(img)
                    if res: parts.append("\n".join(r[1] for r in res))
                txt = "\n".join(parts)
            except Exception as e:
                txt = txt or ""
        d.close()
        return re.sub(r"[\s\x00-\x1f]+", " ", txt), len(txt.strip())

    def worker():
        global _OCR
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from doc_tier import classify
        while True:
            try: f = q.get_nowait()
            except queue.Empty: return
            try:
                tb = classify(f, allow_ocr=True)          # §2 tier router (incl. OCR fallback)
                tier = tb["tier"]
                if tier == "E":
                    print("  ⊘ E(비문서·재수집 반려):", os.path.basename(f)); q.task_done(); continue
                if tb["text_len"] < 30:
                    print("  ⊘ 텍스트부족(OCR후):", os.path.basename(f), tb["text_len"]); q.task_done(); continue
                model = MODEL_BY_TIER.get(tier, DEFAULT_MODEL)
                content, usage = call(tb["text"], model=model)
                r = parse_json(content)
                if r:
                    r["_id"] = os.path.basename(f); r["_file"] = os.path.basename(f)
                    r["_usage"] = usage; r["_source"] = "LLM-parsed-REAL(router)"
                    r["_meta"] = {"tier": tier, "text_len": tb["text_len"], "ocr": tb.get("ocr_used"),
                                  "model": model, "prompt_ver": "v3"}
                    with lock:
                        out.write(json.dumps(r, ensure_ascii=False) + "\n"); out.flush()
                    print(f"  ✓ [{tier}/{model.split('/')[-1]}]", r.get("school"), "| majors:", len(r.get("majors") or []))
            except Exception as e:
                print("  ✗", os.path.basename(f), str(e)[:80])
            q.task_done()

    ths = [threading.Thread(target=worker, daemon=True) for _ in range(6)]
    for t in ths: t.start()
    for t in ths: t.join()
    out.close()
    print("완료 →", OUT)

if __name__ == "__main__":
    main()
