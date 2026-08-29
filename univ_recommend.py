#!/usr/bin/env python3
"""
University Advisor — recommend Korean universities by major, IELTS, degree level.

Usage:
    python univ_recommend.py --ielts 5.5 --major "data science" --level ba
    python univ_recommend.py --ielts 5.5 --major "computer" --level ba --top 10
"""
import argparse
import json
import re
import sys
import os

DATA_FILE = r"C:\Users\USER\camnemi-crm\data.js"

# English + USD output helpers (all student-facing output is English, tuition in USD)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend"))
from en_output import en_name, en_region, fmt_usd, krw_to_usd, logo

# --- application deadline lookup (from verified KB) ---------------------------
_KB_PERIOD = None
_KB_FULL = None


def _load_kb():
    global _KB_FULL
    if _KB_FULL is None:
        try:
            p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend", "verified_kb.json")
            with open(p, encoding="utf-8") as f:
                _KB_FULL = json.load(f)
        except Exception:
            _KB_FULL = {}
    return _KB_FULL


def load_kb_periods():
    """Load school -> application period map from the verified KB."""
    global _KB_PERIOD
    if _KB_PERIOD is not None:
        return _KB_PERIOD
    _KB_PERIOD = {}
    try:
        kb = _load_kb()
        for sec_key in ("schools",):
            for name, d in (kb.get(sec_key) or {}).items():
                if d.get("period"):
                    _KB_PERIOD[name] = d["period"]
        # also master's
        for name, d in (kb.get("master", {}).get("schools") or {}).items():
            if d.get("period"):
                _KB_PERIOD.setdefault(name, d["period"])
        # fallback period notes (popular schools not in BA section)
        for name, period in (kb.get("period_notes") or {}).items():
            _KB_PERIOD.setdefault(name, period)
    except Exception:
        pass
    return _KB_PERIOD


def guide_ref(school):
    """Return (status, ref_url, note) from the KB guide map."""
    g = (_load_kb().get("guide") or {}).get(school) or {}
    return g.get("status"), g.get("ref_url", ""), g.get("note", "")

# --- data loading ----------------------------------------------------------
def load_universities():
    with open(DATA_FILE, encoding="utf-8") as f:
        content = f.read()
    start = content.find("[")
    depth = 0
    for i in range(start, len(content)):
        if content[i] == "[":
            depth += 1
        elif content[i] == "]":
            depth -= 1
            if depth == 0:
                return json.loads(content[start:i + 1])
    return []


# --- major matching ---------------------------------------------------------
MAJOR_KEYWORDS = {
    "data science": ["data", "빅데이터", "데이터"],
    "computer": ["computer", "컴퓨터"],
    "software": ["software", "소프트웨어"],
    "ai": ["ai", "artificial intelligence", "인공지능", "intelligence"],
    "business": ["business", "경영"],
    "nursing": ["nursing", "간호"],
    "media": ["media", "미디어", "communication", "커뮤니케이션"],
    "english": ["english", "영어", "영미"],
    "korean": ["korean", "한국어", "국어국문"],
    "engineering": ["engineering", "공학"],
    "economics": ["economics", "경제"],
    "psychology": ["psychology", "심리"],
}


def match_major(univ, major_query, level):
    """Return True if a university has a major matching the query."""
    q = major_query.lower()
    # collect major strings for the level
    major_texts = []
    if level == "ba":
        for mm in univ.get("majors_ba", []) or []:
            major_texts.append(f"{mm.get('kr','')} {mm.get('en','')}".lower())
        # fallback to flat majors list
        if not major_texts:
            major_texts = [str(x).lower() for x in (univ.get("majors") or [])]
    elif level == "ma":
        for mm in univ.get("majors_ma", []) or []:
            major_texts.append(f"{mm.get('kr','')} {mm.get('en','')}".lower())
    else:
        for mm in univ.get("majors_ba", []) or []:
            major_texts.append(f"{mm.get('kr','')} {mm.get('en','')}".lower())
        for mm in univ.get("majors_ma", []) or []:
            major_texts.append(f"{mm.get('kr','')} {mm.get('en','')}".lower())

    combined = " ".join(major_texts)
    # direct keyword match against query tokens
    tokens = re.split(r"[\s,]+", q)
    for tok in tokens:
        if tok and tok in combined:
            return True
    # known keyword families
    for family, kws in MAJOR_KEYWORDS.items():
        if family in q and any(kw in combined for kw in kws):
            return True
    return False


