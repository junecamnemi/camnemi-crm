#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Classify the APPLICATION/SUBMISSION system of every 모집요강 with DeepSeek V4-Pro.

For each guide PDF: extract the admission-relevant pages (접수/원서/지원), send to
deepseek-v4-pro, get {primary, all[], evidence}. Resumable + auto token refresh.
Output: _apply_pro.jsonl
"""
import os, re, json, glob, time, threading, queue, urllib.request
import pymupdf

BASE = r"C:\Users\USER\camnemi-crm\backend"
UP = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project"
OUT = os.path.join(BASE, "_apply_pro.jsonl")
FOLDERS = {
    "학부": ["adiga_2026_외국인_모집요강", "adiga_2027_외국인_모집요강"],
    "전문대": ["adiga_2026_전문대학_모집요강"],
    "대학원": ["adiga_2026_대학원_모집요강", "adiga_2027_대학원_모집요강"],
    "어학연수": ["adiga_2026_어학연수_모집요강", "adiga_2027_어학연수_모집요강"],
}
MODEL = "deepseek/deepseek-v4-pro"
PROMPT = """다음은 한국 대학의 외국인 모집요강 텍스트입니다. **원서접수(지원) 방법**만 판별해 JSON으로 출력하세요(설명 금지):
{"primary":"유웨이어플라이|진학어플라이|홈페이지|이메일|우편|방문|미기재 중 하나",
 "all":["해당되는 것 모두"],
 "evidence":"원서접수 방법을 알 수 있는 원문 문장 인용(없으면 null)"}

판단 기준:
- 유웨이어플라이 = uwayapply.com / 유웨이어플라이 / 유웨이
- 진학어플라이 = jinhakapply.com / 진학어플라이 / 진학사
- 홈페이지 = 학교 입학 홈페이지·온라인 접수·인터넷 원서접수
- 이메일 = 이메일/메일로 서류·원서 제출
- 우편 = 등기우편 제출 / 방문 = 직접 방문 접수
주의: 단순 연락처 이메일(문의용)은 이메일 제출이 아님. 문서 제출용일 때만 인정.

=== 모집요강 텍스트 ===
"""

def load_auth():
    s = r"C:\Users\USER\AppData\Local\hermes\shared\nous_auth.json"
    if os.path.exists(s):
        d = json.load(open(s, encoding="utf-8"))
        if d.get("access_token"):
            return d["access_token"], d["inference_base_url"].rstrip("/")
    a = json.load(open(r"C:\Users\USER\AppData\Local\hermes\auth.json", encoding="utf-8"))["providers"]["nous"]
    return (a.get("agent_key") or a.get("access_token")), a["inference_base_url"].rstrip("/")

TOK, URL = load_auth()
LOCK = threading.Lock()

def call(text, retries=3):
    global TOK, URL
    body = {"model": MODEL, "messages": [{"role": "user", "content": PROMPT + text[:9000]}],
            "temperature": 0, "max_tokens": 24000}
    last = None
    for _ in range(retries):
        try:
            req = urllib.request.Request(URL + "/chat/completions", data=json.dumps(body).encode(),
                headers={"Authorization": "Bearer " + TOK, "Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=300) as r:
                j = json.loads(r.read().decode())
            msg = (j.get("choices") or [{}])[0].get("message") or {}
            c = msg.get("content") or msg.get("reasoning") or ""
            if c and c.strip():
                return c, j.get("usage", {})
            last = "empty"
        except Exception as e:
            last = str(e)[:80]
            if "401" in last:
                TOK, URL = load_auth()
        time.sleep(2)
    raise RuntimeError(last)

def pj(s):
    s = re.sub(r"^```(json)?|```$", "", str(s).strip(), flags=re.M).strip()
    try:
        return json.loads(s)
    except Exception:
        pass
    dec = json.JSONDecoder()
    for m in re.finditer(r"\{", s):
        try:
            o, _ = dec.raw_decode(s[m.start():])
            if isinstance(o, dict) and "primary" in o:
                return o
        except Exception:
            continue
    return None

def admission_text(p):
    d = pymupdf.open(p)
    keep = []
    for i in range(min(len(d), 80)):
        t = d[i].get_text()
        if re.search(r"원서\s*접수|접수\s*방법|지원\s*방법|uway|진학|이메일|우편|홈페이지|인터넷\s*접수|입학원서", t):
            keep.append(re.sub(r"[\s\x00-\x1f]+", " ", t))
    if not keep:
        keep = [re.sub(r"[\s\x00-\x1f]+", " ", d[i].get_text()) for i in range(min(len(d), 20))]
    d.close()
    return "\n".join(keep)[:14000]

def level_of(p):
    for l, dirs in FOLDERS.items():
        if any(x in p for x in dirs):
            return l
    return "?"

def main():
    files = []
    for l, dirs in FOLDERS.items():
        for dd in dirs:
            files += [(l, p) for p in glob.glob(os.path.join(UP, dd, "**", "*.pdf"), recursive=True)]
    print(f"대상: {len(files)}개 PDF")
    done = set()
    if os.path.exists(OUT):
        for line in open(OUT, encoding="utf-8"):
            try: done.add(json.loads(line)["_id"])
            except Exception: pass
    q = queue.Queue()
    for l, p in files:
        if os.path.basename(p) not in done:
            q.put((l, p))
    print(f"신규: {q.qsize()} (기완료 {len(done)})")
    out = open(OUT, "a", encoding="utf-8")

    def worker():
        while True:
            try: l, p = q.get_nowait()
            except queue.Empty: return
            fn = os.path.basename(p)
            try:
                t = admission_text(p)
                if len(t) < 80:
                    r = {"primary": "미기재", "all": [], "evidence": None, "_note": "text too short"}
                else:
                    c, u = call(t)
                    r = pj(c) or {"primary": "미기재", "all": [], "evidence": None}
                r["_id"] = fn; r["_level"] = l; r["_file"] = fn
                with LOCK:
                    out.write(json.dumps(r, ensure_ascii=False) + "\n"); out.flush()
                print(f"  [{l}] {fn[:40]} → {r.get('primary')}")
            except Exception as e:
                print(f"  ✗ {fn[:40]} {str(e)[:70]}")
            q.task_done()

    ths = [threading.Thread(target=worker, daemon=True) for _ in range(8)]
    for t in ths: t.start()
    for t in ths: t.join()
    out.close()
    print("완료 →", OUT)

if __name__ == "__main__":
    main()
