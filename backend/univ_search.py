#!/usr/bin/env python3
"""
University search engine for the Camnemi Telegram bot.

Searches the 316-university dataset (data.js) by filters:
  location, degree (BA/MA/language), language requirement (TOPIK/IELTS),
  tuition range, major keyword, ranking, school type, English-program.
Returns a ranked, human-readable summary for Telegram.

Usage:
  python univ_search.py --loc 서울 --degree ba --topik 3 --max_tuition 5000000
  python univ_search.py --query "English business program in Seoul under 5M"
"""
import json, re, os, sys, argparse

DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data.js")

REGIONS = {
    "서울": "서울", "경기": "경기", "인천": "인천", "강원": "강원",
    "충북": "충북", "충남": "충남", "대전": "대전", "세종": "세종",
    "전북": "전북", "전남": "전남", "광주": "광주",
    "경북": "경북", "경남": "경남", "대구": "대구", "부산": "부산", "울산": "울산", "제주": "제주",
}
REGION_ALIAS = {
    "서울특별시": "서울", "서울시": "서울", "경기도": "경기", "인천광역시": "인천",
    "강원도": "강원", "강원특별자치도": "강원", "충청북도": "충북", "충청남도": "충남",
    "대전광역시": "대전", "세종특별자치시": "세종", "전라북도": "전북", "전라남도": "전남",
    "광주광역시": "광주", "경상북도": "경북", "경상남도": "경남", "대구광역시": "대구",
    "부산광역시": "부산", "울산광역시": "울산", "제주도": "제주", "제주특별자치도": "제주",
}


def load_universities():
    data = open(DATA_PATH, encoding="utf-8").read()
    start = data.find("[")
    end = data.rfind("];")
    return json.loads(data[start:end + 1])


def normalize_region(loc):
    if not loc:
        return ""
    for k, v in REGION_ALIAS.items():
        if k in loc:
            return v
    for k in REGIONS:
        if k in loc:
            return k
    return ""


def parse_tuition_num(s):
    """Parse '5,000,000', '5M', '500만', '5000000' to int."""
    if not s:
        return None
    s = str(s).strip().replace(",", "").replace(" ", "")
    if not s:
        return None
    m = re.match(r"^(\d+)(만|M|m)?$", s)
    if not m:
        return None
    num = int(m.group(1))
    unit = m.group(2)
    if unit == "만":
        return num * 10000
    if unit in ("M", "m"):
        return num * 1000000
    return num


def major_matches(univ, keyword):
    kw = keyword.strip().lower()
    if not kw:
        return False
    pools = []
    for mp in (univ.get("majors_ba") or []) + (univ.get("majors_ma") or []) + (univ.get("majors") or []):
        if isinstance(mp, dict):
            pools.append((mp.get("kr") or "") + " " + (mp.get("en") or ""))
        elif isinstance(mp, str):
            pools.append(mp)
    blob = " ".join(pools).lower()
    return kw in blob


def search(query=None, loc=None, degree=None, topik=None, ielts=None,
           max_tuition=None, major=None, rank_only=False, english=False,
           univ_type=None, limit=15):
    univs = load_universities()
    results = []

    for u in univs:
        # school type
        ut = u.get("type", "univ")
        if univ_type and ut != univ_type:
            continue

        # location
        if loc:
            want = REGION_ALIAS.get(loc, loc)
            have = normalize_region(u.get("loc", ""))
            if want != have:
                continue

        # degree availability: BA / MA / language school
        if degree == "ba":
            if not (u.get("majors_ba") or u.get("tuition", {}).get("ba", {}).get("min")):
                continue
        elif degree == "ma":
            if not (u.get("majors_ma") or u.get("tuition", {}).get("ma", {}).get("min")):
                continue
        elif degree == "lang":
            # language school presence: tuition.lang or cert.language
            if not (u.get("tuition", {}).get("lang") or u.get("lang_guide") or u.get("language")):
                continue

        # language requirements
        req = u.get("req") or {}
        if topik is not None:
            t = req.get("topik")
            if t is None:
                continue  # no TOPIK requirement info -> can't confirm
            # t could be number or None; filter >= requested
            try:
                if int(t) < topik:
                    continue
            except (TypeError, ValueError):
                continue
        if ielts:
            it = req.get("ielts")
            if not it:
                continue
            try:
                if float(it) < ielts:
                    continue
            except (TypeError, ValueError):
                continue
        if english:
            if not (req.get("english") or req.get("ielts")):
                continue

        # tuition
        if max_tuition is not None:
            if degree == "ma":
                min_t = (u.get("tuition") or {}).get("ma", {}).get("min")
            elif degree == "lang":
                min_t = (u.get("tuition") or {}).get("lang", {}).get("min")
            else:
                min_t = (u.get("tuition") or {}).get("ba", {}).get("min")
            if min_t is None or min_t > max_tuition:
                continue

        # major keyword
        if major and not major_matches(u, major):
            continue

        # ranking
        if rank_only and not u.get("rk"):
            continue

        results.append(u)

    # rank, then sort by rank (rk) if available else students
    def sort_key(u):
        rk = u.get("rk")
        return (0, rk) if rk else (1, -(u.get("stu") or 0))
    results.sort(key=sort_key)

    return results[:limit]


