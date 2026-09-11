#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""kb_verify.py — deterministic verification + confidence score + escalation (ARCHITECTURE §4·§5).

score = 0.4*source_tier + 0.3*schema_ok + 0.2*evidence_in_text + 0.1*cross_match
  >= 0.80  -> ACCEPT   (merge)
  0.50-0.80-> ESCALATE (re-parse with T2/pro)
  < 0.50   -> REVIEW   (human; never auto-merge)

Usage:
  python kb_verify.py <extract.jsonl> [--text-dir DIR] [--out report.json]
"""
import json, os, re, sys, argparse, glob

TIER_SCORE = {"A": 1.0, "B": 0.8, "C": 0.5, "D": 0.2, "E": 0.0}
REQUIRED = ["school", "level"]

def norm(s):
    return re.sub(r"\s+", "", str(s or ""))

def schema_ok(rec):
    """§5 schema contract: required fields + lang invariant + types."""
    problems = []
    for f in REQUIRED:
        if not rec.get(f):
            problems.append(f"missing:{f}")
    lvl = rec.get("level")
    if lvl and lvl not in ("ba", "ma", "lang", "junior"):
        problems.append(f"bad level:{lvl}")
    # INVARIANT: lang programs have no TOPIK/IELTS requirement
    if lvl == "lang":
        r = rec.get("requirements") or {}
        if rec.get("topik") or rec.get("ielts") or rec.get("toefl") or r.get("topik") or r.get("ielts"):
            problems.append("invariant:lang_has_lang_req")
    # year must be int-ish or null
    y = rec.get("year")
    if y not in (None, "unknown") and not re.fullmatch(r"20\d\d", str(y)):
        problems.append(f"bad year:{y}")
    return (len(problems) == 0), problems

def evidence_in_text(rec, text):
    """Do the extracted values actually appear in the source text?"""
    if not text:
        return None  # cannot check
    t = norm(text)
    checked = hit = 0
    for f in ("topik", "ielts", "toefl"):
        v = rec.get(f)
        if v in (None, ""):
            continue
        checked += 1
        # accept bare number OR number near its label
        if str(v) in t:
            hit += 1
    maj = [m for m in (rec.get("majors") or []) if m]
    if maj:
        checked += 1
        pres = sum(1 for m in maj if norm(m) and norm(m) in t)
        if pres / len(maj) >= 0.6:
            hit += 1
    return (hit / checked) if checked else None

def cross_match(rec, kb_index):
    """Does an existing KB value agree? (agreement or absence counts, conflict penalizes)"""
    if kb_index is None:
        return None
    key = norm(rec.get("school"))
    ent = kb_index.get(key)
    if not ent:
        return None
    for f in ("topik", "ielts"):
        a, b = rec.get(f), ent.get(f)
        if a is not None and b is not None:
            return 1.0 if str(a) == str(b) else 0.0
    return 0.5  # present but nothing comparable

def score(rec, tier="B", text=None, kb_index=None):
    s = 0.0
    parts = {}
    ts = TIER_SCORE.get(str(tier).upper(), 0.5)
    s += 0.4 * ts; parts["tier"] = 0.4 * ts
    ok, probs = schema_ok(rec)
    s += 0.3 * (1.0 if ok else 0.0); parts["schema"] = 0.3 * (1.0 if ok else 0.0)
    ev = evidence_in_text(rec, text)
    evv = 0.5 if ev is None else ev
    s += 0.2 * evv; parts["evidence"] = 0.2 * evv
    cm = cross_match(rec, kb_index)
    cmv = 0.5 if cm is None else cm
    s += 0.1 * cmv; parts["cross"] = 0.1 * cmv
    verdict = "ACCEPT" if s >= 0.8 else ("ESCALATE" if s >= 0.5 else "REVIEW")
    return round(s, 3), verdict, parts, probs

def load_kb_index():
    kb = None
    for p in (r"C:\Users\USER\camnemi-crm\backend\verified_kb.json",):
        if os.path.exists(p):
            kb = json.load(open(p, encoding="utf-8"))
    if not kb:
        return None
    idx = {}
    secs = [("schools", None), ("master", "schools"), ("junior", "schools"), ("lang_programs", "schools")]
    for a, b in secs:
        d = kb[a][b] if b else kb[a]
        for k, v in d.items():
            idx[norm(k)] = {"topik": v.get("topik_req"), "ielts": v.get("ielts_req")}
    return idx

def normalize_record(r, tb=None):
    """Map a raw parser output into the §5 canonical schema (program->level, etc.)."""
    lvl = str(r.get("level") or r.get("program") or "").strip().lower()
    lvl = {"ba": "ba", "ma": "ma", "lang": "lang", "junior": "junior",
           "어학연수": "lang", "전문학사": "junior", "대학원": "ma", "학부": "ba"}.get(lvl, "")
    if not lvl:
        fn = str(r.get("_file") or r.get("_id") or "")
        if "전문학사" in fn or "전문대" in fn: lvl = "junior"
        elif "한국어교육" in fn or "어학연수" in fn: lvl = "lang"
        elif "대학원" in fn: lvl = "ma"
        else: lvl = "ba"
    out = {
        "school": r.get("school"),
        "level": lvl,
        "year": r.get("year"),
        "period": r.get("period"),
        "majors": r.get("majors") or [],
        "topik": r.get("topik"), "ielts": r.get("ielts"), "toefl": r.get("toefl"),
        "tuition": r.get("tuition_note"), "scholarship": r.get("scholarship_note"),
    }
    # §5 INVARIANT: lang programs carry no language requirement
    if lvl == "lang":
        out["topik"] = out["ielts"] = out["toefl"] = None
    if tb:
        out["_meta"] = {"tier": tb.get("tier"), "text_len": tb.get("text_len"),
                        "source_pdf": os.path.basename(tb.get("path", "")),
                        "model": (r.get("_meta") or {}).get("model"), "prompt_ver": "v3"}
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("jsonl")
    ap.add_argument("--out")
    a = ap.parse_args()
    raw = [json.loads(l) for l in open(a.jsonl, encoding="utf-8") if l.strip()]
    rows = [normalize_record(r) for r in raw]
    kb_index = load_kb_index()
    # text cache: OCR text + real guide PDFs (by filename)
    text_cache = {}
    BASEB = r"C:\Users\USER\camnemi-crm\backend"
    for f in glob.glob(os.path.join(BASEB, "_ocr_text", "*.txt")):
        text_cache[os.path.splitext(os.path.basename(f))[0]] = open(f, encoding="utf-8").read()
    UP = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project"
    pdf_index = {}
    for p in glob.glob(os.path.join(UP, "**", "*.pdf"), recursive=True):
        pdf_index.setdefault(os.path.basename(p), p)

    def text_for(rec):
        stem = os.path.splitext(str(rec.get("_file") or rec.get("_id") or ""))[0]
        if stem in text_cache:
            return text_cache[stem]
        p = pdf_index.get(str(rec.get("_file") or ""))
        if p:
            try:
                import pymupdf
                d = pymupdf.open(p)
                t = re.sub(r"[\s\x00-\x1f]+", " ", "\n".join(d[i].get_text() for i in range(len(d))))
                d.close()
                return t
            except Exception:
                return None
        return None

    rep = []
    for raw_r, r in zip(raw, rows):
        txt = text_for(raw_r)
        tlen = len(txt or "")
        tier = (r.get("_meta") or {}).get("tier") or ("A" if tlen >= 5000 else ("B" if tlen >= 1000 else ("C" if tlen >= 200 else "D")))
        s, v, parts, probs = score(r, tier=tier, text=txt, kb_index=kb_index)
        rep.append({"school": r.get("school"), "level": r.get("level"), "score": s, "verdict": v, "parts": parts, "problems": probs})
    from collections import Counter
    c = Counter(x["verdict"] for x in rep)
    print(f"검증 {len(rep)}건: {dict(c)}")
    for x in rep:
        flag = "⚠" if x["verdict"] != "ACCEPT" else " "
        print(f"  {flag} {str(x['school'])[:24]:24s} {x['score']:.2f} {x['verdict']:8s} {x['problems']}")
    if a.out:
        json.dump(rep, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("저장:", a.out)

if __name__ == "__main__":
    main()
