#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""T3 adjudication (Opus) of tuition unit conflicts + a learned rule pack for Pro.

For every school flagged in `_tuition_conflicts.json` (college table vs summary one-liner
disagree — usually annual vs semester, or 입학금 included), Opus reads the KB evidence AND the
guide PDF's 등록금 section and must return, with a verbatim quote:

    {"unit":"semester|annual|unknown", "admission_fee_included":true|false,
     "undergrad_semester_krw":int|null, "evidence_quote":"...", "verdict":"...", "confidence":"high|low"}

Output:
    backend/_tuition_conflict_verdicts.jsonl   (one verdict per school level, resumable)
    backend/tuition_unit_rules.json            (rules distilled from the verdicts → Pro's rule pack)
    backend/tuition_rule_pack.md               (the compact prompt Pro consumes)

Run:  python _tuition_opus_adjudicate.py            # adjudicate pending conflicts
      python _tuition_opus_adjudicate.py --learn    # only rebuild rules from existing verdicts
"""
import os, re, json, urllib.request, sys, collections

B = os.path.dirname(os.path.abspath(__file__))
MODEL = "anthropic/claude-opus-5"          # T3 — judgement tier
OUT = os.path.join(B, "_tuition_conflict_verdicts.jsonl")
RULES = os.path.join(B, "tuition_unit_rules.json")
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


PROMPT = """너는 한국 대학 등록금 표의 단위(학기/연간)와 포함항목을 판정하는 감사자다.

아래 증거만 근거로 판정하고, **증거 문장을 그대로 인용**하라. 추측 금지. 판정 불가면 unknown.
다른 말 금지, JSON 하나만 출력:
{"unit":"semester|annual|unknown","admission_fee_included":true|false,
 "undergrad_semester_krw":정수 또는 null,"evidence_quote":"요강 원문 그대로",
 "verdict":"한 문장 판정","confidence":"high|low"}

판정 규칙:
- 요강에 "학기", "1학기 기준" → semester / "연간", "/년", "1년" → annual
- 계열표 금액이 연간이면 undergrad_semester_krw = 학기값(반올림 없이 2로 나눈 정수)
- 이미 학기값이면 표의 학부 최소~최대 중 최소값
- 입학금/전형료가 표에 포함돼 있으면 admission_fee_included=true

=== 증거 ===
"""


def extract_guide_text(v):
    """등록금 section of the school's effective guide PDF, if we can read it."""
    path = v.get("guide_effective_pdf") or v.get("guide_pdf") or ""
    if not path:
        return None, None
    p = path if os.path.exists(path) else None
    if not p:
        # try the known library root
        g = r"G:\공유 드라이브\Hermes\Camnemi\02_Crawling_Sheet\University_Project\guides"
        base = os.path.basename(path)
        for lv in ("ba", "ma", "junior"):
            for y in ("2027", "2026"):
                cand = os.path.join(g, lv, y, base)
                if os.path.exists(cand):
                    p = cand
                    break
            if p:
                break
    if not p:
        return None, path
    try:
        import pymupdf
        doc = pymupdf.open(p)
        t = "".join(doc[i].get_text() for i in range(len(doc)))
        doc.close()
    except Exception:
        return None, path
    idx = [m.start() for m in re.finditer(r"등록금|수업료", t)]
    if not idx:
        return t[:6000], path
    # EVERY hit, not just the first: hit #1 is usually 반환규정/납부 prose, the table is far below.
    spans = []
    for o in idx:
        lo, hi = max(0, o - 350), min(len(t), o + 900)
        if spans and lo < spans[-1][1]:
            spans[-1] = (spans[-1][0], max(spans[-1][1], hi))
        else:
            spans.append((lo, hi))
    return "\n…\n".join(t[a:b] for a, b in spans)[:20000], path


def evidence_block(name, lvl, entry, kb_v):
    rows = "\n".join(f"  - {r['college']}: ₩{r['krw']:,} ({r['level']})" for r in entry.get("rows", [])[:25])
    return (f"학교: {name} [{lvl}]\n"
            f"KB 요약(tuition_semester): {entry.get('summary')}\n"
            f"KB 등록금 note: {entry.get('tuition_note')}\n"
            f"계열/대학별 표:\n{rows}\n")


def call(text):
    body = {"model": MODEL, "messages": [{"role": "user", "content": PROMPT + text[:16000]}],
            "max_tokens": 3000, "temperature": 0}
    req = urllib.request.Request(BASE_URL.rstrip("/") + "/chat/completions",
                                 data=json.dumps(body).encode(),
                                 headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=420) as r:
        d = json.loads(r.read())
    m = d["choices"][0]["message"]
    return m.get("content") or m.get("reasoning") or ""


def learn():
    """Distil the verdicts into deterministic rules + a compact rule pack for Pro."""
    seen = []
    if os.path.exists(OUT):
        for line in open(OUT, encoding="utf-8"):
            if line.strip():
                seen.append(json.loads(line))
    unit = collections.Counter(v.get("unit") for v in seen)
    fee = collections.Counter(bool(v.get("admission_fee_included")) for v in seen)
    rules = {
        "learned_from": {"model": MODEL, "verdicts": len(seen)},
        "unit_rules": [
            r"summary/표 문구에 '연간'·'/년'·'1년' → 표 금액은 연간이므로 학기값 = round(krw/2)",
            r"summary/표 문구에 '학기'·'1학기 기준' → 표 금액 그대로 학기값",
            r"계열표(…계열/…계) 행은 대학(…대학/…학부/…캠퍼스) 행이 있는 학교에서 grad_or_summary → 학부 범위에서 제외",
            r"어학연수/어학당/한국어교육원 금액은 등록금이 아님 → 제외",
            r"'입학금 포함' 문구가 없으면 표 값은 수업료만; 포함 문구가 있으면 입학금 차감 후 비교",
            r"(미분류) 행은 신뢰하지 않음",
            r"의·약·한의·치·수의 행은 학부지만 학교 대표 범위에서 분리해 별도 표기",
        ],
        "unit_counts": dict(unit),
        "admission_fee_included_counts": {str(k): v for k, v in fee.items()},
        "verdicts": [{"school": v.get("school"), "level": v.get("level"), "unit": v.get("unit"),
                      "sem_krw": v.get("undergrad_semester_krw"), "conf": v.get("confidence"),
                      "evidence": (v.get("evidence_quote") or "")[:200]} for v in seen],
    }
    json.dump(rules, open(RULES, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    pack = ["# Tuition unit rule pack (learned from Opus verdicts — Pro must follow)",
            "", f"Source: {len(seen)} Opus verdicts ({dict(unit)}).", "", "## Hard rules"]
    pack += [f"{i+1}. {r}" for i, r in enumerate(rules["unit_rules"])]
    pack += ["", "## School-specific verdicts (authoritative over the KB summary)"]
    for v in seen:
        pack.append(f"- {v.get('school')} [{v.get('level')}]: unit={v.get('unit')} · "
                    f"semester ₩{v.get('undergrad_semester_krw')} · {v.get('verdict') or ''}"
                    + (f" · \"{(v.get('evidence_quote') or '')[:90]}\"" if v.get('evidence_quote') else ""))
    open(PACK, "w", encoding="utf-8").write("\n".join(pack))
    print("WROTE", RULES, "and", PACK, "| verdicts:", len(seen), dict(unit))
    return rules


def main():
    if "--learn" in sys.argv or "--rules" in sys.argv:
        learn(); return
    conf = json.load(open(os.path.join(B, "_tuition_conflicts.json"), encoding="utf-8"))["conflicts"]
    kbidx = {}
    kb = json.load(open(os.path.join(B, "verified_kb.json"), encoding="utf-8"))
    for lvl, (sec, key) in (("BA", ("schools", None)), ("MA", ("master", "schools")), ("전문학사", ("junior", "schools"))):
        d = kb[sec]; d = d.get(key, {}) if key else d
        for n, v in d.items():
            kbidx[(n, lvl)] = v
    tbd = json.load(open(os.path.join(B, "tuition_by_department.json"), encoding="utf-8"))["schools"]
    done = set()
    if os.path.exists(OUT):
        for line in open(OUT, encoding="utf-8"):
            if line.strip():
                d = json.loads(line); done.add((d.get("school"), d.get("level")))
    todo = [c for c in conf if (c["school"], c["level"]) not in done]
    print(f"conflicts: {len(conf)} | already judged: {len(done)} | to do: {len(todo)}")
    ok = 0
    with open(OUT, "a", encoding="utf-8") as out:
        for c in todo:
            name, lvl = c["school"], c["level"]
            entry = (tbd.get(name) or {}).get(lvl) or {}
            v = kbidx.get((name, lvl), {})
            guide_txt, gpath = extract_guide_text(v)
            blk = evidence_block(name, lvl, entry, v)
            if guide_txt:
                blk += f"\n=== 요강 등록금 구간 (source: {os.path.basename(gpath or '')}) ===\n{guide_txt}\n"
            else:
                blk += "\n(요강 PDF 텍스트 확보 실패 — KB 증거만으로 판정, confidence=low)\n"
            try:
                raw = call(blk)
                m = re.search(r"\{.*\}", raw, re.S)
                if not m:
                    print("  NO-JSON", name, lvl); continue
                verdict = json.loads(m.group(0))
                verdict.update({"school": name, "level": lvl, "guide_file": os.path.basename(gpath or "") or None,
                                "guide_text_found": bool(guide_txt), "model": MODEL})
                out.write(json.dumps(verdict, ensure_ascii=False) + "\n")
                out.flush()
                ok += 1
                print(f"  ✔ {name} [{lvl}] unit={verdict.get('unit')} sem={verdict.get('undergrad_semester_krw')} "
                      f"({verdict.get('confidence')})")
            except Exception as e:
                print(f"  ERR {name} [{lvl}] {type(e).__name__}: {e}")
    print(f"judged {ok}/{len(todo)}")
    if ok:
        learn()


if __name__ == "__main__":
    BASE_URL, KEY = _auth()
    main()