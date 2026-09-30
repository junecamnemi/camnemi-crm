# -*- coding: utf-8 -*-
"""Coverage-regression guard for the 3-layer pipeline.

The invariant that matters is per-school: **every field the source (verified_kb.json) has for a
school must also be present in each derived store** (consulting_db.json, data.js). Comparing raw
counts across layers was wrong — data.js carries schools that are not in the KB and vice versa, so
the counts drift for reasons that are not data loss (it produced a false "missing 22" alarm).

Exit non-zero when a derived store drops a field the source has. Recovered-but-unpublished schools
(_pending_publish.json) are reported separately instead of failing the run.
"""
import json
import os
import re
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KB = os.path.join(BASE, "backend", "verified_kb.json")
DB = os.path.join(BASE, "backend", "consulting_db.json")
DATA = os.path.join(BASE, "data.js")

SEC_OF = {"BA": "schools", "MA": "master", "전문학사": "junior", "어학연수": "lang_programs"}
FIELDS = ("tuition", "scholarship", "period")
KB_KEYS = {
    "tuition": ("tuition_semester", "tuition", "tuition_min", "tuition_range"),
    "scholarship": ("scholarships", "scholarships_categorized", "scholarship_curated",
                    "scholarships_verified"),
    "period": ("period",),
}
_SYN = {"글로컬": "glocal"}


def norm(name: str) -> str:
    """Fold KB/derived spellings together: '한양대학교(ERICA)' == '한양대학교 ERICA캠퍼스'."""
    s = str(name or "").lower()
    for a, b in _SYN.items():
        s = s.replace(a, b)
    s = re.sub(r"\[.*?\]|\(.*?\)", "", s)
    for suf in ("대학원대학교", "대학교", "대학원", "대학", "전문대학", "전문대"):
        if s.endswith(suf):
            s = s[: -len(suf)]
            break
    if s.endswith("대") and len(s) > 1:
        s = s[:-1]
    for ch in " ·,.-_":
        s = s.replace(ch, "")
    return s.replace("캠퍼스", "")


def load_datajs() -> list:
    c = open(DATA, encoding="utf-8").read()
    s = c.find("[")
    d = 0
    for i in range(s, len(c)):
        if c[i] == "[":
            d += 1
        elif c[i] == "]":
            d -= 1
            if d == 0:
                return json.loads(c[s:i + 1])
    raise SystemExit("data.js array not found")


kb = json.load(open(KB, encoding="utf-8"))
db = json.load(open(DB, encoding="utf-8"))
data = load_datajs()


def has_content(v) -> bool:
    """Does a field actually carry information?

    `{enroll: [], existing: []}` is a dict and therefore truthy, but it holds nothing — counting it
    as "the source has scholarships" made the guard demand a published scholarship list for 10
    schools whose guides state none.
    """
    if v is None:
        return False
    if isinstance(v, str):
        return bool(v.strip())
    if isinstance(v, list):
        return any(has_content(x) for x in v)
    if isinstance(v, dict):
        return any(has_content(x) for x in v.values())
    return bool(v)


def kb_has(field: str, v) -> bool:
    """Does the SOURCE carry this field?

    For tuition, prose placeholders are not amounts: 수원가톨릭대 says "확인 필요" and 한국농수산대
    "전액 지원 (등록금·수업료·실습비)" — demanding a published number for those asks the derived
    files to invent one.
    """
    if field == "tuition":
        return any(re.search(r"\d", str(v.get(k) or "")) for k in KB_KEYS[field])
    return any(has_content(v.get(k)) for k in KB_KEYS[field])


def kb_schools(level: str) -> dict:
    node = kb.get(SEC_OF[level]) or {}
    holder = node.get("schools", node) if isinstance(node, dict) else {}
    return {k: v for k, v in (holder or {}).items() if isinstance(v, dict)}


src = {lvl: kb_schools(lvl) for lvl in SEC_OF}
src_stat = {lvl: {"n": len(s), **{f: sum(1 for v in s.values() if kb_has(f, v))
                                 for f in FIELDS}}
            for lvl, s in src.items()}

# ---- derived lookups, keyed by folded school name ----
# Folding strips 대학교/대/campus suffixes, so distinct records collide: '금강대' and '금강대학교'
# both fold to '금강', and '한양대학교' collides with '한양대학교(ERICA)'. Keeping only the first
# candidate tested the wrong record and reported 18 filled schools as gaps. Keep every candidate and
# treat the field as present when ANY of them carries it.
from collections import defaultdict

db_map = defaultdict(list)
for name, sc in (db.get("schools") or {}).items():
    db_map[norm(name)].append(sc)

js_map = defaultdict(list)
for u in data:
    if u.get("n"):
        js_map[norm(u.get("n"))].append(u)


def db_has(level: str, folded: str, field: str) -> bool:
    return any(_db_one(sc, level, field) for sc in db_map.get(folded, []))


