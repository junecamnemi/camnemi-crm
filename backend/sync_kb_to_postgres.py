"""Load verified_kb.json + curated lists into the `cat` schema (Phase 1).

Usage:
  uv run --with "psycopg[binary]" python sync_kb_to_postgres.py            # dry-run: report only
  uv run --with "psycopg[binary]" python sync_kb_to_postgres.py --write    # commit to Postgres

Design notes
- Idempotent: re-running upserts the same natural keys (school.id, program (school,level,year)).
- Never invents values: fields missing in the KB stay NULL.
- lang programs must not carry topik/ielts/toefl requirements (cat.program CHECK enforces it);
  the loader passes None for lang unconditionally.
- is_current = the newest guide_year present for that (school, level).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import re
import sys
import unicodedata
from collections import Counter, defaultdict

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from pg_conn import connect  # noqa: E402

BACKEND = pathlib.Path(__file__).parent
KB_PATH = BACKEND / "verified_kb.json"
CANON_PATH = BACKEND / "canonical" / "schools.jsonl"
ASSUMED_YEAR = 2026


# ---------------------------------------------------------------- helpers
def _md5_text(s: str) -> str:
    return hashlib.md5(s.encode("utf-8", "ignore")).hexdigest()


def slug(name: str) -> str:
    """Stable ascii-ish id from a Korean school name (readable + unique)."""
    base = unicodedata.normalize("NFKC", name).strip()
    ascii_part = re.sub(r"[^A-Za-z0-9]+", "-", base).strip("-").lower()
    h = hashlib.md5(base.encode("utf-8")).hexdigest()[:6]
    return (ascii_part + "-" if ascii_part else "") + h


def as_list(v) -> list:
    if v is None:
        return []
    if isinstance(v, list):
        return v
    if isinstance(v, dict):
        return list(v.values())
    return [v]


def num(v):
    if v is None or isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return v
    s = re.sub(r"[^0-9.]", "", str(v))
    try:
        return float(s) if "." in s else int(s)
    except ValueError:
        return None


def int_year(*vals):
    for v in vals:
        n = num(v)
        if n and 1990 <= int(n) <= 2100:
            return int(n)
    return None


DATE_RANGE = re.compile(
    r"(20\d{2})[.\-/]\s*(\d{1,2})[.\-/]\s*(\d{1,2})\s*(?:~|-|–|—|부터)\s*(20\d{2})?[.\-/]?\s*(\d{1,2})[.\-/]\s*(\d{1,2})"
)


def date_ranges(text: str) -> list[tuple[str, str]]:
    """Conservative: only unambiguous YYYY.MM.DD ~ YYYY.MM.DD pairs."""
    out = []
    for m in DATE_RANGE.finditer(text or ""):
        y1, m1, d1, y2, m2, d2 = m.groups()
        y2 = y2 or y1
        out.append((f"{y1}-{int(m1):02d}-{int(d1):02d}", f"{y2}-{int(m2):02d}-{int(d2):02d}"))
    return out


def file_md5(path: str):
    p = pathlib.Path(path)
    if not p.is_file():
        return None, None
    h = hashlib.md5()
    size = 0
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
            size += len(chunk)
    return h.hexdigest(), size


def year_from_name(path: str):
    m = re.search(r"(20\d{2})", pathlib.Path(path).name if path else "")
    return int(m.group(1)) if m else None


def resolve_years(entry: dict, path: str, fallback: int):
    """label_year = the physical file's year; effective_year = the cycle the KB uses it for.

    Camnemi deliberately carries an older guide forward when the new one is unpublished and records
    that in `guide_effective_note` ('2027 모집요강 미공개 — 2026 요강 기준 정보'). That is not an
    error, so it is flagged `carried_forward` instead of being clamped. Anything else that disagrees
    wildly is reported and the file's own year is kept.
    """
    label = year_from_name(path) or int_year(entry.get("guide_year")) or fallback
    eff = int_year(entry.get("guide_effective_year")) or int_year(entry.get("guide_year")) or fallback
    note = str(entry.get("guide_effective_note") or "")
    carried = bool(note) and ("미공개" in note or "기준 정보" in note) and eff > label
    if eff == label or (label - 1 <= eff <= label + 2) or (carried and eff - label <= 8):
        return label, eff, carried
    conflicts.append(dict(path=path, label_year=label, kb_effective_year=eff,
                          used_effective_year=label, kb_guide_year=int_year(entry.get("guide_year"))))
    return label, label, False


conflicts: list = []
carried_forward: list = []
unparsed_money: list = []
unparsed_rows: list = []


MONEY_NUM = re.compile(r"\d[\d,]{3,}")
PROSE_RANGE = re.compile(r"^[^\d]*(\d[\d,]{3,})\s*[~\-–]\s*[^\d]*(\d[\d,]{3,})[^\d]*$")
MAX_SANE_KRW = 20_000_000


def money_strict(v):
    """Money only when it is unambiguous — never glue several prose amounts into one number.

    Returns (min, max) or (None, None). A clean "X~Y" range yields both; a single clean number
    yields (X, None). Prose with several different amounts (e.g. '연평균 ₩8,590,000/년 → 약
    ₩4,295,000/학기') yields nothing, and the raw text is kept in tuition_note instead.
    """
    if v is None or isinstance(v, bool):
        return None, None
    if isinstance(v, (int, float)):
        x = int(v)
        return (x, None) if 0 < x <= MAX_SANE_KRW else (None, None)
    s = str(v).strip()
    toks = MONEY_NUM.findall(s)
    if not toks:
        return None, None
    nums = [int(t.replace(",", "")) for t in toks]
    if any(n > MAX_SANE_KRW for n in nums):
        return None, None
    m = PROSE_RANGE.match(s)
    if m:
        lo, hi = sorted((int(m.group(1).replace(",", "")), int(m.group(2).replace(",", ""))))
        return lo, hi
    if len(nums) == 1 and not re.search(r"/\s*(년|year)", s):
        return nums[0], None
    return None, None


def is_prose_money(v) -> bool:
    return isinstance(v, str) and bool(re.search(r"[가-힣A-Za-z]", v)) and bool(MONEY_NUM.search(v))


def score_strict(v, kind: str):
    """Requirement scores only when unambiguous — '3급 또는 4급' must not become 34."""
    limits = {"topik": (0, 6), "ielts": (0, 9), "toefl": (0, 120), "gpa": (0, 4.5)}
    lo, hi = limits[kind]
    if v is None or isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return v if lo <= v <= hi else None
    toks = re.findall(r"\d+(?:\.\d+)?", str(v))
    if len(toks) != 1:
        return None
    x = float(toks[0])
    return int(x) if kind != "ielts" and x == int(x) else x if lo <= x <= hi else None


SCORE_KW = {"topik": ("topik", "급", "한국어"), "ielts": ("ielts",), "toefl": ("toefl", "ibt")}
# Plausibility floors: no university requires IELTS 3.0 or TOEFL 3. Anything below is a parsing
# artifact, so it is rejected (None) and logged rather than published as a requirement.
SCORE_CEIL = {"topik": 6, "ielts": 9, "toefl": 120}
SCORE_FLOOR = {"ielts": 4.0, "toefl": 20}
inferred_scores: list = []
implausible_scores: list = []


def _nums_for(seg: str, kind: str) -> list[float]:
    """Numbers that are actually attached to the test keyword (never list markers like '(2)')."""
    if kind == "topik":
        pats = [r"topik[^0-9]{0,8}(\d+(?:\.\d+)?)", r"(\d+(?:\.\d+)?)\s*급"]
    elif kind == "ielts":
        pats = [r"ielts[^0-9]{0,10}(\d+(?:\.\d+)?)"]
    else:
        # 'TOPIK(IBT) 3급' is a Korean test, not TOEFL: drop that spelling before looking for iBT
        seg = re.sub(r"topik\s*\(?\s*ibt\s*\)?", " ", seg, flags=re.I)
        pats = [r"toefl[^0-9]{0,10}(\d+(?:\.\d+)?)", r"ibt[^0-9]{0,8}(\d+(?:\.\d+)?)"]
    out = []
    for p in pats:
        out += [float(m) for m in re.findall(p, seg, flags=re.I)]
    return out


def toefl_from_text(text: str):
    """-> (value, scale) for the smallest TOEFL-family score in `text`, with its own scale.

    Handles 'TOEFL 530 (CBT 197, iBT 71)', 'TOEFL iBT 80', 'New TEPS 290', and the 2026 iBT 1-6
    scale. TEPS is a different test and is ignored. Returns (None, None) when the text states no
    TOEFL score, so an unverifiable number is never published.
    """
    # 'TOPIK iBT' is a Korean test, not TOEFL; TEPS is a different test entirely.
    text = re.sub(r"topik\s*\(?\s*ibt\s*\)?", " ", text or "", flags=re.I)
    best = None
    # Scale-specific keywords first: in 'TOEFL 530 (CBT 197, iBT 71)' a generic 'toefl' match would
    # swallow the following 'CBT' and lose the real 197.
    for pattern, scale in ((r"cbt[^0-9]{0,12}(\d+(?:\.\d+)?)", "cbt"),
                           (r"pbt[^0-9]{0,12}(\d+(?:\.\d+)?)", "pbt"),
                           (r"ibt[^0-9]{0,12}(\d+(?:\.\d+)?)", "ibt")):
        for m in re.finditer(pattern, text, re.I):
            num = float(m.group(1))
            if best is None or num < best[0]:
                best = (num, scale)
    for m in re.finditer(r"toefl[^0-9]{0,12}(\d+(?:\.\d+)?)", text, re.I):
        num = float(m.group(1))
        if best is not None and num >= best[0]:
            continue
        if num <= 6:
            best = (num, "new_2026")                  # 2026 iBT 1-6 scale
        elif num <= 120:
            best = (num, "ibt")
        # >120 with no scale keyword: unusable, skip
    if best is None:
        return None, None
    value, scale = best
    if scale == "ibt" and value <= 6:
        scale = "new_2026"            # 'iBT 4.0(기존 80점)' is the 2026 1-6 scale, not a 4-point iBT
    return (int(value) if value == int(value) else value), scale


def score_lower_bound(v, kind: str):
    """Take the *minimum* of the clause that actually talks about this test.

    The KB often writes prose such as
      '한국어트랙 TOPIK 3~4 (상위권 TOPIK 4~5) / 영어트랙 IELTS 5.5~6.5'
    A single numeric column cannot hold that, so we store the Korean-track lower bound (3) and
    keep the whole sentence in lang_req_text. Nothing is invented: the raw text stays next to it.
    """
    direct = score_strict(v, kind) if not isinstance(v, str) or \
        re.fullmatch(r"\s*\d+(?:\.\d+)?\s*", v) else None
    if direct is not None:
        # A bare number still has to be possible: TOPIK grades are 1-6, IELTS 4.0-9, TOEFL iBT
        # 20-120. Without the upper bound a year (2026) or an attachment number (붙임9) published as
        # a TOPIK requirement — 한국교통대 ma got 2026, 한밭대 ma got 9, both from a guide that
        # explicitly states no requirement.
        floor = SCORE_FLOOR.get(kind)
        ceil = SCORE_CEIL.get(kind)
        if (floor is not None and direct < floor) or (ceil is not None and direct > ceil):
            implausible_scores.append(dict(kind=kind, value=direct, floor=floor, ceil=ceil,
                                           from_text=str(v)[:200]))
            return None
        if kind == "topik" and float(direct) != int(direct):
            return None
        return direct
    if not isinstance(v, str):
        return None
    parts = re.split(r"[/|·]| 또는 | 혹은 ", v)
    kws = SCORE_KW[kind]
    cand = [p for p in parts if any(k in p.lower() for k in kws)]
    if not cand:
        cand = parts if len(parts) == 1 else []
    nums = []
    for p in cand:
        for x in _nums_for(p, kind):
            lo, hi = {"topik": (0, 6), "ielts": (0, 9), "toefl": (0, 120)}[kind]
            if lo <= x <= hi:
                nums.append(x)
    if not nums:
        return None
    lo = min(nums)
    floor = SCORE_FLOOR.get(kind)
    if floor is not None and lo < floor:
        implausible_scores.append(dict(kind=kind, value=lo, floor=floor, from_text=str(v)[:200]))
        return None
    val = int(lo) if kind != "ielts" and lo == int(lo) else lo
    inferred_scores.append(dict(kind=kind, value=val, from_text=str(v)[:200]))
    return val


def as_bool(v):
    """Strict boolean; prose (e.g. '기숙사 제공, 약 1,180,000원/3개월') becomes None, never truthy."""
    if isinstance(v, bool):
        return v
    if v is None:
        return None
    s = str(v).strip().lower()
    if s in ("true", "yes", "y", "가능", "있음", "o"):
        return True
    if s in ("false", "no", "n", "불가", "없음", "x"):
        return False
    return None


def canonical_ids() -> dict:
    """name_kr -> (id, name_en, aliases, region, type) from canonical/schools.jsonl."""
    out = {}
    if not CANON_PATH.exists():
        return out
    for line in CANON_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            continue
        nm = r.get("name_kr") or r.get("name")
        if not nm:
            continue
        aliases = r.get("aliases") or r.get("alias") or []
        if isinstance(aliases, str):
            aliases = [aliases]
        out[nm] = (r.get("id") or slug(nm), r.get("name_en"), list(aliases),
                   r.get("region"), r.get("type") or r.get("category"))
    return out


# ---------------------------------------------------------------- extraction per level
def program_fields(entry: dict, level: str) -> dict:
    tmin_a, tmax_a = money_strict(entry.get("tuition_min"))
    tmin_b, tmax_b = money_strict(entry.get("tuition_max"))
    tmin_c, tmax_c = money_strict(entry.get("tuition_semester"))
    tmin_d, tmax_d = money_strict(entry.get("tuition_range"))
    tmin = tmin_a if tmin_a is not None else (tmin_c if tmin_c is not None else tmin_d)
    tmax = tmax_b if tmax_b is not None else (tmax_c if tmax_c is not None else tmax_d)
    if tmax is None:
        tmax = tmin
    if tmin is not None and tmax is not None and tmax < tmin:
        tmin, tmax = tmax, tmin
    prose = entry.get("tuition_semester") if is_prose_money(entry.get("tuition_semester")) else None
    if prose:
        unparsed_money.append(dict(level=level, field="tuition_semester", text=str(prose)[:220]))
    f = dict(
        period_text=entry.get("period"),
        tuition_min=tmin, tuition_max=tmax,
        tuition_note=prose or entry.get("tuition_note"),
        apply_system=entry.get("apply_system"),
        apply_system_all=entry.get("apply_system_all"),
        ieqas_certified=as_bool(entry.get("ieqas_certified")),
        ieqas_level=entry.get("ieqas_level"),
        ieqas_course=entry.get("ieqas_course"),
        ieqas_year=int_year(entry.get("ieqas_year")),
        student_count=num(entry.get("student_count")),
        foreign_students=num(entry.get("foreign_students")),
        # every column the INSERT references must exist for every level (None = unknown)
        note=None,
        scholarship_note=None,
        toefl_scale=None,
        req_verified=None,
        lang_per_term=None, lang_total_hours=None, lang_dorm=None, lang_d4_eligible=None,
    )
    if level == "lang":
        f.update(topik_req=None, ielts_req=None, toefl_req=None, lang_req_text=None,
                 lang_per_term=(entry.get("structure") or {}).get("per_term"),
                 lang_total_hours=(entry.get("structure") or {}).get("total_hours"),
                 lang_dorm=as_bool(entry.get("dorm")), lang_d4_eligible=as_bool(entry.get("d4_eligible")))
        f["tuition_note"] = f["tuition_note"] or entry.get("tuition_note")
        f["note"] = entry.get("note")
    else:
        def prose_score(val, kind):
            """Only prose may be mined for a *different* test.

            `topik_req` is often a bare int (3 = TOPIK 3급). Feeding that int to the IELTS/TOEFL
            parser produced 119 bogus 'IELTS 3.0' and 209 'TOEFL 3' requirements.
            """
            return score_lower_bound(val, kind) if isinstance(val, str) else None

        def first_prose(*vals, kind):
            for val in vals:
                got = prose_score(val, kind)
                if got is not None:
                    return got
            return None

        ielts = score_lower_bound(entry.get("ielts_req"), "ielts")
        if ielts is None:
            ielts = first_prose(entry.get("topik_req"), entry.get("lang_req"), kind="ielts")
        # Is the published number actually stated in the guide? 경민대 junior carried ielts 4.5 that
        # no guide sentence supports — it came from a curator note ("IELTS may also be accepted,
        # confirm with college"). Keep such values out of the "verified" set so a consumer can tell
        # a quoted requirement from an unconfirmed one.
        _prose = " ".join(str(entry.get(k) or "") for k in ("lang_req", "lang_note"))
        _txt_ielts = score_lower_bound(_prose, "ielts") if _prose.strip() else None
        # TOEFL appears on several scales (iBT / CBT / PBT / TEPS / the 2026 1-6 scale) and the KB
        # mixed them inside one number column: 530 (CBT) next to 71 (iBT), and 800 which is a TEPS
        # score, not TOEFL at all. Prefer the number the guide text actually attaches to the test
        # keyword and record which scale it is; drop a value the text does not support.
        _txt = " ".join(str(entry.get(k) or "") for k in ("lang_req", "lang_note", "topik_req",
                                                          "toefl_req"))
        _low = _txt.lower()
        # The scale must come from the keyword *attached to the chosen number*: a guide often lists
        # "530 (CBT 197, iBT 71)" — keying off word presence labelled the iBT value 71 as "cbt".
        toefl, toefl_scale = toefl_from_text(_txt)
        _topik = score_lower_bound(entry.get("topik_req"), "topik")
        _txt_topik = score_lower_bound(_prose, "topik") if _prose.strip() else None
        # A published number whose own guide sentence never mentions that test has no basis — and a
        # stale value survives the upsert (coalesce keeps the old row when the new value is NULL), so
        # it must be cleared explicitly. 국민대 ma carried TOEFL 50 scraped from "전자공학전공 50%↑ 영어".
        if toefl is None and not re.search(r"toefl|ibt", _txt, re.I):
            f["_clear_toefl"] = True
        if ielts is None and not re.search(r"ielts", _txt, re.I):
            f["_clear_ielts"] = True
        if _topik is None and not re.search(r"topik|급", _txt):
            f["_clear_topik"] = True
        f.update(topik_req=_topik,
                 req_verified=all([
                     _topik is None or _txt_topik is not None,
                     ielts is None or _txt_ielts is not None,
                     toefl is None or ("toefl" in _txt.lower() or "ibt" in _txt.lower()),
                 ]),
                 ielts_req=ielts, toefl_req=toefl, toefl_scale=toefl_scale,
                 lang_req_text=entry.get("lang_req") or entry.get("lang_note") or
                 (entry.get("topik_req") if isinstance(entry.get("topik_req"), str) else None),
                 scholarship_note=(entry.get("scholarship_note") or "")[:2000] or None,
                 note=entry.get("guide_effective_note"))
    return f


def majors_of(entry: dict) -> list[str]:
    names = []
    for key in ("majors_full", "majors_ba", "majors", "majors_sample", "popular_majors"):
        v = entry.get(key)
        if isinstance(v, list):
            names += [x for x in v if isinstance(x, str) and x.strip()]
    seen, out = set(), []
    for n in names:
        n = n.strip()
        if n and n not in seen:
            seen.add(n)
            out.append(n)
    return out


def tuition_rows(entry: dict) -> list[dict]:
    """-> [{scope, tier, unit, amount, note, ref}] ; ref = college/department name or None."""
    rows = []
    by_dept = entry.get("tuition_semester_by_dept")
    if isinstance(by_dept, dict):
        fields = by_dept.get("fields")
        if isinstance(fields, dict):
            for k, v in fields.items():
                amt, _ = money_strict(v)
                if amt:
                    rows.append(dict(scope="college", tier="semester", unit="per_semester",
                                     amount=amt, ref=k, note=by_dept.get("note")))
    for coll, v in (entry.get("tuition_per_college_semester") or {}).items():
        raw = v.get("수업료합계") if isinstance(v, dict) else v
        amt, _ = money_strict(raw)
        if amt:
            rows.append(dict(scope="college", tier="semester", unit="per_semester",
                             amount=amt, ref=coll, note=None))
    tmin = money_strict(entry.get("tuition_min"))[0]
    tmax = money_strict(entry.get("tuition_max"))[0]
    if tmin is None:
        c = money_strict(entry.get("tuition_semester"))[0]
        d = money_strict(entry.get("tuition_range"))[0]
        tmin = c if c is not None else d
    if tmin:
        rows.append(dict(scope="program", tier="semester", unit="per_semester", amount=tmin,
                         ref=None, note="min"))
    if tmax and tmax != tmin:
        rows.append(dict(scope="program", tier="semester", unit="per_semester", amount=tmax,
                         ref=None, note="max"))
    return rows


SCORE_TYPE = {"topik": "topik", "ielts": "ielts", "toefl": "toefl", "gpa": "gpa"}


def cond_type(score_type: str):
    s = (score_type or "").lower()
    for k, v in SCORE_TYPE.items():
        if k in s:
            return v
    return "general" if s else "none"


BENEFIT = [("%", "percent"), ("면제", "fee_waiver"), ("전액", "fee_waiver"),
           ("기숙사", "dorm"), ("원", "amount")]


def benefit_type(text: str):
    t = text or ""
    for k, v in BENEFIT:
        if k in t:
            return v
    return "other"


def scholarships_of(entry: dict) -> list[dict]:
    """Normalise every shape the KB uses into {name,type,category,tiers:[...]}."""
    out = []
    seen = set()

    def add(name, typ, cat, tiers, note=None):
        key = (name, typ)
        if not name or key in seen:
            return
        seen.add(key)
        out.append(dict(name=name.strip(), type=typ, category=cat, tiers=tiers, note=note))

    cat_map = {"language": "language", "academic": "academic", "both": "both", "general": "general"}
    for item in as_list(entry.get("scholarships_categorized")):
        if not isinstance(item, dict):
            continue
        typ = "existing" if str(item.get("type", "")).lower().startswith("exist") else "enroll"
        cat = cat_map.get(str(item.get("category", "")).lower(), "general")
        if "tiers" in item:
            tiers = [dict(condition_type=cond_type(t.get("score_type")),
                          condition_text=t.get("score"), condition_min=num(t.get("score")),
                          benefit_text=t.get("amount"),
                          benefit_type=benefit_type(t.get("amount")),
                          benefit_value=num(t.get("amount")))
                     for t in as_list(item.get("tiers")) if isinstance(t, dict)]
            add(item.get("name"), typ, cat, tiers)
        else:
            cond = item.get("condition")
            ben = item.get("benefit")
            add(item.get("name"), typ, cat,
                [dict(condition_type=cond_type(cond), condition_text=cond, condition_min=num(cond),
                      benefit_text=ben, benefit_type=benefit_type(ben), benefit_value=num(ben))])

    cur = entry.get("scholarship_curated")
    for item in as_list(cur):
        if isinstance(item, dict):
            add(item.get("name"), "existing" if item.get("type") == "existing" else "enroll",
                cat_map.get(str(item.get("category", "")).lower(), "general"),
                [dict(condition_type=cond_type(item.get("condition")),
                      condition_text=item.get("condition"), condition_min=num(item.get("condition")),
                      benefit_text=item.get("benefit"),
                      benefit_type=benefit_type(item.get("benefit")),
                      benefit_value=num(item.get("benefit")))])

    flat = entry.get("scholarships")
    if isinstance(flat, dict):
        for typ in ("enroll", "existing"):
            for line in as_list(flat.get(typ)):
                if not isinstance(line, str):
                    continue
                name, _, rest = line.partition(":")
                add(name, typ, "general", [dict(condition_type=cond_type(rest),
                                                condition_text=rest.strip() or None,
                                                condition_min=num(rest),
                                                benefit_text=rest.strip() or None,
                                                benefit_type=benefit_type(rest),
                                                benefit_value=num(rest))])
    elif isinstance(flat, list):
        for line in flat:
            if not isinstance(line, str):
                continue
            name, _, rest = line.partition(":")
            if rest.strip() and num(rest) is None and len(rest) < 8:
                add(name, "enroll", "general",
                    [dict(condition_type="none", condition_text=None, condition_min=None,
                          benefit_text=rest.strip(), benefit_type=benefit_type(rest),
                          benefit_value=num(rest))])
            else:
                add(name or line, "enroll", "general",
                    [dict(condition_type=cond_type(rest or line), condition_text=(rest or line).strip(),
                          condition_min=num(rest or line), benefit_text=(rest or line).strip(),
                          benefit_type=benefit_type(rest or line), benefit_value=num(rest or line))])
    return out


# ---------------------------------------------------------------- main load
def build(kb: dict) -> dict:
    canon = canonical_ids()
    data = dict(schools={}, documents={}, programs=[], colleges=[], departments=[], tuition=[],
                rounds=[], scholarships=[], curated=[])
    levels = [("ba", kb.get("schools") or {}, False),
              ("ma", (kb.get("master") or {}).get("schools") or {}, False),
              ("junior", (kb.get("junior") or {}).get("schools") or {}, False),
              ("lang", (kb.get("lang_programs") or {}).get("schools") or {}, True)]

    # The KB mixes short and full names for the same school ('국민대' vs '국민대학교'), which would
    # create two cat.school rows and split that school's programs in half. Fold the short form into
    # the full form and keep the short form as an alias.
    all_names = set()
    for _level, entries, _lang in levels:
        all_names |= set(entries)
    short_of = {n: n + "학교" for n in all_names if (n + "학교") in all_names and n not in canon}

    def canonical_name(n: str) -> str:
        return short_of.get(n, n)

    years_by_school_level = defaultdict(set)
    for level, entries, _ in levels:
        for name, entry in entries.items():
            if not isinstance(entry, dict):
                continue
            yr = int_year(entry.get("guide_effective_year"), entry.get("guide_year")) or ASSUMED_YEAR
            years_by_school_level[(canonical_name(name), level)].add(yr)

    for level, entries, is_lang in levels:
        for name, entry in entries.items():
            if not isinstance(entry, dict):
                continue
            cname = canonical_name(name)
            sid, name_en, aliases, c_region, c_type = canon.get(cname, (slug(cname), None, [], None, None))
            aliases = list(aliases)
            if cname != name:
                aliases.append(name)
            if sid not in data["schools"]:
                data["schools"][sid] = dict(
                    id=sid, name_kr=cname,
                    name_en=entry.get("name_en") or name_en,
                    region=entry.get("region") or c_region,
                    loc=entry.get("loc"), category="junior_college" if level == "junior" else
                    ("language" if level == "lang" else "university"),
                    type=entry.get("type") or c_type,
                    rank=num(entry.get("rank")), students=num(entry.get("student_count")),
                    foreign_students=num(entry.get("foreign_students")),
                    ieqas_certified=as_bool(entry.get("ieqas_certified")),
                    ieqas_level=entry.get("ieqas_level"),
                    ieqas_year=int_year(entry.get("ieqas_year")),
                    excluded=bool(entry.get("excluded")), exclude_reason=entry.get("exclude_reason"),
                    aliases=aliases)
            else:
                # same school reached through another level/section: merge aliases in
                have = set(data["schools"][sid].get("aliases") or [])
                data["schools"][sid]["aliases"] = sorted(have | set(aliases))
            yr = int_year(entry.get("guide_effective_year"), entry.get("guide_year")) or ASSUMED_YEAR
            pdf = entry.get("guide_effective_pdf") or entry.get("guide_pdf")
            url = entry.get("guide_url") or entry.get("guide_page_url")
            if not pdf and not url:
                continue
            md5v, size = file_md5(pdf) if pdf else (None, None)
            path = pdf or f"url:{url}"
            label_y, yr, carried = resolve_years(entry, path, yr)
            if carried:
                carried_forward.append(dict(path=path, file_year=label_y, used_for_year=yr,
                                            note=str(entry.get("guide_effective_note"))[:160],
                                            school=name, level=level))
            data["documents"][path] = dict(
                md5=md5v or _md5_text(path), path=path,
                file_name=pathlib.Path(pdf).name if pdf else None,
                level=level, label_year=label_y, effective_year=yr, carried_forward=carried,
                school_id=sid, kind="pdf" if pdf else "page-render", url=url, bytes=size,
                tier="A" if entry.get("_llm_parsed") else "C",
                status="parsed" if md5v else "detected",
                reject_reason=None if md5v else "source file not present locally")
            pf = program_fields(entry, level)
            for flag, col in (("_clear_toefl", "toefl_req"), ("_clear_ielts", "ielts_req"),
                              ("_clear_topik", "topik_req")):
                if pf.pop(flag, None):
                    data.setdefault("clear_scores", []).append((sid, level, col))
            # is_current is decided in SQL (newest guide_year per school+level), so no max_year here
            data["programs"].append(dict(
                school_id=sid, level=level, guide_year=yr, effective_year=yr,
                doc_path=path, evidence=1.0 if entry.get("_llm_parsed") else 0.6,
                asserted_by="verified_kb.json", **pf))
            for m in majors_of(entry):
                data["departments"].append(dict(school_id=sid, level=level, year=yr, name=m,
                                                english=False, college=None))
            for m in as_list(entry.get("eng_track_majors")):
                if isinstance(m, str) and m.strip():
                    data["departments"].append(dict(school_id=sid, level=level, year=yr, name=m.strip(),
                                                    english=True, college=None))
            for r in tuition_rows(entry):
                data["tuition"].append(dict(school_id=sid, level=level, year=yr, **r))
            for rng in date_ranges(entry.get("period") or ""):
                data["rounds"].append(dict(school_id=sid, level=level, year=yr,
                                           starts_on=rng[0], ends_on=rng[1],
                                           period_text=entry.get("period")))
            for s in scholarships_of(entry):
                data["scholarships"].append(dict(school_id=sid, level=level, year=yr, **s))

    for key, node in (("visa_restricted_2026", kb.get("visa_restricted_2026")),
                      ("free_major_programs", kb.get("free_major_programs")),
                      ("ai_departments", kb.get("ai_departments")),
                      ("medical_reqs", kb.get("medical_reqs")),
                      ("selftest", kb.get("selftest"))):
        if not node:
            continue
        src = node.get("source") if isinstance(node, dict) else None
        note = node.get("note") if isinstance(node, dict) else None
        data["curated"].append(dict(id=key, name=key, source_text=src, note=note,
                                    schools=node.get("schools") if isinstance(node, dict) else None,
                                    items=node if not isinstance(node, dict) else None,
                                    raw=node if isinstance(node, dict) else None,
                                    degree=node.get("degree_restricted") if isinstance(node, dict) else None,
                                    lang=node.get("lang_restricted") if isinstance(node, dict) else None))
    return data


def write_all(conn, data, verbose=True):
    cur = conn.cursor()
    stats = Counter()
    for s in data["schools"].values():
        cur.execute("""
            insert into cat.school (id,name_kr,name_en,region,loc,category,type,rank,students,
                                    foreign_students,ieqas_certified,ieqas_level,ieqas_year,
                                    excluded,exclude_reason)
            values (%(id)s,%(name_kr)s,%(name_en)s,%(region)s,%(loc)s,%(category)s,%(type)s,
                    %(rank)s,%(students)s,%(foreign_students)s,%(ieqas_certified)s,%(ieqas_level)s,
                    %(ieqas_year)s,%(excluded)s,%(exclude_reason)s)
            on conflict (id) do update set
              name_kr=excluded.name_kr, name_en=coalesce(excluded.name_en,cat.school.name_en),
              region=coalesce(excluded.region,cat.school.region), loc=coalesce(excluded.loc,cat.school.loc),
              type=coalesce(excluded.type,cat.school.type), rank=coalesce(excluded.rank,cat.school.rank),
              students=coalesce(excluded.students,cat.school.students),
              foreign_students=coalesce(excluded.foreign_students,cat.school.foreign_students),
              ieqas_certified=coalesce(excluded.ieqas_certified,cat.school.ieqas_certified),
              ieqas_level=coalesce(excluded.ieqas_level,cat.school.ieqas_level),
              ieqas_year=coalesce(excluded.ieqas_year,cat.school.ieqas_year),
              excluded=excluded.excluded, exclude_reason=excluded.exclude_reason,
              updated_at=now()
        """, s)
        stats["school"] += 1
        for a in s.get("aliases") or []:
            cur.execute("""insert into cat.school_alias (school_id,alias,kind) values (%s,%s,'short')
                           on conflict do nothing""", (s["id"], a))
    doc_ids = {}
    # any school row that is not in this build is a folded-away short-form shell (or a school the
    # KB dropped): remove it — cascades take its stale programs with it
    cur.execute("delete from cat.school where id <> all(%s)", (list(data["schools"]),))
    stats["stale_schools_removed"] = cur.rowcount
    for path, d in data["documents"].items():
        cur.execute("""
            insert into cat.guide_document (md5,path,file_name,level,label_year,effective_year,school_id,
                                            kind,url,bytes,tier,status,reject_reason,carried_forward)
            values (%(md5)s,%(path)s,%(file_name)s,%(level)s,%(label_year)s,%(effective_year)s,
                    %(school_id)s,%(kind)s,%(url)s,%(bytes)s,%(tier)s,%(status)s,%(reject_reason)s,
                    %(carried_forward)s)
            on conflict (md5) do update set
              path=excluded.path, level=excluded.level, label_year=excluded.label_year,
              effective_year=excluded.effective_year, school_id=excluded.school_id,
              url=coalesce(excluded.url,cat.guide_document.url),
              bytes=coalesce(excluded.bytes,cat.guide_document.bytes),
              tier=excluded.tier, status=excluded.status, reject_reason=excluded.reject_reason,
              carried_forward=excluded.carried_forward, updated_at=now()
            returning id
        """, d)
        doc_ids[path] = cur.fetchone()[0]
        stats["guide_document"] += 1
    prog_ids = {}
    prog_doc = {}
    prog_meta = {}
    for p in data["programs"]:
        doc_id = doc_ids.get(p["doc_path"])
        if not doc_id:
            stats["program_skipped_no_doc"] += 1
            continue
        cur.execute("""
            insert into cat.program (school_id,level,guide_year,effective_year,period_text,topik_req,
                ielts_req,toefl_req,toefl_scale,req_verified,lang_req_text,tuition_min,tuition_max,tuition_note,apply_system,
                apply_system_all,ieqas_certified,ieqas_level,ieqas_course,ieqas_year,student_count,
                foreign_students,note,scholarship_note,lang_per_term,lang_total_hours,lang_dorm,
                lang_d4_eligible,status,is_current,source_doc_id,asserted_by,evidence)
            values (%(school_id)s,%(level)s,%(guide_year)s,%(effective_year)s,%(period_text)s,
                %(topik_req)s,%(ielts_req)s,%(toefl_req)s,%(toefl_scale)s,%(req_verified)s,%(lang_req_text)s,%(tuition_min)s,
                %(tuition_max)s,%(tuition_note)s,%(apply_system)s,%(apply_system_all)s,
                %(ieqas_certified)s,%(ieqas_level)s,%(ieqas_course)s,%(ieqas_year)s,%(student_count)s,
                %(foreign_students)s,%(note)s,%(scholarship_note)s,%(lang_per_term)s,
                %(lang_total_hours)s,%(lang_dorm)s,
                %(lang_d4_eligible)s,'active',false,%(doc_id)s,%(asserted_by)s,%(evidence)s)
            on conflict (school_id,level,guide_year) do update set
              effective_year=excluded.effective_year, period_text=coalesce(excluded.period_text,cat.program.period_text),
              topik_req=coalesce(excluded.topik_req,cat.program.topik_req),
              ielts_req=coalesce(excluded.ielts_req,cat.program.ielts_req),
              toefl_req=coalesce(excluded.toefl_req,cat.program.toefl_req),
              toefl_scale=coalesce(excluded.toefl_scale,cat.program.toefl_scale),
              req_verified=coalesce(excluded.req_verified,cat.program.req_verified),
              lang_req_text=coalesce(excluded.lang_req_text,cat.program.lang_req_text),
              tuition_min=coalesce(excluded.tuition_min,cat.program.tuition_min),
              tuition_max=coalesce(excluded.tuition_max,cat.program.tuition_max),
              tuition_note=coalesce(excluded.tuition_note,cat.program.tuition_note),
              apply_system=coalesce(excluded.apply_system,cat.program.apply_system),
              apply_system_all=coalesce(excluded.apply_system_all,cat.program.apply_system_all),
              ieqas_certified=coalesce(excluded.ieqas_certified,cat.program.ieqas_certified),
              ieqas_level=coalesce(excluded.ieqas_level,cat.program.ieqas_level),
              ieqas_course=coalesce(excluded.ieqas_course,cat.program.ieqas_course),
              ieqas_year=coalesce(excluded.ieqas_year,cat.program.ieqas_year),
              student_count=coalesce(excluded.student_count,cat.program.student_count),
              foreign_students=coalesce(excluded.foreign_students,cat.program.foreign_students),
              note=coalesce(excluded.note,cat.program.note),
              scholarship_note=coalesce(excluded.scholarship_note,cat.program.scholarship_note),
              lang_per_term=coalesce(excluded.lang_per_term,cat.program.lang_per_term),
              lang_total_hours=coalesce(excluded.lang_total_hours,cat.program.lang_total_hours),
              lang_dorm=coalesce(excluded.lang_dorm,cat.program.lang_dorm),
              lang_d4_eligible=coalesce(excluded.lang_d4_eligible,cat.program.lang_d4_eligible),
              status='active', source_doc_id=excluded.source_doc_id,
              asserted_by=excluded.asserted_by, evidence=excluded.evidence, updated_at=now()
            returning id
        """, {**p, "doc_id": doc_id})
        prog_ids[(p["school_id"], p["level"], p["guide_year"])] = cur.fetchone()[0]
        prog_doc[(p["school_id"], p["level"], p["guide_year"])] = doc_id
        prog_meta[(p["school_id"], p["level"], p["guide_year"])] = p
        stats["program"] += 1

    # exactly one is_current per (school, level): newest year
    cur.execute("""
        with ranked as (
          select id, row_number() over (partition by school_id, level order by guide_year desc) rn
          from cat.program)
        update cat.program p set is_current = (r.rn = 1)
        from ranked r where r.id = p.id and p.is_current is distinct from (r.rn = 1)
    """)
    stats["is_current_set"] = cur.rowcount

    # children are derived: clear them for these programs so re-runs stay idempotent
    pids = list(prog_ids.values())
    cur.execute("delete from cat.scholarship_tier where scholarship_id in "
                "(select id from cat.scholarship where program_id = any(%s))", (pids,))
    for tbl in ("scholarship", "tuition", "application_round", "department"):
        cur.execute(f"delete from cat.{tbl} where program_id = any(%s)", (pids,))
    stats["children_cleared"] = len(pids)

    seen_dept = {}
    for d in data["departments"]:
        key = (d["school_id"], d["level"], d["year"])
        if key not in prog_ids or d["level"] == "lang":
            continue
        # the same major can appear both as a plain major and as an english-track major:
        # merge instead of letting whichever came first win
        k = (key, d["name"])
        seen_dept[k] = seen_dept.get(k, False) or bool(d["english"])
    for (key, name), is_english in seen_dept.items():
        pid = prog_ids.get(key)
        meta = prog_meta.get(key)
        if not pid or not meta:
            continue
        english = is_english
        cur.execute("""
            insert into cat.department (program_id,name,korean_track,english_track,
                                        korean_topik,korean_ielts,english_topik,english_ielts,
                                        source_doc_id)
            values (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (pid, name[:300], not english, english,
              meta.get("topik_req"), meta.get("ielts_req"),
              meta.get("topik_req") if english else None,
              meta.get("ielts_req") if english else None,
              prog_doc[key]))
        stats["department"] += 1

    for t in data["tuition"]:
        key = (t["school_id"], t["level"], t["year"])
        pid = prog_ids.get(key)
        if not pid:
            stats["tuition_skipped"] += 1
            continue
        cur.execute("""
            insert into cat.tuition (program_id,scope,tier,unit,amount_krw,note,source_doc_id)
            values (%s,%s,%s,%s,%s,%s,%s)
        """, (pid, t["scope"], t["tier"], t["unit"], t["amount"],
              (t["ref"] or "") + ((" | " + t["note"]) if t["note"] else "") or None,
              prog_doc[key]))
        stats["tuition"] += 1
    for r in data["rounds"]:
        key = (r["school_id"], r["level"], r["year"])
        pid = prog_ids.get(key)
        if not pid:
            continue
        cur.execute("""insert into cat.application_round (program_id,kind,starts_on,ends_on,period_text,
                         source_doc_id)
                       values (%s,'application',%s,%s,%s,%s)""",
                    (pid, r["starts_on"], r["ends_on"], r["period_text"], prog_doc[key]))
        stats["application_round"] += 1
    for s in data["scholarships"]:
        key = (s["school_id"], s["level"], s["year"])
        pid = prog_ids.get(key)
        if not pid:
            stats["scholarship_skipped"] += 1
            continue
        cur.execute("""insert into cat.scholarship (program_id,name,type,category,note,source_doc_id)
                       values (%s,%s,%s,%s,%s,%s) returning id""",
                    (pid, s["name"][:200], s["type"], s["category"], s.get("note"), prog_doc[key]))
        sch_id = cur.fetchone()[0]
        for t in s["tiers"]:
            cur.execute("""insert into cat.scholarship_tier (scholarship_id,condition_type,
                             condition_text,condition_min,benefit_type,benefit_value,benefit_text,
                             source_doc_id)
                           values (%s,%s,%s,%s,%s,%s,%s,%s)""",
                        (sch_id, t.get("condition_type"), t.get("condition_text"),
                         t.get("condition_min"), t.get("benefit_type"),
                         t.get("benefit_value"), t.get("benefit_text"), prog_doc[key]))
        stats["scholarship"] += 1

    # short/full name duplicates: '국민대' was folded into '국민대학교', so the leftover short-form
    # school row is an empty shell — drop it (its name lives on as an alias of the full row)
    cur.execute("""
        delete from cat.school s
        where exists (select 1 from cat.school b where b.name_kr = s.name_kr || '학교')
          and not exists (select 1 from cat.program p where p.school_id = s.id)
          and not exists (select 1 from cat.guide_document g where g.school_id = s.id)
    """)
    stats["school_dupes_removed"] = cur.rowcount
    if verbose:
        print("write stats:", dict(stats))
    return stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--reset", action="store_true", help="truncate cat.* before loading")
    args = ap.parse_args()

    kb = json.loads(KB_PATH.read_text(encoding="utf-8"))
    data = build(kb)
    print(f"schools={len(data['schools'])} documents={len(data['documents'])} "
          f"programs={len(data['programs'])} departments={len(data['departments'])} "
          f"tuition={len(data['tuition'])} rounds={len(data['rounds'])} "
          f"scholarships={len(data['scholarships'])} curated={len(data['curated'])}")
    if conflicts:
        rep = BACKEND / "_pg_year_conflicts.json"
        rep.write_text(json.dumps(conflicts, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"\nYEAR CONFLICTS (file name vs KB effective year): {len(conflicts)} -> {rep.name}")
        for c in conflicts[:12]:
            print(f"  {c['label_year']} (file) vs {c['kb_effective_year']} (kb effective)"
                  f" | kb guide_year={c['kb_guide_year']} | {pathlib.Path(c['path']).name[:60]}")
    if implausible_scores:
        rep5 = BACKEND / "_pg_implausible_scores.json"
        rep5.write_text(json.dumps(implausible_scores, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"IMPLAUSIBLE requirement scores rejected: {len(implausible_scores)} -> {rep5.name}")
    if inferred_scores:
        rep3 = BACKEND / "_pg_scores_inferred.json"
        rep3.write_text(json.dumps(inferred_scores, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"SCORES taken as lower bound from prose: {len(inferred_scores)} -> {rep3.name}")
    if carried_forward:
        rep4 = BACKEND / "_pg_carried_forward.json"
        rep4.write_text(json.dumps(carried_forward, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"\nCARRIED-FORWARD (구요강을 최신 사이클 데이터로 사용): {len(carried_forward)} -> {rep4.name}")
        for c in carried_forward[:10]:
            print(f"  {c['level']:6s} {c['school'][:16]:16s} file {c['file_year']} -> used for {c['used_for_year']}")
    if unparsed_money:
        rep2 = BACKEND / "_pg_unparsed_tuition.json"
        rep2.write_text(json.dumps(unparsed_money, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"UNPARSED tuition prose: {len(unparsed_money)} -> {rep2.name} (kept as tuition_note, "
              f"no digits written to numeric columns)")
    by_level = Counter((p["level"], p["guide_year"]) for p in data["programs"])
    for k in sorted(by_level):
        print(f"  program {k[0]:6s} {k[1]} : {by_level[k]}")
    if not args.write:
        print("\nDRY RUN — nothing written. Re-run with --write.")
        return

    conn = connect()
    try:
        if args.reset:
            with conn.cursor() as c:
                c.execute("""truncate cat.school, cat.guide_document, cat.program, cat.college,
                             cat.department, cat.tuition, cat.application_round, cat.scholarship,
                             cat.scholarship_tier, cat.curated_list, cat.curated_list_item,
                             cat.academyinfo_ref, cat.field_provenance, cat.field_change cascade""")
            print("cat.* truncated")
        stats = write_all(conn, data)
        # The upsert keeps existing values when a field arrives NULL (coalesce), which means a score
        # that was corrected to NULL would otherwise survive forever. Enforce the plausibility floors
        # on every run so a bogus "IELTS 3.0"/"TOEFL 3" cannot come back.
        with conn.cursor() as c:
            c.execute("update cat.program set ielts_req=null where ielts_req is not null and ielts_req < %s",
                      (SCORE_FLOOR["ielts"],))
            stats["scores_cleared_ielts"] = c.rowcount
            # The floor must not eat the 2026 scale: guides now print "TOEFL iBT 4.0 (기존 80)",
            # where 4 is a 1-6 score, not a broken iBT number. Only unlabelled sub-floor values go.
            c.execute("""update cat.program set toefl_req=null
                         where toefl_req is not null and toefl_req < %s
                           and coalesce(toefl_scale,'ibt') <> 'new_2026'""",
                      (SCORE_FLOOR["toefl"],))
            stats["scores_cleared_toefl"] = c.rowcount
            # The old "IELTS = TOPIK int" bug also produced values that sit AT the floor (한양대 ma
            # showed ielts 4.0 from TOPIK 4급), so a floor test alone cannot find them. An IELTS/TOEFL
            # value that equals the TOPIK grade, while the guide text never mentions that test, is an
            # artifact: clear it (the raw text stays in lang_req_text).
            c.execute("""update cat.program set ielts_req=null
                         where ielts_req is not null and topik_req is not null
                           and ielts_req = topik_req
                           and coalesce(lang_req_text,'') not ilike '%ielts%'""")
            stats["scores_cleared_ielts_eq_topik"] = c.rowcount
            c.execute("""update cat.program set toefl_req=null
                         where toefl_req is not null and topik_req is not null
                           and toefl_req = topik_req
                           and coalesce(lang_req_text,'') !~* '(toefl|ibt)'""")
            stats["scores_cleared_toefl_eq_topik"] = c.rowcount
            # A TOEFL number above 120 cannot be on the iBT scale: it is CBT/PBT/TEPS written into a
            # scale-less column (530, 800 …). Without a matching scale label, publish nothing.
            # scores whose guide sentence never mentions the test at all (stale values survive
            # the coalesce upsert, so they are cleared explicitly)
            cleared = 0
            for sid, level, col in data.get("clear_scores", []):
                c.execute(f"""update cat.program set {col}=null
                               where school_id=%s and level=%s and is_current and {col} is not null""",
                          (sid, level))
                cleared += c.rowcount
            stats["scores_cleared_no_keyword"] = cleared
            c.execute("""update cat.program set topik_req=null
                         where topik_req is not null and (topik_req < 1 or topik_req > 6)""")
            stats["scores_cleared_topik_range"] = c.rowcount
            c.execute("""update cat.department set korean_topik=null
                         where korean_topik is not null and (korean_topik < 1 or korean_topik > 6)""")
            c.execute("""update cat.department set english_topik=null
                         where english_topik is not null and (english_topik < 1 or english_topik > 6)""")
            c.execute("""update cat.program set toefl_req=null
                         where toefl_req is not null and toefl_req > 120
                           and coalesce(toefl_scale,'') not in ('cbt','pbt')""")
            stats["scores_cleared_toefl_scale"] = c.rowcount
            c.execute("""update cat.department set korean_ielts=null
                         where korean_ielts is not null and korean_ielts < %s""",
                      (SCORE_FLOOR["ielts"],))
            c.execute("""update cat.department set english_ielts=null
                         where english_ielts is not null and english_ielts < %s""",
                      (SCORE_FLOOR["ielts"],))
        if stats.get("scores_cleared_ielts") or stats.get("scores_cleared_toefl"):
            print(f"cleared implausible scores: ielts={stats.get('scores_cleared_ielts')} "
                  f"toefl={stats.get('scores_cleared_toefl')}")
        conn.commit()
        print("COMMITTED")
        with conn.cursor() as c:
            for tbl in ("school", "guide_document", "program", "tuition", "application_round",
                        "scholarship", "scholarship_tier"):
                c.execute(f"select count(*) from cat.{tbl}")
                print(f"  cat.{tbl}: {c.fetchone()[0]}")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()