# --- recommendation ----------------------------------------------------------
def recommend(ielts=None, major=None, level="ba", top=15, min_rank=None):
    univs = load_universities()
    results = []

    for u in univs:
        # junior colleges: only when level=junior; universities: not when level=junior
        is_junior = (u.get("type") == "junior")
        if level == "junior":
            if not is_junior:
                continue
        elif is_junior:
            continue

        # major filter
        if major:
            if not match_major(u, major, level):
                continue

        # IELTS filter: university requires IELTS <= user's score
        req = u.get("req") or {}
        u_ielts = req.get("ielts")
        if ielts is not None and u_ielts is not None:
            try:
                if float(u_ielts) > float(ielts):
                    continue
            except ValueError:
                pass  # non-numeric, ignore

        # rank filter
        if min_rank and u.get("rk") and u.get("rk") > min_rank:
            continue

        results.append(u)

    # sort: ranked first, then by tuition min
    def sort_key(u):
        rk = u.get("rk") or 9999
        t = ((u.get("tuition") or {}).get("ba") or {}).get("min") or 999999999
        return (rk, t)

    results.sort(key=sort_key)
    return results[:top]


# --- output ------------------------------------------------------------------
def fmt_result(u, level="ba"):
    req = u.get("req") or {}
    # junior colleges store tuition under 'ba' key
    tu_key = "ba" if level == "junior" else level
    tu = ((u.get("tuition") or {}).get(tu_key) or {})
    tmin = tu.get("min")
    tmax = tu.get("max")
    tstr = ""
    if tmin and tmax:
        tstr = f"{fmt_usd(tmin)}~{fmt_usd(tmax)}"
    elif tmin:
        tstr = f"{fmt_usd(tmin)}"
    parts = []
    lg = logo(u.get("n"))
    if lg:
        parts.append(f"[{lg}]")
    parts.append(f"{en_name(u.get('n'))}")
    if u.get("rk"):
        parts.append(f"[Rank {u['rk']}]")
    if u.get("loc"):
        parts.append(f"({en_region(u['loc'])})")
    line = " ".join(parts)
    extras = []
    if req.get("ielts"):
        extras.append(f"IELTS {req['ielts']}")
    if req.get("topik"):
        extras.append(f"TOPIK {req['topik']}")
    if req.get("selftest"):
        extras.append("own test")
    if extras:
        line += f" — {', '.join(extras)}"
    if tstr:
        line += f" | Tuition {tstr}/semester"
    # application deadline from verified KB
    if level == "junior":
        # junior colleges: no 2027 guide status; show official page if available
        gurl = u.get("degree_guide") or ""
        if gurl:
            line += f" | 📄 Admission page: {gurl}"
        return line
    gstatus, gref, gnote = guide_ref(u.get("n"))
    period = load_kb_periods().get(u.get("n"))
    if gstatus != '2026':
        # 2027 published (or unknown) -> show deadline as-is
        if period:
            line += f" | Apply {period}"
        elif gstatus == '2027':
            line += " | Apply: see 2027 guide"
    else:
        # 2027 not published -> don't show stale 2026 deadline, flag it
        line += " | 2027 guide NOT published yet"
    if gref:
        label = "2027 guide" if gstatus == '2027' else "2026 guide"
        line += f" | 📄 {label}: {gref}"
    return line


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ielts", type=float, help="User's IELTS score")
    ap.add_argument("--major", help="Major query, e.g. 'data science'")
    ap.add_argument("--level", default="ba", choices=["ba", "ma", "lang", "junior"])
    ap.add_argument("--top", type=int, default=15)
    ap.add_argument("--min-rank", type=int, default=None)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    recs = recommend(args.ielts, args.major, args.level, args.top, args.min_rank)
    if args.json:
        print(json.dumps([{
            "name": en_name(u.get("n")), "eng": u.get("en"), "loc": en_region(u.get("loc")),
            "rank": u.get("rk"), "ielts": (u.get("req") or {}).get("ielts"),
            "topik": (u.get("req") or {}).get("topik"),
            "tuition_usd": krw_to_usd(((u.get("tuition") or {}).get(args.level) or {}).get("min")),
            "selftest": (u.get("req") or {}).get("selftest"),
            "logo": logo(u.get("n")),
        } for u in recs], ensure_ascii=False, indent=2))
        return

    if not recs:
        print("No universities found matching your criteria.")
        return
    print(f"Found {len(recs)} universities:\n")
    for i, u in enumerate(recs, 1):
        print(f"{i}. {fmt_result(u, args.level)}")


if __name__ == "__main__":
    main()
