#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build backend/tuition_by_department.json — per-college/department tuition (학과·계열별 등록금).

Sources inside verified_kb.json, in priority order:
  1. tuition_per_college_semester  — 계열/대학별 표 (수업료1+수업료2 = 합계), most reliable
  2. tuition_semester_by_dept      — data.js 역방향 동기화 (fields), often only holds 어학연수 → filtered out
  3. tuition_semester              — summary one-liner (kept as `summary`)

Never emits a language-course price (어학연수/연수 keys) as tuition, and never a grad row without
marking level="grad".  Run:  python tuition_by_dept.py --build   (from backend/)
"""
import json, re, math, os, sys, datetime

B = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(B, "tuition_by_department.json")
GRAD_K = ("대학원", "석사", "박사", "학과간", "협동과정")
LANG_K = ("어학", "연수", "한국어교육원", "어학당")


def usd(k):
    return math.ceil(int(k) / 1400 / 100) * 100


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


def _level(name, has_colleges):
    """grad vs undergrad vs grad-or-summary row.

    '계열/…계' rows on a school that ALSO lists colleges are the graduate/summary table
    (가천대 공학계열 6,674,000 · 광운대 공학계 7,090,000 · 전북대 인문사회(전주) 3,140,000),
    so they must not widen the undergrad range. '(미분류)' is never trusted.
    """
    if any(s in name for s in GRAD_K):
        return "grad"
    if name.strip() in ("(미분류)", "미분류"):
        return "unknown"
    if has_colleges and (name.rstrip().endswith(("계", "계열")) or "계열" in name):
        return "grad_or_summary"
    return "undergrad"


def rows_for(v):
    rows, src = [], None
    pc = v.get("tuition_per_college_semester")
    if isinstance(pc, dict):
        has_colleges = any(("대학" in k or "학부" in k or "캠퍼스" in k) for k in pc)
        for k, val in pc.items():
            if any(s in k for s in LANG_K):
                continue
            if isinstance(val, dict):
                tot = val.get("합계") or val.get("수업료합계")
                if not isinstance(tot, (int, float)):
                    tot = sum(x for x in val.values() if isinstance(x, (int, float))) or None
                if isinstance(tot, (int, float)) and tot >= 300_000:
                    rows.append({"college": k, "krw": int(tot), "level": _level(k, has_colleges),
                                 "parts": {kk: vv for kk, vv in val.items() if isinstance(vv, (int, float))} or None})
            elif isinstance(val, (int, float)) and val >= 300_000:
                rows.append({"college": k, "krw": int(val), "level": _level(k, has_colleges), "parts": None})
        if rows:
            src = "tuition_per_college_semester"
    if not rows:
        t = v.get("tuition_semester_by_dept")
        if isinstance(t, dict):
            for k, val in (t.get("fields") or {}).items():
                if any(s in k for s in LANG_K):
                    continue
                for n in _nums(val):
                    if n >= 300_000:
                        rows.append({"college": k, "krw": n, "level": _level(k, True), "parts": None})
            if rows:
                src = "tuition_semester_by_dept"
    for r in rows:
        r["usd"] = usd(r["krw"])
    return rows, src


def build():
    kb = json.load(open(os.path.join(B, "verified_kb.json"), encoding="utf-8"))
    out = {"meta": {"built": datetime.date.today().isoformat(), "unit": "KRW per semester",
                    "usd_rate": 1400, "usd_rounding": "up to nearest $100",
                    "note": "과별 학비 = college/department level. level='grad' rows excluded from undergrad sheets.",
                    "levels": ["BA", "MA", "전문학사"]}, "schools": {}}
    stats = {"BA": 0, "MA": 0, "전문학사": 0, "no_rows": 0}
    conflicts = []
    for lvl, (sec, key) in (("BA", ("schools", None)), ("MA", ("master", "schools")), ("전문학사", ("junior", "schools"))):
        d = kb[sec]
        d = d.get(key, {}) if key else d
        for name, v in d.items():
            if v.get("excluded") or v.get("recommend_exclude"):
                continue
            rows, src = rows_for(v)
            ug = sorted({r["krw"] for r in rows if r["level"] == "undergrad"})
            # conflict check: does the summary one-liner agree with the college table?
            summ = _nums(v.get("tuition_semester"))
            summ = [x for x in summ if 500_000 <= x <= 12_000_000]
            conflict = bool(ug and summ and (max(ug) < min(summ) * 0.9 or min(ug) > max(summ) * 1.1))
            if conflict:
                conflicts.append({"school": name, "level": lvl, "college_table": f"{ug[0]}~{ug[-1]}",
                                  "summary": v.get("tuition_semester")})
            entry = {"level": lvl, "source": src, "summary": v.get("tuition_semester"),
                     "tuition_note": v.get("tuition_note"), "rows": rows,
                     "conflict": conflict,
                     "undergrad_range": {"min": ug[0], "max": ug[-1]} if ug else None,
                     "undergrad_usd": (f"${usd(ug[0]):,}" if len(set(ug)) <= 1 else f"${usd(ug[0]):,}~${usd(ug[-1]):,}") if ug else None}
            out["schools"].setdefault(name, {})[lvl] = entry
            if not rows:
                stats["no_rows"] += 1
            else:
                stats[lvl] += 1
    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump({"built": out["meta"]["built"], "count": len(conflicts), "conflicts": conflicts},
              open(os.path.join(B, "_tuition_conflicts.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("WROTE", OUT)
    print("schools with per-college rows:", stats,
          "| total school-level entries:", sum(len(v) for v in out["schools"].values()))
    print("conflicts (college table vs summary one-liner):", len(conflicts))
    return out


def show(name, level="BA"):
    d = json.load(open(OUT, encoding="utf-8"))["schools"]
    hit = d.get(name) or next((d[k] for k in d if name in k), None)
    if not hit:
        print("NOT IN DB:", name); return
    key = hit.get(level) or list(hit.values())[0]
    print(f"# {name} [{key['level']}] src={key['source']} | undergrad: {key['undergrad_usd']}")
    for r in key["rows"]:
        tag = " (grad)" if r["level"] == "grad" else ""
        print(f"  {r['college']}{tag}: ₩{r['krw']:,} → ${r['usd']:,}/sem")


if __name__ == "__main__":
    if "--build" in sys.argv:
        build()
    else:
        args = [a for a in sys.argv[1:]]
        lvl = "BA"
        if "--level" in args:
            i = args.index("--level"); lvl = args[i + 1].upper(); del args[i:i + 2]
        for n in args:
            show(n, lvl)
            print()