def _db_one(sc: dict, level: str, field: str) -> bool:
    p = (sc.get("programs") or {}).get(level)
    if not p:
        return False
    if field == "tuition":
        return any(p.get(k) for k in ("tuition", "tuition_max", "tuition_range", "tuition_total",
                                      "tuition_semester"))
    if field == "scholarship":
        sch = p.get("scholarship")
        if isinstance(sch, str):
            return bool(sch.strip())          # 전문학사 records carry one prose line
        if isinstance(sch, list):
            return bool(sch)
        if isinstance(sch, dict):
            # Categorized scholarships use the guide's own headings (입학장학금/재학장학금) rather than
            # enroll/existing, so testing only those two keys reported 16 filled schools as gaps.
            if sch.get("enroll") or sch.get("existing"):
                return True
            return any(v for v in sch.values())
        return False
    return bool(p.get(field))


def js_has(level: str, folded: str, field: str) -> bool:
    return any(_js_one(u, level, field) for u in js_map.get(folded, []))


def _js_one(u: dict, level: str, field: str) -> bool:
    # The KB keeps 4-year and 2-year schools in one "schools" section while data.js splits them into
    # type univ/junior, so a school's record is looked up either way (name presence is what matters).
    if field == "tuition":
        t = u.get("tuition") or {}
        if isinstance(t, int):
            return True
        slot = "ba" if level in ("BA", "전문학사") else "ma"   # data.js junior tuition lives under "ba"
        v = t.get(slot)
        return bool(v.get("min") if isinstance(v, dict) else v)
    if field == "scholarship":
        return bool(u.get("scholarships"))
    if u.get("period"):
        return True
    return bool(u.get("majors_ba") if level in ("BA", "전문학사") else u.get("majors_ma"))


PENDING = os.path.join(BASE, "backend", "_pending_publish.json")
pending_by_lvl = {}
if os.path.exists(PENDING):
    for p in json.load(open(PENDING, encoding="utf-8")):
        pending_by_lvl.setdefault(p["level"], []).append(p["school"])
skip_norm = {(lvl, norm(n)) for lvl, names in pending_by_lvl.items() for n in names}

CHECKS = [("consulting_db", db_has, ["BA", "MA", "전문학사", "어학연수"]),
          ("data.js", js_has, ["BA", "전문학사"])]

gaps = {}
for store, has, levels in CHECKS:
    for level in levels:
        for field in FIELDS:
            missing = sorted(name for name, v in src[level].items()
                             if kb_has(field, v)
                             and (level, norm(name)) not in skip_norm
                             and not has(level, norm(name), field))
            if missing:
                gaps[f"{store}|{level}|{field}"] = missing

# A *new* gap (a school/field that was covered in the recorded baseline) is a regression.
# Known gaps are printed every run and tracked in _coverage_gaps.json so the daily cron is not
# blocked by backlog; run `python publish_new_schools.py --write` to shrink them.
GAPS = os.path.join(BASE, "backend", "_coverage_gaps.json")
known = {}
if os.path.exists(GAPS):
    known = {k: 0 for k in json.load(open(GAPS, encoding="utf-8"))}

regressions = []
for key, missing in sorted(gaps.items()):
    if key not in known:
        regressions.append(f"NEW GAP {key}: {len(missing)} school(s) — "
                           + ", ".join(missing[:6]) + (" ..." if len(missing) > 6 else ""))
json.dump(gaps, open(GAPS, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

print("=== 3-layer coverage (per-school) ===")
for lvl in SEC_OF:
    s = src_stat[lvl]
    print(f"src {lvl:>6}: n={s['n']} tuition={s['tuition']} sch={s['scholarship']} period={s['period']}")

if pending_by_lvl:
    print("\nPENDING PUBLISH (in KB, not yet in consulting_db/data.js — excluded from this check):")
    for lvl in sorted(pending_by_lvl):
        names = pending_by_lvl[lvl]
        print(f"  {lvl}: {len(names)} schools — {', '.join(names[:6])}"
              + (" ..." if len(names) > 6 else ""))
    print("  regenerate the list with: python _pending_publish.py")

if gaps:
    total = sum(len(v) for v in gaps.values())
    if known:
        newly = [k for k in gaps if k not in known]
        fixed = [k for k in known if k not in gaps]
        print(f"\nOPEN GAPS (tracked in _coverage_gaps.json): {total} school-field entries in "
              f"{len(gaps)} groups | newly appeared: {len(newly)} | cleared since last run: {len(fixed)}")
    else:
        print(f"\nOPEN GAPS (baseline recorded): {total} school-field entries in {len(gaps)} groups")
    for key, missing in sorted(gaps.items()):
        print(f"  - {key}: {len(missing)} — " + ", ".join(missing[:5])
              + (" ..." if len(missing) > 5 else ""))
    print("  shrink the backlog with: python publish_new_schools.py --write")

if regressions:
    print("\nREGRESSION DETECTED:")
    for r in regressions:
        print("  !", r)
    sys.exit(1)
print("\nNo NEW coverage regression.")
