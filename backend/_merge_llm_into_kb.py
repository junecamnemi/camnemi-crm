#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Merge LLM(pro)-parsed guides into verified_kb.json (fill-only, source-tagged).

Sources:
  guides_llm_parsed.jsonl      -> keep only records whose source PDF had >=1000 chars text (trusted)
  guides_llm_parsed_ocr.jsonl  -> OCR-based re-parse (pro), trusted (OCR text)
Fill rules: never overwrite an existing KB value. Add majors when absent. Tag every
touched field's origin in `_llm_parsed` so it stays auditable.

Usage: python _merge_llm_into_kb.py [--write]
"""
import json, os, sys, glob, re, argparse, shutil, datetime
from pathlib import Path

BASE = os.path.dirname(os.path.abspath(__file__))
KB = os.path.join(BASE, "verified_kb.json")
sys.path.insert(0, BASE)
import pipeline_paths as _pp  # ONE data home (_pipeline_data/parsed)
J1 = str(_pp.path("parsed"))
J2 = str(_pp.path("parsed_ocr"))
J3 = str(_pp.path("parsed_real"))   # newly-collected REAL guides
# J4: library batch parse (G: guides/{level}/{year}) — tier-routed + evidence-checked at parse time
J4 = str(_pp.PARSED_DIR / "guides_llm_parsed_library.jsonl")
TRUST = os.path.join(BASE, "_llmparse_trust.json")
AUDIT_PATH = str(_pp.REPORT_DIR / "_year_upgrade.json")
CURRENT_YEAR = "2027"   # a newer record year may only replace older values
_DRIVE_ROOTS = [Path(r"G:/공유 드라이브/Hermes/Camnemi/02_Crawling_Sheet/University_Project"),
                Path.home() / "내 드라이브" / "02_Crawling_Sheet" / "University_Project"]
UP = str(next((p for p in _DRIVE_ROOTS if (p / "guides").is_dir()), _DRIVE_ROOTS[-1]))

# Lazy: walking the library over the network drive costs minutes. Only build this map
# when the trust cache cannot answer (see trust gate in main()).
PDF_BY_NAME = {}
_PDF_INDEX_BUILT = False


def pdf_index():
    global _PDF_INDEX_BUILT
    if not _PDF_INDEX_BUILT:
        for p in glob.glob(os.path.join(UP, "**", "*.pdf"), recursive=True):
            PDF_BY_NAME.setdefault(os.path.basename(p), p)
        _PDF_INDEX_BUILT = True
    return PDF_BY_NAME

def tlen(path):
    import pymupdf
    try:
        d = pymupdf.open(path); n = sum(len(d[i].get_text()) for i in range(len(d))); d.close(); return n
    except Exception:
        return -1

def norm(s):
    return re.sub(r"[^가-힣a-zA-Z0-9]", "", str(s or "")).replace("대학교", "").replace("대학", "")

def load(path):
    if not os.path.exists(path): return []
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--write", action="store_true")
    ap.add_argument("--upgrade-years", action="store_true",
                    help="let a newer guide year replace older-year values (2027 wins over 2026)")
    args = ap.parse_args()
    AUDIT = []
    kb = json.load(open(KB, encoding="utf-8"))
    sections = {"ba": ("schools", None), "ma": ("master", "schools"), "lang": ("lang_programs", "schools"), "junior": ("junior", "schools")}

    def section_dict(sec):
        a, b = sections[sec]
        return kb[a][b] if b else kb[a]

    # build key index per section
    idx = {s: {norm(k): k for k in section_dict(s)} for s in sections}

    # Trust gate: prefer the cached trust report (flags only the untrusted PDFs), so we do
    # NOT re-open ~950 PDFs on the network drive. Fall back to a live text-length probe.
    flagged = None
    try:
        _t = json.load(open(TRUST, encoding="utf-8"))
        flagged = {x.get("file") for x in (_t.get("flagged") or []) if x.get("file")}
    except Exception:
        flagged = None
    recs = []
    for r in load(J1):
        fn = r.get("_file") or ""
        if flagged is not None:
            trusted = fn not in flagged
        else:
            p = pdf_index().get(fn)
            trusted = bool(p) and tlen(p) >= 1000
        if trusted:
            r["_trusted"] = True; recs.append(r)
    recs += load(J2)
    recs += load(J3)   # REAL guides (already tier-routed + OCR'd at parse time)
    recs += load(J4)   # library guides (G: guides/…) — trusted: tier-routed + evidence-checked
    # J5 = vision pass over the guides the text pipeline could not read (tier E / text≈0).
    # Vision reads the picture, so it fills gaps only — it must never overwrite a text-layer value.
    J5 = os.path.join(BASE, "_parse_library_vl.jsonl")
    recs += load(J5)
    # NOTE: the second number is every non-text-trusted record: OCR (J2) + real (J3) + library (J4).
    # It used to say "OCR", which reads as an OCR-only count and caused a false alarm (2026-09-29).
    print(f"병합 대상: {len(recs)} (text-trusted {sum(1 for r in recs if r.get('_trusted'))} + OCR/real {sum(1 for r in recs if not r.get('_trusted'))})")

    stats = {"matched": 0, "unmatched": 0, "majors_added": 0, "period_filled": 0, "lang_filled": 0,
             "tuition_note_filled": 0, "scholarship_note_filled": 0, "majors_unioned": 0}
    unmatched = set()
    for r in recs:
        # The collection folder is the routing source; LLM's program label can be wrong.
        sec = (r.get("_prog_hint") or r.get("program") or "ba").strip()
        if sec not in sections: sec = "ba"
        d = section_dict(sec)
        key = norm(r.get("school"))
        if not key:
            stats["unmatched"] += 1; continue
        real = idx[sec].get(key)
        if not real:
            # try containment within the same section
            for k2, orig in idx[sec].items():
                if key and (key in k2 or k2 in key):
                    real = orig; break
        if not real:
            # FALLBACK: search every other section (program hint may be wrong/'unknown')
            for alt in sections:
                if alt == sec:
                    continue
                real = idx[alt].get(key)
                if not real:
                    for k2, orig in idx[alt].items():
                        if key and (key in k2 or k2 in key):
                            real = orig; break
                if real:
                    sec = alt
                    break
        if not real:
            stats["unmatched"] += 1; unmatched.add(r.get("school")); continue
        stats["matched"] += 1
        v = section_dict(sec)[real]
        have_year = str(v.get("guide_year") or "")
        rec_year = str(r.get("year") or "")
        # The collection folder is the routing source; the model's year label is unreliable
        # (a guide sitting in the 2027 folder routinely comes back as "2026" or "unknown").
        # Trust the folder year when it is a real year and newer than the model's, or the
        # newly collected guide can never upgrade the KB and keeps serving last year's facts.
        hint_year = str(r.get("_year_hint") or "")
        if re.fullmatch(r"20\d\d", hint_year) and (
                not re.fullmatch(r"20\d\d", rec_year) or hint_year > rec_year):
            rec_year = hint_year
        # Only the CURRENT guide year may replace older values, and only forwards:
        # a 2026 record must never overwrite anything, and a numeric KB year wins ties.
        m = re.search(r"(20\d\d)", have_year)
        have_num = m.group(1) if m else ""
        # OCR records fill gaps only: poster-style OCR is low-confidence and must never
        # replace a text-layer value (김포대 OCR read "TOPIK 3" where the guide lists
        # 2/3/4 for different tracks -- 2026-09-29).
        upgrade = bool(args.upgrade_years and not r.get("_ocr") and not r.get("_vision")
                       and rec_year == CURRENT_YEAR
                       and (not have_num or rec_year > have_num))
        majors = [m for m in (r.get("majors") or []) if m]
        if majors and sec != "lang":
            field = {"ba": "majors", "ma": "majors", "junior": "majors_sample"}.get(sec, "majors")
            if upgrade or not v.get(field):
                if upgrade and v.get(field) and v.get(field) != majors:
                    AUDIT.append({"school": real, "level": sec, "field": field,
                                  "from_year": have_year or "unknown", "to_year": rec_year,
                                  "old": v.get(field), "new": majors})
                v[field] = majors; stats["majors_added"] += 1
                v.setdefault("_llm_parsed", {})[field] = "LLM(pro)"
            elif r.get("_vision") or r.get("_ocr"):
                # An independent modality (vision read of an unreadable guide) found majors the KB
                # does not list. Union — additive only, nothing is ever removed — because a thin KB
                # list is often just one residual entry (한양대 ba had 1 major vs 69 in the guide).
                have = v.get(field) or []
                extra = [m for m in majors if m not in have]
                if extra:
                    v[field] = list(have) + extra
                    stats["majors_unioned"] = stats.get("majors_unioned", 0) + 1
                    v.setdefault("_llm_parsed", {})[field] = "LLM(pro) + vision union"
            # also keep a fuller list for junior
            if sec == "junior" and not v.get("majors_full"):
                v["majors_full"] = majors
                v.setdefault("_llm_parsed", {})["majors_full"] = "LLM(pro)"
        for f, kbk in (("period", "period"), ("topik", "topik_req"), ("ielts", "ielts_req"), ("toefl", "toefl_req")):
            val = r.get(f)
            if sec == "lang" and f != "period":
                continue  # 어학연수는 TOPIK/IELTS/TOEFL 입학요건 아님
            if val not in (None, "", "unknown") and (upgrade or not v.get(kbk)):
                if upgrade and v.get(kbk) and v.get(kbk) != val:
                    AUDIT.append({"school": real, "level": sec, "field": kbk,
                                  "from_year": have_year or "unknown", "to_year": rec_year,
                                  "old": v.get(kbk), "new": val})
                v[kbk] = val; stats["period_filled" if f == "period" else "lang_filled"] += 1
                v.setdefault("_llm_parsed", {})[kbk] = "LLM(pro)"

        # Preserve curated scholarship data; only fill an empty field from the source guide.
        scholarship_rows = [x for x in (r.get("scholarships") or [])
                            if isinstance(x, dict) and x.get("name") and (x.get("condition") or x.get("benefit"))]
        existing_scholarship = any(v.get(k) for k in ("scholarships", "scholarships_categorized",
                                                       "scholarship_curated", "scholarships_verified"))
        if scholarship_rows and not existing_scholarship and sec != "lang":
            v["scholarships_categorized"] = [
                {"name": x.get("name", ""), "condition": x.get("condition", ""),
                 "benefit": x.get("benefit", ""), "type": "enroll", "category": "academic"}
                for x in scholarship_rows
            ]
            v.setdefault("_llm_parsed", {})["scholarships_categorized"] = "LLM(pro; guide _file)"

        # Prose notes were parsed but never merged, so a guide's tuition detail / scholarship
        # sentence was silently dropped. Fill only when the KB has nothing (never overwrite prose).
        PLACEHOLDERS = {"unknown", "none", "n/a", "null", "-", "없음", "미정", "해당없음"}
        for f, kbk in (("tuition_note", "tuition_note"), ("scholarship_note", "scholarship_note")):
            val = r.get(f)
            val = val.strip() if isinstance(val, str) else ""
            # the model writes "unknown" for missing values; never store a placeholder as prose
            if len(val) > 4 and val.lower() not in PLACEHOLDERS and not v.get(kbk):
                v[kbk] = val[:800]
                v.setdefault("_llm_parsed", {})[kbk] = "LLM(pro; guide _file)"
                stats[kbk + "_filled"] = stats.get(kbk + "_filled", 0) + 1

    upgraded = 0
    if args.upgrade_years:
        for sname, (a, b) in sections.items():
            for name, v in (kb[a][b] if b else kb[a]).items():
                toup = [x for x in AUDIT if x["school"] == name]
                if toup:
                    v["guide_year"] = str(toup[0]["to_year"])
                    v["guide_year_source"] = "LLM(pro) 2027 guide parse (year upgrade)"
                    v.setdefault("_llm_parsed", {})["guide_year"] = "LLM(pro; year upgrade)"
                    upgraded += 1
        stats["schools_upgraded"] = upgraded
        os.makedirs(os.path.dirname(AUDIT_PATH), exist_ok=True)
        json.dump({"at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
                   "changes": AUDIT}, open(AUDIT_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        for rec in AUDIT[:6]:
            print(f"  UPGRADE {rec['school']} [{rec['level']}] {rec['field']}: {rec['from_year']} -> {rec['to_year']}")
        print(f"year-upgrade audit -> {AUDIT_PATH}")
    print("stats:", stats)
    print("unmatched schools:", sorted(list(unmatched))[:20])
    if args.write:
        shutil.copy(KB, KB.replace(".json", f"_bak_llmmerge_{datetime.date.today()}.json"))
        json.dump(kb, open(KB, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
        print("저장 완료:", KB)

if __name__ == "__main__":
    main()
