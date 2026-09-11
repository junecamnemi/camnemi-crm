#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Camnemi smart recommender — profile -> ranked matches with ELIGIBILITY VERDICT + REASON.

Reads kb_smart.json (structured eligibility + major tags).

Usage:
  python recommend.py --ielts 5.5 --major AI_CS --level ba --top 10
  python recommend.py --topik 3 --level ba --region 서울
  python recommend.py --ielts 5.5 --level lang --region 인천
  python recommend.py --ielts 6.5 --major AI_CS --level ba --max-tuition-usd 3000 --top 15

Verdicts: ELIGIBLE / CONDITIONAL / NOT_ELIGIBLE
  ELIGIBLE     : meets a stated requirement directly (IELTS or TOPIK)
  CONDITIONAL  : can qualify via another accepted path (자체시험/어학원 수료/KIIP/세종학당/TOPIK 취득)
  NOT_ELIGIBLE : no path with the given profile
"""
import json, os, argparse, re

B = r"C:\Users\USER\camnemi-crm\backend"
SMART = os.path.join(B, "kb_smart.json")
KB = os.path.join(B, "verified_kb.json")
RATE = 1400.0

LEVELS = ["ba", "ma", "jun", "lang"]


def load():
    smart = json.load(open(SMART, encoding="utf-8"))
    kb = json.load(open(KB, encoding="utf-8"))
    return smart, kb


def to_usd(v):
    try:
        return round(float(v) / RATE)
    except Exception:
        return None


def tri_to_usd(t):
    if isinstance(t, dict):
        lo, hi = t.get("min"), t.get("max")
        return (to_usd(lo), to_usd(hi)) if lo else (None, None)
    return (to_usd(t), to_usd(t))


def evaluate(elig, ielts, topik):
    """Return (verdict, reason). ielts/topik may be None."""
    e_ielts = (elig.get("ielts") or {}).get("min")
    e_topik = (elig.get("topik") or {}).get("min") or (elig.get("topik") or {}).get("arts_min")
    amb = elig.get("ambiguous")
    caveat = " ⚠️트랙별 요건 상이 — 지원 전공 확인 필요" if amb else ""

    # direct English
    if ielts is not None and e_ielts is not None and ielts >= e_ielts:
        return "ELIGIBLE", f"IELTS {ielts} ≥ {e_ielts} (English/higher-edu path)" + caveat
    # direct TOPIK
    if topik is not None and e_topik is not None and topik >= e_topik:
        return "ELIGIBLE", f"TOPIK {topik}급 ≥ {e_topik}급" + caveat

    # conditional alternatives
    conds = []
    if elig.get("selftest"): conds.append("자체 한국어시험 합격")
    if isinstance(elig.get("lang_school"), dict):
        conds.append(f"어학원 {elig['lang_school'].get('min_level')}급 수료")
    if elig.get("kiip") is not None: conds.append("KIIP/사회통합프로그램 3단계")
    if elig.get("sejong"): conds.append(f"세종학당 {elig['sejong']}")
    if elig.get("interview_eval"): conds.append("면접 구술평가")
    if e_topik is not None: conds.append(f"TOPIK {e_topik}급 취득")
    if e_ielts is not None: conds.append(f"IELTS {e_ielts} 취득")

    if conds:
        # if the gap is small (e.g. needs TOPIK only) mark CONDITIONAL
        return "CONDITIONAL", " 또는 ".join(dict.fromkeys(conds))
    return "NOT_ELIGIBLE", "제시 프로필로 충족 경로 없음"


def fit_score(rec, ielts, topik, major_tags, region):
    """Higher = better fit. rank(낮을수록 좋음) + tuition + region bonus."""
    score = 0.0
    rank = rec.get("rank")
    if isinstance(rank, (int, float)):
        score += max(0, 60 - rank) * 1.5
    else:
        score += 10
    # region match
    if region and rec.get("region") and region in str(rec["region"]):
        score += 20
    # major match
    if major_tags:
        hit = set(major_tags) & set(rec.get("major_tags", []))
        score += len(hit) * 15
    # tuition (cheaper better)
    lo = rec.get("tuition_usd_min")
    if isinstance(lo, (int, float)):
        score += max(0, (4 - lo / 1000.0)) * 5
    return round(score, 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ielts", type=float, default=None)
    ap.add_argument("--topik", type=int, default=None)
    ap.add_argument("--level", choices=LEVELS, default="ba")
    ap.add_argument("--major", action="append", default=[], help="canonical tag e.g. AI_CS, 경영")
    ap.add_argument("--region", default=None)
    ap.add_argument("--max-tuition-usd", type=int, default=None)
    ap.add_argument("--top", type=int, default=15)
    ap.add_argument("--include-conditional", action="store_true", default=True)
    args = ap.parse_args()

    smart, kb = load()
    lvl = args.level.upper() if args.level != "jun" else "jun"
    rows = []
    for school, lv in smart["schools"].items():
        rec = lv.get(lvl)
        if not rec:
            continue
        elig = rec.get("eligibility", {})
        region = rec.get("region")
        if args.region and region and args.region not in str(region):
            continue
        if args.major and not (set(args.major) & set(rec.get("major_tags", []))):
            continue
        verdict, reason = evaluate_for_level(lvl, elig, args.ielts, args.topik, rec)
        if verdict == "NOT_ELIGIBLE":
            continue
        # tuition
        if lvl == "lang":
            tmin, tmax = tri_to_usd(rec.get("tuition"))
        else:
            tmin, tmax = tri_to_usd(rec.get("tuition_semester") if lvl in ("BA", "jun") else
                                    {"min": rec.get("tuition_min"), "max": rec.get("tuition_max")})
        if args.max_tuition_usd and isinstance(tmin, (int, float)) and tmin > args.max_tuition_usd:
            continue
        rec2 = dict(rec); rec2["tuition_usd_min"], rec2["tuition_usd_max"] = tmin, tmax
        score = fit_score(rec2, args.ielts, args.topik, args.major, args.region)
        rows.append({"school": school, "level": lvl, "verdict": verdict, "reason": reason,
                     "score": score, "region": region, "rank": rec.get("rank"),
                     "tuition_usd": (tmin, tmax), "period": rec.get("period"),
                     "major_tags": rec.get("major_tags", [])})

    rows.sort(key=lambda r: (0 if r["verdict"] == "ELIGIBLE" else 1, -r["score"]))
    rows = rows[: args.top]

    print(f"Criteria: level={args.level} IELTS={args.ielts} TOPIK={args.topik} "
          f"major={args.major or 'any'} region={args.region or 'any'} "
          f"max_tuition=${args.max_tuition_usd or 'any'}")
    print(f"→ {len(rows)} matches\n")
    for i, r in enumerate(rows, 1):
        icon = {"ELIGIBLE": "✅", "CONDITIONAL": "⚠️", "NOT_ELIGIBLE": "❌"}[r["verdict"]]
        tu = ""
        if r["tuition_usd"][0]:
            tu = f"${r['tuition_usd'][0]}" + (f"~${r['tuition_usd'][1]}" if r["tuition_usd"][1] != r["tuition_usd"][0] else "") + "/sem"
        rk = f"#{r['rank']}" if isinstance(r["rank"], (int, float)) else "-"
        print(f"{i}. {icon} {r['school']} ({rk}, {r['region'] or '-'})  [score {r['score']}]")
        print(f"   {r['verdict']}: {r['reason']}")
        if r["major_tags"]:
            print(f"   tags: {', '.join(r['major_tags'])}")
        if tu:
            print(f"   Tuition: {tu}")


def evaluate_for_level(lvl, elig, ielts, topik, rec):
    """Level-aware verdict. lang level: only D-4 eligibility matters."""
    if lvl == "lang":
        d4 = rec.get("d4_eligible")
        if d4 is True:
            return "ELIGIBLE", "D-4 어학연수 가능"
        if d4 is None:
            return "CONDITIONAL", "D-4 여부 미확인"
        return "NOT_ELIGIBLE", "D-4 불가"
    return evaluate(elig, ielts, topik)


if __name__ == "__main__":
    main()
