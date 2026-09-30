#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Retry the library-parse failures (bad_json / error) with an escalated model.

Reads _library_parse_report.json → entries whose status is bad_json or error,
re-classifies the PDF, re-calls (flash → pro on second attempt) and appends the
successful rows to _parse_library.jsonl.
"""
import os, sys, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _parse_library_batch as P
from doc_tier import classify
from kb_verify import evidence_in_text

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "_parse_library.jsonl")
REPORT = os.path.join(BASE, "_library_parse_report.json")
LIB = P.LIB

COMPACT = """한국 대학 외국인 모집요강 텍스트에서 정보를 추출해 JSON만 출력하세요(설명·주석 금지):
{"school":"대학명", "program":"ba|ma|lang|junior", "year":"2026|2027|unknown",
 "period":"원서접수 기간", "topik":TOPIK최소 또는 null, "ielts":IELTS최소 또는 null,
 "toefl":TOEFL최소 또는 null, "majors":["학과 (최대 80개)"],
 "tuition_note":null, "scholarship_note":null}
텍스트에 실제로 적힌 값만. 없으면 null. 반드시 유효한 JSON 하나만 출력하고 즉시 닫으세요.

=== 텍스트 ===
"""


def main():
    rep = json.load(open(REPORT, encoding="utf-8"))
    failed = [e for e in rep.get("log", []) if e.get("status") in ("bad_json", "error")]
    print("retry targets:", [f["file"] for f in failed])
    # locate each file in the library
    found = {}
    for lv, yr in P.CURRENT_DIRS:
        d = os.path.join(LIB, lv, yr)
        if not os.path.isdir(d):
            continue
        for fn in os.listdir(d):
            if fn.lower().endswith(".pdf"):
                found[fn] = (os.path.join(d, fn), lv)
    for e in failed:
        fn = e["file"]
        if fn not in found:
            print("  ? not in library:", fn); continue
        path, lv = found[fn]
        ok = False
        for attempt, model in enumerate(("deepseek/deepseek-v4-flash-0731", "deepseek/deepseek-v4-pro")):
            try:
                tb = classify(path, allow_ocr=True)
                if tb["tier"] == "E" or tb["text_len"] < 30:
                    print("  ⊘", fn, "tier", tb["tier"], tb["text_len"]); ok = True; break
                prompt_text = tb["text"]
                content, usage = P.call(prompt_text, model)
                r = P.parse_json(content)
                if not r:
                    # second attempt: compact prompt (no long note fields, majors capped)
                    body_prompt = COMPACT + prompt_text[:14000]
                    import urllib.request
                    tok, base = P.load_auth()
                    req = urllib.request.Request(base + "/chat/completions",
                        data=json.dumps({"model": model, "messages": [{"role": "user", "content": body_prompt}],
                                         "temperature": 0, "max_tokens": P.MAXTOK}).encode(),
                        headers={"Authorization": "Bearer " + tok, "Content-Type": "application/json"})
                    with urllib.request.urlopen(req, timeout=420) as rr:
                        j = json.loads(rr.read().decode())
                    msg = (j.get("choices") or [{}])[0].get("message") or {}
                    content = msg.get("content") or msg.get("reasoning") or msg.get("reasoning_content") or ""
                    r = P.parse_json(content); usage = j.get("usage", {})
                if not r:
                    print("  ✗ json again:", fn, "[%s]" % model.split("/")[-1]); continue
                r.setdefault("program", lv)
                if r.get("program") not in ("ba", "ma", "lang", "junior"):
                    r["program"] = lv
                if lv == "lang":
                    r["topik"] = r["ielts"] = r["toefl"] = None
                ev = evidence_in_text(r, tb["text"])
                r["_file"] = fn; r["_level"] = lv
                r["_source"] = "LLM-parsed-LIBRARY(router-retry)"
                r["_meta"] = {"tier": tb["tier"], "text_len": tb["text_len"], "ocr": tb.get("ocr_used"),
                              "model": model, "prompt_ver": "v4-lib-retry", "evidence": ev,
                              "parsed_at": time.strftime("%Y-%m-%dT%H:%M:%S")}
                r["_usage"] = usage
                with open(OUT, "a", encoding="utf-8") as fh:
                    fh.write(json.dumps(r, ensure_ascii=False) + "\n")
                print("  ✓ [%s] %-45s %-14s majors=%s ev=%s" % (tb["tier"], fn[:45], r.get("school"),
                                                                 len(r.get("majors") or []), ev))
                ok = True
                break
            except Exception as ex:
                print("  ✗ err", fn, str(ex)[:90])
        if not ok:
            print("  !! still failing:", fn)


if __name__ == "__main__":
    main()