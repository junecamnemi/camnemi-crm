#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fast query tool over the verified knowledge base.
Usage:
  python advisor_query.py --ielts 5.5 [--major data] [--track english] [--year 2027] [--top 10]
  python advisor_query.py --ielts 5.0 --track english
  python advisor_query.py --topik 3 --track korean
"""
import argparse
import json
import re
import os

KB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "verified_kb.json")

# English + USD output helpers (all student-facing output is English, tuition in USD)
from en_output import en_name, en_region, en_major, en_scholarship, en_track, en_lang, fmt_tuition_usd, logo

_KB = None


def _kb():
    global _KB
    if _KB is None:
        with open(KB_PATH, encoding="utf-8") as f:
            _KB = json.load(f)
    return _KB


def guide_ref(school):
    """Return (status, ref_url, note) for a school from the KB guide map."""
    g = (_kb().get("guide") or {}).get(school) or {}
    return g.get("status"), g.get("ref_url", ""), g.get("note", "")


def parse_ielts(lang_req):
    """Return min IELTS from a lang requirement string, or None."""
    m = re.search(r"IELTS\s*(\d+\.?\d*)", str(lang_req))
    return float(m.group(1)) if m else None


def parse_topik(lang_req):
    m = re.search(r"TOPIK\s*(\d+)", str(lang_req))
    return int(m.group(1)) if m else None


def main():
    ap = argparse.ArgumentParser(description="Camnemi verified university query")
    ap.add_argument("--ielts", type=float, help="min IELTS score the student has")
    ap.add_argument("--topik", type=int, help="min TOPIK level the student has")
    ap.add_argument("--major", type=str, help="major keyword (e.g. data, computer, business)")
    ap.add_argument("--track", type=str, choices=["english", "korean", "all"], default="all")
    ap.add_argument("--level", type=str, choices=["ba", "ma", "junior"], default="ba", help="ba=bachelor, ma=master's, junior=2yr college")
    ap.add_argument("--region", type=str, help="region filter (e.g. 서울, 경기, 부산)")
    ap.add_argument("--max_tuition", type=int, help="max tuition per semester (KRW)")
    ap.add_argument("--year", type=str, help="2027 or 2026")
    ap.add_argument("--top", type=int, default=15)
    args = ap.parse_args()

    with open(KB_PATH, encoding="utf-8") as f:
        kb = json.load(f)

    # select section: master, junior, or bachelor
    if args.level == "ma":
        section = kb.get("master", {}).get("schools", {})
        lang_field = "lang_req"
    elif args.level == "junior":
        section = kb.get("junior", {}).get("schools", {})
        lang_field = "lang_req"
    else:
        section = kb.get("schools", {})
        lang_field = "lang_req"

    results = []
    for name, s in section.items():
        # track filter (bachelor only has track field)
        if args.track != "all" and "track" in s:
            want = "영어트랙" if args.track == "english" else "한국어트랙"
            if s["track"] != want:
                continue
        # year filter
        if args.year and s.get("year") and str(s.get("year")) != args.year:
            continue
        # IELTS filter: school min IELTS must be <= student's
        if args.ielts is not None:
            req = s.get("ielts_req") if args.level == "junior" else parse_ielts(s.get(lang_field))
            if req is not None:
                req = float(req) if not isinstance(req, str) else parse_ielts(req)
            if req is not None and req > args.ielts:
                continue
        # TOPIK filter
        if args.topik is not None:
            req = s.get("topik_req") if args.level == "junior" else parse_topik(s.get(lang_field))
            if req is not None:
                req = int(req) if not isinstance(req, str) else parse_topik(req)
            if req is not None and req > args.topik:
                continue
        # region filter (substring match)
        if args.region:
            reg_hay = (s.get("region", "") or "") + (s.get("loc", "") or "")
            if args.region not in reg_hay:
                # also try matching just the short name
                short = {"서울": "서울", "경기": "경기", "인천": "인천", "부산": "부산", "대구": "대구",
                         "대전": "대전", "광주": "광주", "울산": "울산", "강원": "강원", "충북": "충북",
                         "충남": "충남", "전북": "전북", "전남": "전남", "경북": "경북", "경남": "경남", "제주": "제주"}
                if short.get(args.region, args.region) not in reg_hay:
                    continue
        # max tuition (require tuition to be known)
        if args.max_tuition:
            if not s.get("tuition_min"):
                continue
            if s["tuition_min"] > args.max_tuition:
                continue
        # major keyword (match English + Korean aliases)
        if args.major:
            alias = {
                "data": ["data", "데이터", "빅데이터", "통계", "빅데이터경영"],
                "computer": ["computer", "컴퓨터", "소프트웨어", "ai", "인공지능", "ict", "정보"],
                "business": ["business", "경영", "무역", "금융", "경제"],
                "game": ["game", "게임", "디지펜"],
                "engineering": ["engineering", "공학", "전자", "전기", "반도체", "로봇", "시스템"],
                "english": ["english", "영어", "language", "언어"],
                "global": ["global", "글로벌", "international", "국제"],
                "hospitality": ["hospitality", "호텔", "관광", "외식", "항공서비스"],
            }
            keys = alias.get(args.major.lower(), [args.major.lower()])
            hay = ""
            # junior stores majors_sample list; MA stores majors list; BA stores majors string
            major_src = s.get("majors") or s.get("majors_sample") or []
            if isinstance(major_src, list):
                hay = " ".join(str(m) for m in major_src) + " " + str(s.get(lang_field, ""))
            else:
                hay = str(major_src) + " " + str(s.get(lang_field, ""))
            hay = hay.lower()
            if not any(k.lower() in hay for k in keys):
                continue
        results.append(s)

    # sort by rank (parse #N)
    def rank_key(s):
        m = re.match(r"#(\d+)", str(s.get("rank", "-")))
        return (0 if m else 1, int(m.group(1)) if m else 999)

    results.sort(key=rank_key)
    results = results[: args.top]

    if not results:
        print("No universities match your criteria.")
        return

    lv = "Junior college" if args.level == "junior" else ("Master's" if args.level == "ma" else "Bachelor")
    print(f"Criteria: {lv} / IELTS {args.ielts} / TOPIK {args.topik} / track {args.track} / major {args.major} / region {args.region} / max tuition {args.max_tuition} / year {args.year}")
    print(f"→ {len(results)} universities\n")
    for s in results:
        name = s.get('name', '')
        rk = f"Rank {s.get('rank')}" if s.get("rank") not in (None, "-", "") else "Rank -"
        lg = logo(name)
        lgp = f" [{lg}]" if lg else ""
        print(f"■ {en_name(name)}{lgp} ({rk}, {en_region(s.get('region') or s.get('loc',''))})")
        major_src = s.get("majors") or s.get("majors_sample") or []
        if isinstance(major_src, list):
            majors_txt = ", ".join(en_major(str(m)) for m in major_src[:5])
            if len(major_src) > 5:
                majors_txt += f" (+{len(major_src)-5} more)"
        else:
            majors_txt = ", ".join(en_major(m) for m in str(major_src).split("/") if m.strip())[:300]
        print(f"   Majors: {majors_txt}")
        # language display
        if args.level == "junior":
            lang_disp = f"TOPIK {s.get('topik_req')}" if s.get("topik_req") else ""
            if s.get("ielts_req"):
                lang_disp += (f" / IELTS {s['ielts_req']}" if lang_disp else f"IELTS {s['ielts_req']}")
            lang_disp = lang_disp or "No strict requirement"
        else:
            lang_disp = s.get('lang_req', '')
        print(f"   Language: {en_lang(lang_disp)} | Apply: {s.get('period','-')}")
        if args.level == "junior" and s.get("lang_note"):
            print(f"   ⚠️ {en_lang(s['lang_note'])}")
        tu = fmt_tuition_usd(s.get("tuition_semester") or s.get("tuition_min"))
        if not tu:
            tu = "not in our system / please confirm"
        print(f"   Tuition: {tu}/semester")
        # fee structure: app fee(지원비) + admission fee(입학금) + semester tuition
        fs = s.get("fee_structure")
        if fs:
            parts = []
            if fs.get("app_fee"):
                parts.append(f"App fee ₩{fs['app_fee']}")
            af = fs.get("admission_fee")
            if af is not None:
                if str(af) == "0":
                    parts.append("Admission fee waived")
                else:
                    parts.append(f"Admission fee ₩{af}")
            if parts:
                print(f"   💵 {' / '.join(parts)}")
        if s.get("scholarship"):
            print(f"   Scholarship: {en_scholarship(s['scholarship'])}")
        # categorized scholarships: enroll/existing × academic/language (preferred)
        sc = s.get("scholarships_categorized") or []
        en = (s.get("scholarships") or {}).get("enroll") or []
        ex = (s.get("scholarships") or {}).get("existing") or []
        if sc:
            # group by (type, category)
            from collections import defaultdict
            groups = defaultdict(list)
            for x in sc:
                groups[(x.get("type"), x.get("category"))].append(x)
            for (t, cat), items in groups.items():
                label = {
                    ("enroll", "academic"): "[Admission · Academic]",
                    ("enroll", "language"): "[Admission · Language]",
                    ("enroll", "both"): "[Admission · Academic+Lang]",
                    ("enroll", "general"): "[Admission · General]",
                    ("existing", "academic"): "[During-study · Academic]",
                    ("existing", "language"): "[During-study · Language]",
                    ("existing", "both"): "[During-study · Academic+Lang]",
                    ("existing", "general"): "[During-study · General]",
                }.get((t, cat), f"[{t}/{cat}]")
                brief = " / ".join(en_scholarship(x.get("name", "")) for x in items[:2])
                # skip empty briefs (e.g. translated names that lose meaning)
                if brief and brief.strip(" /·"):
                    print(f"   {label} {brief}")
        elif en or ex:
            # fallback: old flat lists (schools without categorized data)
            if en:
                print(f"   [Admission scholarship] {' / '.join(en_scholarship(x) for x in en[:2])}")
            if ex:
                print(f"   [During-study scholarship] {' / '.join(en_scholarship(x) for x in ex[:2])}")
        if s.get("note"):
            print(f"   💡 {en_scholarship(s['note'])}")
        # reference + 2027 status
        if args.level == "junior":
            gref = s.get("guide_url", "")
            if gref:
                print(f"   📄 Reference: official admission page -> {gref}")
            else:
                print(f"   📄 Reference: check school site (guide not in system)")
        else:
            gstatus, gref, gnote = guide_ref(name)
            if gstatus == '2027':
                print(f"   📄 Reference: 2027 admission guide -> {gref}")
            else:
                print(f"   📄 Reference: {gnote} -> {gref}")
        print()


if __name__ == "__main__":
    main()
