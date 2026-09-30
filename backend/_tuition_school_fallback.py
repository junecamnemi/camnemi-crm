#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""School-level tuition fallback — the shapes tuition_by_dept.py silently dropped.

The operator caught this: 한양대학교 had tuition in the KB and no rows in
tuition_by_department.json. Cause: the builder understood a number or a list of numbers, but the KB
stores three other shapes:
  · {"min": 5279000, "max": 7820000}          (한양대 BA, 학기당)
  · tuition_min / tuition_max as siblings    (한양대 MA 7,257,000 / 11,324,000)
  · "₩3,700,000 (학기당, 전 학과 동일)"        (김포대 전문학사 — a string with the number in it)
A missing row is a wrong answer too: a student sheet showing nothing for a school that publishes
₩3,700,000 reads as "we didn't look".

Rules kept identical to the per-department path:
  · 입학금 stays 별도 — a value that says 입학금 포함 is NOT stripped here (we cannot tell how much of
    it is the fee), it is recorded with `admission_fee_included: true` so the sheet can say so
  · 어학연수 prices are a language course, not 등록금 → never emitted as tuition
  · unit is taken from the KB's own wording (학기/연간); unknown is never converted
  · a range becomes TWO rows (min, max) tagged detail_level=school, so nothing is averaged
  python _tuition_school_fallback.py --dry
  python _tuition_school_fallback.py
