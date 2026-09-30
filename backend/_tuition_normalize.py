#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Normalise tuition rows to TUITION ONLY, with 입학금 labelled "별도" (operator rule 2026-09-30).

Operator instruction: "일단 입학금은 전부 별도 있음으로 표기해. 학과별로 등록금만 있으면 돼."
So every entry gets admission_fee = "별도 (separate)" and every row must carry 수업료 only.

Stripping rules, applied in this order (never guess — if none applies the row is FLAGGED, not altered):
  1. note states a second-semester value ("첫학기 A / 2학기 이후 B") → B is the pure 수업료.
  2. the row is a printed 합계 (= 등록수수료/입학금 + 수업료) and the school's admission fee is known
     from the guide text or the KB → subtract it. Known, verified amounts:
        건국대(글로컬)  등록수수료 187,000  (guide: 디자인대학 187,000 + 6,675,000 = 6,862,000)
        국민대          입학금   1,029,000  (guide: 아시아올림픽 1,029,000 + 6,897,000 = 7,926,000)
     Nothing else is hardcoded: other schools must yield the fee from their own record.
  3. the KB carries an 입학금/전형료 field for that school → subtract it.

Writes tuition_by_department.json in place (backup alongside) and prints the audit.
"""
import os, re, json, shutil, datetime

B = os.path.dirname(os.path.abspath(__file__))
TBD = os.path.join(B, "tuition_by_department.json")
KB = os.path.join(B, "verified_kb.json")

# derived from each guide's own table, not guessed: (fee, evidence)
KNOWN_ADMISSION_FEE = {
    "건국대학교 GLOCAL 캠퍼스": (187_000, "등록수수료(첫 번째 학기) — guide: 187,000+6,675,000=6,862,000"),
    "국민대": (1_029_000, "입학금 — guide: 1,029,000+6,897,000=7,926,000"),
}
SECOND_SEM = re.compile(r"(?:2\s*학기\s*이후|두\s*번째\s*학기|2\s*번째\s*학기|입학학기\s*이후|2학기)[^\d]{0,14}([\d,]{6,})")
SUM_HINT = re.compile(r"합계|첫\s*학기|첫번째\s*학기|등록수수료|입학금")
# the model often records the breakdown in its note: "등록금 4,350,000 + 입학금 800,000 합계"
TUITION_PART = re.compile(r"(?:등록금|수업료)\s*([\d,]{6,})\s*\+\s*입학금")
TUITION_PART2 = re.compile(r"입학금\s*[\d,]{6,}\s*(?:원)?\s*\+\s*(?:수업료|등록금)\s*([\d,]{6,})")
FEE_SEPARATE = re.compile(r"입학금[^)]{0,20}별도")
# "입학금 없음" → the printed value IS the tuition; "수업료1 X / 수업료2 Y 합계" → that is tuition, not a
# total with an admission fee (국제대학교 219,000 + 2,957,000 = 3,176,000, no 입학금 involved).
NO_FEE = re.compile(r"입학금\s*(?:없음|없슴|미징수|0원|해당\s*없|-\s*(?:\+|$))")
TWO_PARTS = re.compile(r"수업료\s*1\s*[\d,]{4,}.*?수업료\s*2\s*[\d,]{4,}\s*합계")
# "첫학기 수업료(입학금 146,000원 포함)" → the fee is inside the printed value, and it is stated
FEE_INCLUDED = re.compile(r"입학금\s*([\d,]{5,})\s*원?\s*(?:포함|별도\s*아님|포함됨)")
# "TOPIK 2급 실납부금(첫학기)" → that is the amount payable AFTER a scholarship, not tuition
NOT_TUITION = re.compile(r"실납부금|고지액|실납부")
PREV_YEAR = re.compile(r"전년도|직전\s*학년도|이전\s*학년도")


def kb_admission_fee(v):
    """입학금/전형료 from the KB record, if present."""
    for key in ("입학금", "admission_fee", "tuition_admission_fee"):
        val = v.get(key)
        if isinstance(val, (int, float)) and 50_000 <= val <= 3_000_000:
            return int(val)
    pc = v.get("tuition_per_college_semester")
    if isinstance(pc, dict):
        for k, val in pc.items():
            if "입학금" in k and isinstance(val, (int, float)) and 50_000 <= val <= 3_000_000:
                return int(val)
    return None


def main():
    tbd = json.load(open(TBD, encoding="utf-8"))
    kb = json.load(open(KB, encoding="utf-8"))
    idx = {}
    for lvl, (sec, key) in (("BA", ("schools", None)), ("MA", ("master", "schools")),
                            ("전문학사", ("junior", "schools"))):
        d = kb[sec]
        d = d.get(key, {}) if key else d
        for n, v in d.items():
            idx[(n, lvl)] = v

    stat = {"entries": 0, "rows": 0, "from_second_semester": 0, "from_note_breakdown": 0,
            "already_separate": 0, "two_parts_tuition": 0, "minus_stated_fee": 0,
            "not_tuition_rows": 0, "prev_year_rows": 0, "minus_known_fee": 0,
            "minus_kb_fee": 0, "flagged_not_stripped": 0}
    flagged = []
    for name, levels in tbd["schools"].items():
        for lvl, e in levels.items():
            if not e.get("rows"):
                continue
            stat["entries"] += 1
            e["admission_fee"] = "별도 (separate)"
            e["fee_basis"] = "tuition_only"
            known = KNOWN_ADMISSION_FEE.get(name)
            kbfee = kb_admission_fee(idx.get((name, lvl), {}))
            for row in e["rows"]:
                stat["rows"] += 1
                note = row.get("note") or ""
                if row.get("krw_incl_admission"):
                    continue  # already stripped in a previous run — never subtract twice
                m = SECOND_SEM.search(note)
                if m:
                    new = int(m.group(1).replace(",", ""))
                    if 300_000 <= new <= 15_000_000 and new != row["krw"]:
                        row["krw_incl_first_semester"] = row["krw"]
                        row["krw"] = new
                        row["basis"] = "2학기 이후(수업료만)"
                        stat["from_second_semester"] += 1
                    continue
                # the note itself may state the tuition component: "등록금 4,350,000 + 입학금 800,000 합계"
                m2 = TUITION_PART.search(note) or TUITION_PART2.search(note)
                if m2:
                    new = int(m2.group(1).replace(",", ""))
                    if 300_000 <= new <= 15_000_000 and new < row["krw"]:
                        row["krw_incl_admission"] = row["krw"]
                        row["krw"] = new
                        row["basis"] = "요강 표기 분해(수업료만) - note에서 추출"
                        stat["from_note_breakdown"] += 1
                        continue
                if FEE_SEPARATE.search(note) or NO_FEE.search(note):
                    row["basis"] = ("요강: 입학금 별도 명시 → 값은 수업료" if FEE_SEPARATE.search(note)
                                    else "요강: 입학금 없음 → 값은 수업료")
                    stat["already_separate"] += 1
                    continue
                if TWO_PARTS.search(note):
                    row["basis"] = "수업료1+수업료2 합계(입학금 별도)"
                    stat["two_parts_tuition"] += 1
                    continue
                m3 = FEE_INCLUDED.search(note)
                if m3:
                    fee = int(m3.group(1).replace(",", ""))
                    if 50_000 <= fee <= 3_000_000 and row["krw"] > fee:
                        row["krw_incl_admission"] = row["krw"]
                        row["krw"] = row["krw"] - fee
                        row["admission_fee"] = "별도 (separate)"
                        row["basis"] = f"요강: 입학금 {fee:,} 포함 → 차감(수업료만)"
                        stat["minus_stated_fee"] += 1
                        continue
                if NOT_TUITION.search(note):
                    row["not_tuition"] = True
                    row["basis"] = "장학금 반영 실납부금 — 등록금 아님(참고용)"
                    stat["not_tuition_rows"] += 1
                    continue
                if PREV_YEAR.search(note):
                    row["basis"] = "전년도 학년도 등록금(요강 표기)"
                    stat["prev_year_rows"] += 1
                    continue
                if re.search(r"수업료", note) and not re.search(r"입학금|등록수수료", note):
                    row["basis"] = "요강 표의 수업료(입학금 별도)"
                    stat["already_separate"] += 1
                    continue
                if SUM_HINT.search(note) or row.get("krw_incl_admission"):
                    fee = known[0] if known else kbfee
                    if fee and row["krw"] > fee:
                        row["krw_incl_admission"] = row["krw"]
                        row["krw"] = row["krw"] - fee
                        row["admission_fee"] = "별도 (separate)"
                        row["basis"] = ("합계 - " + (known[1] if known else "KB 입학금"))
                        stat["minus_known_fee" if known else "minus_kb_fee"] += 1
                    else:
                        row["basis"] = "합계로 보이나 입학금 근거 없음 → 미차감"
                        stat["flagged_not_stripped"] += 1
                        flagged.append((name, lvl, row.get("college"), row.get("krw")))
                else:
                    row.setdefault("basis", "요강 표의 수업료(입학금 별도)")
            ug = sorted({r["krw"] for r in e["rows"] if r.get("level") == "undergrad"})
            if ug:
                e["undergrad_range"] = {"min": ug[0], "max": ug[-1]}
                e["undergrad_usd"] = (f"${-(-ug[0]//1400//100)*100:,}" if ug[0] == ug[-1]
                                      else f"${-(-ug[0]//1400//100)*100:,}~${-(-ug[-1]//1400//100)*100:,}")
    bak = TBD.replace(".json", f"_bak_admission_{datetime.datetime.now():%Y%m%d_%H%M}.json")
    shutil.copy2(TBD, bak)
    json.dump(tbd, open(TBD, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("admission fee set to '별도 (separate)' on", stat["entries"], "entries |", stat["rows"], "rows")
    print(f"  stripped via 2학기 이후 수업료 : {stat['from_second_semester']}")
    print(f"  stripped via note 분해        : {stat['from_note_breakdown']}")
    print(f"  이미 입학금 별도/없음(유지)    : {stat['already_separate']}")
    print(f"  수업료1+2 합계(수업료로 인정)  : {stat['two_parts_tuition']}")
    print(f"  stripped via 요강 명시 입학금  : {stat['minus_stated_fee']}")
    print(f"  실납부금(등록금 아님) 태그    : {stat['not_tuition_rows']}")
    print(f"  전년도 등록금 태그            : {stat['prev_year_rows']}")
    print(f"  stripped via KB 입학금        : {stat['minus_kb_fee']}")
    print(f"  FLAGGED (합계 의심·근거 없음)  : {stat['flagged_not_stripped']}")
    for f in flagged[:15]:
        print("     ", f)
    print("backup:", os.path.basename(bak))
    print("sample:",
          json.dumps(tbd["schools"]["제주한라대학교"]["BA"]["rows"][:2], ensure_ascii=False))


if __name__ == "__main__":
    main()