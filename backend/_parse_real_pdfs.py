#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Parse the newly-collected REAL guide PDFs (real/ folders) with DeepSeek V4-Pro."""
import os, sys, json, glob, threading, queue, re, urllib.request
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
MODEL = "deepseek/deepseek-v4-pro"
PROMPT = """한국 대학 외국인 모집요강 텍스트에서 정보를 추출해 JSON만 출력하세요(설명 금지):
{"school":"대학명(한글)", "program":"ba|ma|lang|junior", "year":"2026|2027|unknown",
 "period":"원서접수 기간", "topik":TOPIK최소급수 또는 null, "ielts":IELTS최소 또는 null,
 "toefl":TOEFL최소 또는 null, "majors":["모집학과 전체"],
 "tuition_note":"등록금 한 줄", "scholarship_note":"장학금 한 줄"}
중요: 텍스트에 실제로 적힌 값만. 없으면 null (추측 금지).

=== 모집요강 텍스트 ===
"""

def call(text):
    body = {"model": MODEL, "messages": [{"role": "user", "content": PROMPT + text[:14000]}],
            "temperature": 0, "max_tokens": 4000}
    req = urllib.request.Request(API_BASE + "/chat/completions", data=json.dumps(body).encode(),
        headers={"Authorization": "Bearer " + API_KEY, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        j = json.loads(r.read().decode())
    return j["choices"][0]["message"]["content"], j.get("usage", {})

def parse_json(s):
    s = re.sub(r"^```(json)?|```$", "", s.strip(), flags=re.M).strip()
    m = re.search(r"\{.*\}", s, re.S)
    return json.loads(m.group(0)) if m else None

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

    def worker():
        while True:
            try: f = q.get_nowait()
            except queue.Empty: return
            try:
                d = pymupdf.open(f)
                txt = re.sub(r"[\s\x00-\x1f]+", " ", "\n".join(d[i].get_text() for i in range(len(d))))
                d.close()
                if len(txt) < 50:
                    print("  ⊘ 텍스트부족:", os.path.basename(f), len(txt)); q.task_done(); continue
                content, usage = call(txt)
                r = parse_json(content)
                if r:
                    r["_id"] = os.path.basename(f); r["_file"] = os.path.basename(f)
                    r["_usage"] = usage; r["_source"] = "LLM(pro)-parsed-REAL"
                    with lock:
                        out.write(json.dumps(r, ensure_ascii=False) + "\n"); out.flush()
                    print("  ✓", r.get("school"), "| majors:", len(r.get("majors") or []))
            except Exception as e:
                print("  ✗", os.path.basename(f), str(e)[:70])
            q.task_done()

    ths = [threading.Thread(target=worker, daemon=True) for _ in range(6)]
    for t in ths: t.start()
    for t in ths: t.join()
    out.close()
    print("완료 →", OUT)

if __name__ == "__main__":
    main()