"""
import os, re, json, sys, shutil, datetime

B = os.path.dirname(os.path.abspath(__file__))
TBD = os.path.join(B, "tuition_by_department.json")
KB = os.path.join(B, "verified_kb.json")
TODAY = datetime.date.today().isoformat()
NUM = re.compile(r"(\d{1,3}(?:,\d{3}){2,}|\d{7,})")


def to_int(x):
    if isinstance(x, bool):
        return None
    if isinstance(x, (int, float)) and x >= 500_000:
        return int(x)
    if isinstance(x, str):
        m = NUM.search(x)
        if m:
            v = int(m.group(1).replace(",", ""))
            return v if 500_000 <= v <= 30_000_000 else None
    return None


def unit_of(text, level):
    t = text or ""
    if re.search(r"학기", t):
        return "semester"
    if re.search(r"연간|년간|1년", t):
        return "year"
    return "unknown"


# 값의 출처 문장이 '어학연수/한국어과정'이면 등록금이 아니다 — 전북과학대 "950,000원/학기
# (한국어과정 수업료…)" 가 그대로 학비로 들어갔다.
LANG_COURSE = re.compile(r"한국어\s*과정|어학(연수|과정|당)?|language\s*(course|program)", re.I)
# 문서 스스로 "등록금 정보 없음"이라 하는데 값만 있는 경우(성운대: note='등록금 관련 정보 없음'
# 인데 2,641,854~5,283,708 이 있고 상한이 하한의 정확히 2배) → 신뢰 불가
NODATA = re.compile(r"등록금[^.\n]{0,12}(정보|자료|내역)?\s*(없음|미공개|미확인)")


def main():
    kb = json.load(open(KB, encoding="utf-8"))
    secs = {"BA": kb["schools"], "MA": kb["master"]["schools"], "전문학사": kb["junior"]["schools"]}
    doc = json.load(open(TBD, encoding="utf-8"))
    dry = "--dry" in sys.argv
    if not dry:
        shutil.copy(TBD, TBD.replace(".json", f"_bak_schoolfallback_{TODAY}.json"))

    made, per = [], {}
    for level, sec in secs.items():
        for name, v in sec.items():
            lvmap = doc["schools"].get(name)
            if not lvmap:
                continue
            e = lvmap.get(level)
            if not isinstance(e, dict) or e.get("rows"):
                continue
            src, rows = None, []
            ts = v.get("tuition_semester")
            lo, hi = to_int(v.get("tuition_min")), to_int(v.get("tuition_max"))
            # 1) {"min":…, "max":…}
            if isinstance(ts, dict) and ("min" in ts or "max" in ts):
                lo = lo or to_int(ts.get("min"))
                hi = hi or to_int(ts.get("max"))
                src = "tuition_semester{min,max}"
            # 2) siblings tuition_min / tuition_max
            elif lo or hi:
                src = "tuition_min/max"
            # 3) a string carrying the amount
            elif isinstance(ts, str) and to_int(ts):
                lo = hi = to_int(ts)
                src = "tuition_semester(str)"
            if not (lo or hi):
                continue
            # 어학연수-only values are a language course, not 등록금
            bydept = v.get("tuition_semester_by_dept")
            if isinstance(bydept, dict):
                fields = bydept.get("fields") or {}
                if fields and set(fields) <= {"어학연수"} and not (lo and hi):
                    continue
            text = " ".join(str(v.get(k) or "") for k in ("tuition_semester", "tuition_note"))
            if LANG_COURSE.search(text) and not re.search(r"등록금", text):
                continue                       # "한국어과정 수업료"도 제외 (수업료라는 단어로 면제되지 않게)
            if NODATA.search(text):
                continue                       # 스스로 '등록금 정보 없음'이라 하는 기록
            unit = unit_of(text, level)
            incl = bool(re.search(r"입학금[^)]{0,10}포함", text))
            for val, tag in ((lo, "min"), (hi, "max")):
                if not val:
                    continue
                if tag == "max" and val == lo:
                    continue                      # single value → one row
                rows.append({"college": "전체(학교 공표)" if tag != "max" else "전체(학교 공표·최대)",
                             "krw": val, "krw_raw": f"{val:,}", "unit": unit,
                             "detail_level": "school",
                             "basis": f"KB {src} — 학과별 미공개" + ("" if tag != "max" else " (상한)"),
                             "admission_fee_included": incl,
                             "source": "verified_kb.json", "evidence": (text or "")[:160]})
            if not rows:
                continue
            # max == 2×min means the KB pair mixes 학기 and 연간 across departments (창원문성대
            # 3,450,000/6,900,000 · 성운대 2,641,854/5,283,708). Emit the range but say so.
            mix = bool(lo and hi and hi == lo * 2)
            e["rows"] = rows
            e["admission_fee"] = "별도 (separate)"
            e["fee_status"] = "school_level_only"
            e["fee_checked"] = TODAY
            e["fee_detail_level"] = "school"
            e["fee_note"] = ("학교 공표 금액만 있음 — 학과/계열별 표 미공개"
                             + (" · 입학금 포함 표기" if incl else "")
                             + (" · ⚠ 상한이 하한의 2배(학기/연간 단위 혼재 의심) — 확인 필요" if mix else ""))
            if mix:
                e["unit_mix_suspect"] = True
            if lo and lo < 1_500_000:
                e["low_value_suspect"] = True     # 전북과학대 950,000 같은 값 — 확인 필요
            made.append((name, level, [r["krw"] for r in rows]))
            per[level] = per.get(level, 0) + 1

    print(f"filled {len(made)} entries  {per}")
    for n, lv, vals in made:
        print(f"  ✔ {n[:18]:20}[{lv:8}] {', '.join(f'{x:,}' for x in vals)}")
    if not dry:
        json.dump(doc, open(TBD, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    left = {}
    for level in secs:
        left[level] = sum(1 for lvs in doc["schools"].values() for l, e in lvs.items()
                          if l == level and isinstance(e, dict) and not e.get("rows"))
    print("still missing:", left)
    withr = sum(1 for lvs in doc["schools"].values() for e in lvs.values()
                if isinstance(e, dict) and e.get("rows"))
    total = sum(1 for lvs in doc["schools"].values() for e in lvs.values() if isinstance(e, dict))
    print(f"entries with rows: {withr} / {total}")


if __name__ == "__main__":
    main()