def format_result(u, degree=None):
    """One university -> compact text line for Telegram."""
    lines = []
    name = u.get("n", "")
    en = u.get("en", "")
    head = name
    if en:
        head += f" ({en})"
    rk = u.get("rk")
    if rk:
        head += f" ★{rk}"
    lines.append(head)
    info = []
    if u.get("loc"):
        info.append(u["loc"])
    if u.get("stu"):
        info.append(f"학생 {u['stu']:,}")
    if u.get("type") == "junior":
        info.append("전문대")
    if info:
        lines.append("  " + " · ".join(info))
    # tuition
    t = u.get("tuition") or {}
    if degree == "ma" and t.get("ma", {}).get("min"):
        lines.append(f"  대학원 등록금: ₩{t['ma']['min']:,}~")
    elif degree == "lang" and t.get("lang", {}).get("min"):
        lines.append(f"  어학당 등록금: ₩{t['lang']['min']:,}~")
    elif t.get("ba", {}).get("min"):
        lines.append(f"  학부 등록금: ₩{t['ba']['min']:,}~")
    # language req
    req = u.get("req") or {}
    req_parts = []
    if req.get("topik"):
        req_parts.append(f"TOPIK {req['topik']}")
    if req.get("ielts"):
        req_parts.append(f"IELTS {req['ielts']}")
    if req.get("kiip"):
        req_parts.append("사회통합(KIIP)")
    if req.get("sejong"):
        req_parts.append("세종학당")
    if req.get("selftest"):
        req_parts.append("자체시험")
    if req.get("english"):
        req_parts.append("영어수업")
    if req_parts:
        lines.append("  요건: " + ", ".join(req_parts))
    return "\n".join(lines)


def search_text(query=None, **kw):
    results = search(query=query, **kw)
    # graceful fallback: if too strict (e.g. TOPIK req kills all MA), retry
    # without language requirements but note it.
    if not results:
        relaxed = {k: v for k, v in kw.items() if k not in ("topik", "ielts")}
        results = search(query=query, **relaxed)
        if results:
            out = [f"🔎 TOPIK/IELTS 조건을 빼고 {len(results)}개 대학을 찾았습니다:"]
            for u in results:
                out.append("")
                out.append(format_result(u, degree=kw.get("degree")))
            return "\n".join(out)
    if not results:
        return "😔 조건에 맞는 대학을 찾지 못했습니다. 조건을 바꿔 다시 검색해보세요."
    out = [f"🔎 {len(results)}개 대학을 찾았습니다:"]
    for u in results:
        out.append("")
        out.append(format_result(u, degree=kw.get("degree")))
    return "\n".join(out)


def parse_natural(query):
    """Parse a natural-language query into structured filters (best-effort)."""
    q = query or ""
    kw = {"loc": None, "degree": None, "topik": None, "ielts": None,
          "max_tuition": None, "major": None, "english": False, "univ_type": None}
    # location
    for k in REGIONS:
        if k in q:
            kw["loc"] = k
            break
    # degree
    if any(w in q for w in ["석사", "대학원", "master", "ma"]):
        kw["degree"] = "ma"
    elif any(w in q for w in ["어학", "언어", "한국어학당", "language", "d-4", "D-4"]):
        kw["degree"] = "lang"
    elif any(w in q for w in ["학부", "학사", "학사과정", "undergraduate", "bachelor", "ba"]):
        kw["degree"] = "ba"
    # TOPIK
    m = re.search(r"(?:topik|토픽)\s*(\d)", q, re.I)
    if m:
        kw["topik"] = int(m.group(1))
    # IELTS
    m = re.search(r"(?:ielts|아이엘츠)\s*([\d.]+)", q, re.I)
    if m:
        kw["ielts"] = float(m.group(1))
    # tuition
    m = re.search(r"(?:under|below|이하|~|<)\s*(?:₩|\\|원)?\s*([\d,]+(?:만|M)?)", q, re.I)
    if m:
        kw["max_tuition"] = parse_tuition_num(m.group(1))
    m = re.search(r"([\d,]+(?:만|M))\s*(?:이하|원 이하|~|이내)", q)
    if m and not kw["max_tuition"]:
        kw["max_tuition"] = parse_tuition_num(m.group(1))
    # English program
    if any(w in q for w in ["영어", "english program", "english-taught", "international"]):
        kw["english"] = True
    # junior college
    if any(w in q for w in ["전문대", "전문대학", "junior"]):
        kw["univ_type"] = "junior"
    # major: try to find a major-ish token (Korean word followed by 학과/전공/학)
    m = re.search(r"([\uac00-\ud7a3]{2,10})(?:학과|전공|학부)", q)
    if m:
        kw["major"] = m.group(1) + "학"
    return kw


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--query", help="natural-language query")
    p.add_argument("--loc")
    p.add_argument("--degree", choices=["ba", "ma", "lang"])
    p.add_argument("--topik", type=int)
    p.add_argument("--ielts", type=float)
    p.add_argument("--max_tuition", type=parse_tuition_num)
    p.add_argument("--major")
    p.add_argument("--english", action="store_true")
    p.add_argument("--junior", action="store_true")
    p.add_argument("--limit", type=int, default=15)
    args = p.parse_args()

    if args.query:
        filters = parse_natural(args.query)
        print(f"# Parsed: {filters}")
        print(search_text(args.query, **filters))
    else:
        print(search_text(None, loc=args.loc, degree=args.degree, topik=args.topik,
                          ielts=args.ielts, max_tuition=args.max_tuition, major=args.major,
                          english=args.english, univ_type=("junior" if args.junior else None),
                          limit=args.limit))
