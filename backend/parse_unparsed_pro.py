#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Parse ONLY genuinely-unparsed guide PDFs with DeepSeek V4-Pro.
Skips a file if its SCHOOL is already parsed (handles renamed/copy adiga files)
or its _file is already in guides_llm_parsed.jsonl. lang files like
"가천대_한국어교육원.pdf" are matched by school too. Appends to guides_llm_parsed.jsonl.
"""
import os, re, json, urllib.request

BASE = r"C:\Users\wisew\camnemi-crm\backend"
UP = r"C:\Users\wisew\내 드라이브\02_Crawling_Sheet\University_Project"
PARSED = os.path.join(BASE, "guides_llm_parsed.jsonl")
MODEL = "deepseek/deepseek-v4-pro"

def _auth():
    for p in [r"C:\Users\wisew\AppData\Local\hermes\shared\nous_auth.json", r"C:\Users\wisew\AppData\Local\hermes\auth.json"]:
        if not os.path.exists(p): continue
        d = json.load(open(p, encoding="utf-8"))
        if isinstance(d, dict) and d.get("access_token"):
            return d.get("inference_base_url") or "https://inference-api.nousresearch.com/v1", d["access_token"]
        n = (d.get("providers") or {}).get("nous") or {}
        if n.get("agent_key"):
            return n.get("inference_base_url") or "https://inference-api.nousresearch.com/v1", n["agent_key"]
    raise SystemExit("no auth")
BASE_URL, KEY = _auth()

PROMPT = """한국 대학 외국인 모집요강 텍스트에서 정보를 추출해 JSON만 출력하세요(설명·마크다운 금지):
{"school":"대학명(한글)", "program":"ba|ma|lang|junior", "year":"2026|2027|unknown",
 "period":"원서접수 기간(문자열)", "topik":TOPIK최소급수 숫자 또는 null, "ielts":IELTS최소 숫자 또는 null,
 "toefl":TOEFL최소 숫자 또는 null, "majors":["모집학과 전체 목록"],
 "tuition_note":"등록금 관련 한 줄 요약",
 "scholarships":[{"name":"장학금명", "condition":"지급조건(TOPIK/IELTS/성적 등)", "benefit":"혜택(수업료 %/금액/기간)"}]}

장학금 추출 규칙: 요강에 나온 모든 장학금 등급/조건/혜택을 배열로 추출. 없으면 [].
=== 모집요강 텍스트 ===
"""

def school_from(fname):
    m = re.search(r'([가-힣A-Za-z]+(?:대학교|대학|전문대학|교육원))', fname)
    return m.group(1) if m else fname

def list_unparsed():
    parsed_schools = set()
    parsed_files = set()
    if os.path.exists(PARSED):
        for l in open(PARSED, encoding="utf-8"):
            if l.strip():
                try:
                    d = json.loads(l)
                    if d.get("school"): parsed_schools.add(d["school"])
                    if d.get("_file"): parsed_files.add(d["_file"])
                except Exception: pass
    out = []
    for prog in ["ba", "ma", "junior", "lang"]:
        for y in ["2026", "2027"]:
            d = os.path.join(UP, "guides", prog, y)
            if not os.path.isdir(d): continue
            for f in os.listdir(d):
                if not f.endswith(".pdf"): continue
                if f in parsed_files: continue
                s = school_from(f)
                if s in parsed_schools: continue
                out.append((os.path.join(d, f), prog, y, s))
    return out

def extract_text(path):
    import pymupdf
    doc = pymupdf.open(path)
    t = "".join(doc[i].get_text() for i in range(min(len(doc), 12)))
    doc.close()
    return t

def call(text, retries=3):
    for i in range(retries):
        try:
            body = {"model": MODEL, "messages": [{"role": "user", "content": PROMPT + text[:14000]}],
                    "max_tokens": 4000, "temperature": 0}
            req = urllib.request.Request(BASE_URL.rstrip("/") + "/chat/completions",
                                         data=json.dumps(body).encode(),
                                         headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=300) as r:
                d = json.loads(r.read())
            m = d["choices"][0]["message"]
            return m.get("content") or m.get("reasoning") or ""
        except Exception as e:
            if i == retries - 1:
                raise
            continue

def main():
    items = list_unparsed()
    print(f"진짜 미파싱 대상: {len(items)}")
    from collections import Counter
    print("레벨별:", Counter(p for _, p, _, _ in items))
    ok = 0
    with open(PARSED, "a", encoding="utf-8") as out:
        for path, prog, year, school in items:
            try:
                txt = extract_text(path)
                if len(txt.strip()) < 50:
                    print(f"  SKIP(텍스트부족): {os.path.basename(path)}")
                    continue
                resp = call(txt)
                m = re.search(r'\{.*\}', resp, re.S)
                if not m:
                    print(f"  FAIL(no json): {os.path.basename(path)}")
                    continue
                d = json.loads(m.group(0))
                d["_file"] = os.path.basename(path)
                d["_prog_hint"] = prog
                d["_year_hint"] = year
                out.write(json.dumps(d, ensure_ascii=False) + "\n")
                ok += 1
                print(f"  OK: {school} [{prog}]")
            except Exception as e:
                print(f"  ERR: {os.path.basename(path)} {type(e).__name__}")
    print(f"완료: {ok}/{len(items)} 파싱")

if __name__ == "__main__":
    main()