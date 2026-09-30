#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Answer-sheet rows for school questions — the operator's standing 5-column format:

    School | Location | Requirement Language | Tuition fee | Scholarship

Usage:
    python sheet_row.py 가천대학교 건국대학교 인제대학교
    python sheet_row.py --level junior 계원예술대학교
    python sheet_row.py --no-score            # every school with a verified no-score tier

Tuition rule: undergrads only. NEVER quote `tuition_semester_by_dept.fields["어학연수"]`
(a language-course price) as a degree tuition — that produced a false "$800~$1,100/sem"
for 국립금오공과대/광운대. Prefer `tuition_semester`, fall back to
`tuition_per_college_semester` with grad/med keys removed.
"""
import json, re, math, argparse, os

B = os.path.dirname(os.path.abspath(__file__))
KB = json.load(open(os.path.join(B, "verified_kb.json"), encoding="utf-8"))
NO_SCORE = os.path.join(B, "no_language_score_admission_clean.json")

LOC = {"경기도": "Gyeonggi", "서울특별시": "Seoul", "대구광역시": "Daegu", "대전광역시": "Daejeon",
       "부산광역시": "Busan", "충청북도": "Chungbuk", "전라북도": "Jeonbuk", "전북특별자치도": "Jeonbuk",
       "경상남도": "Gyeongnam", "경상북도": "Gyeongbuk", "충청남도": "Chungnam", "광주광역시": "Gwangju",
       "전라남도": "Jeonnam", "강원도": "Gangwon", "인천광역시": "Incheon", "제주특별자치도": "Jeju",
       "경기(안산)": "Gyeonggi"}
SKIP = ("대학원", "학과간", "의학", "약학", "한의", "치의", "수의")


def usd(k):
    return f"${math.ceil(int(k) / 1400 / 100) * 100:,}"


def _nums(x):
    if isinstance(x, (int, float)):
        return [int(x)]
    if isinstance(x, str):
        out = []
        for m in re.findall(r"\d[\d,]{5,}", x):
            try:
                out.append(int(m.replace(",", "")))
            except ValueError:
                pass
        return out
    return []


def tuition(v):
    """Undergrad semester tuition, KRW, as a USD string."""
    vals = _nums(v.get("tuition_semester"))
    ts = v.get("tuition_semester")
    if isinstance(ts, dict):
        vals += _nums(ts.get("min")) + _nums(ts.get("max"))
    if not vals:
        pc = v.get("tuition_per_college_semester")
        if isinstance(pc, dict):
            for k, val in pc.items():
                if any(s in k for s in SKIP):
                    continue
                if isinstance(val, dict):
                    vals += [int(x) for x in val.values() if isinstance(x, (int, float))]
        t = v.get("tuition_semester_by_dept")
        if isinstance(t, dict):
            for k, val in (t.get("fields") or {}).items():
                if "어학" in k or "연수" in k:      # language-course price is NOT tuition
                    continue
                vals += _nums(val)
    vals = [x for x in vals if 500_000 <= x <= 12_000_000]
    if not vals:
        return "확인 필요"
    lo, hi = min(vals), max(vals)
    return usd(lo) if lo == hi else f"{usd(lo)}~{usd(hi)}"


def requirement(v):
    i, t = v.get("ielts_req"), v.get("topik_req")
    if not i and not t:
        return "None"
    return " / ".join(([f"TOPIK {t}"] if t else []) + ([f"IELTS {i}"] if i else []))


def scholarship(v, limit=2):
    """Score-relevant scholarship summary; full fields live in the KB."""
    out = []
    def rec(x):
        if isinstance(x, str):
            if "%" in x or "감면" in x or "면제" in x:
                out.append(re.sub(r"\s+", " ", x).strip())
        elif isinstance(x, dict):
            for k in ("benefit", "amount"):
                if x.get(k):
                    out.append(re.sub(r"\s+", " ", str(x[k])).strip())
            for k, val in x.items():
                if k not in ("name", "benefit", "amount", "level", "type", "category", "score_type"):
                    rec(val)
        elif isinstance(x, list):
            for y in x:
                rec(y)
    for f in ("scholarships_categorized", "scholarships", "scholarship_curated"):
        if v.get(f):
            rec(v[f])
    seen, ded = set(), []
    for s in out:
        k = s[:40]
        if k not in seen:
            seen.add(k)
            ded.append(s)
    return " · ".join(ded[:limit])[:150] if ded else "확인 필요"


def rows(level, names):
    kb = KB if level == "ba" else KB[level]
    src = kb.get("schools", kb)
    for n in names:
        v = src.get(n)
        if not v:
            hit = [k for k in src if n in k]
            if not hit:
                print(f"{n} | NOT IN KB")
                continue
            n, v = hit[0], src[hit[0]]
        print(f"{n}\t{LOC.get(v.get('region') or v.get('loc'), v.get('region') or v.get('loc') or '?')}"
              f"\t{requirement(v)}\t{tuition(v)}\t{scholarship(v)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("names", nargs="*")
    ap.add_argument("--level", default="ba", choices=["ba", "ma", "junior"])
    ap.add_argument("--no-score", action="store_true")
    a = ap.parse_args()
    if a.no_score:
        ns = json.load(open(NO_SCORE, encoding="utf-8"))
        names = [r["school"] for r in ns["schools"]] if a.level == "ba" else [r["school"] for r in ns.get(a.level, [])]
        rows("ba" if a.level == "ba" else a.level, names)
    else:
        rows(a.level, a.names)


if __name__ == "__main__":
    main()