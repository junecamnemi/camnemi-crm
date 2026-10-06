"""Publish recovered schools into the derived stores (consulting_db.json + data.js).

sync_3layer.py is fill-only, so a school that exists in verified_kb.json but not in the derived
stores never appears there (coverage_guard reports it as PENDING instead of a regression).
This script adds exactly those missing entries — it never rewrites an existing school.

  python publish_new_schools.py                 # dry run: show the sample entries
  python publish_new_schools.py --write         # apply (backups written next to each file)

Fields are mapped only from the KB; anything the KB does not have stays null/empty rather than being
guessed. Logo/image assets are a separate build step, so `logo` is null for new entries.
"""
from __future__ import annotations

from region_norm import canonical_or_none   # 지역 정식명 강제(파생 저장소 보호)

import argparse
import json
import pathlib
import re
import shutil
from datetime import datetime

BASE = pathlib.Path(__file__).resolve().parent.parent
KB = BASE / "backend" / "verified_kb.json"
DB = BASE / "backend" / "consulting_db.json"
DATA = BASE / "data.js"
PENDING = BASE / "backend" / "_pending_publish.json"

KB_SEC = {"BA": "schools", "MA": "master", "전문학사": "junior", "어학연수": "lang_programs"}
LIB_SEC = {"BA": ("schools", "schools"), "MA": ("master", "schools"),
           "전문학사": ("junior", "schools"), "어학연수": ("lang_programs", "schools")}


def _array_of(c: str) -> list:
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


def load_datajs() -> tuple[str, list, str]:
    raw = DATA.read_bytes()
    nl = "\r\n" if raw.count(b"\r\n") > 10 else "\n"
    c = raw.decode("utf-8").replace("\r\n", "\n")
    return c, _array_of(c), nl
    s = c.find("[")
    d = 0
    for i in range(s, len(c)):
        if c[i] == "[":
            d += 1
        elif c[i] == "]":
            d -= 1
            if d == 0:
                return c, json.loads(c[s:i + 1])
    raise SystemExit("data.js array not found")


def db_map_get(db: dict, school: str):
    for name, sc in db["schools"].items():
        if norm_name(name) == norm_name(school):
            return sc
    return None


def kb_schools_all(kb: dict, level: str) -> dict:
    sec = KB_SEC[level]
    node = kb.get(sec) or {}
    holder = node.get("schools", node) if isinstance(node, dict) else {}
    return {k: v for k, v in (holder or {}).items() if isinstance(v, dict)}


def kb_entry(kb: dict, school: str, level: str) -> dict:
    sec = KB_SEC[level]
    node = kb.get(sec) or {}
    holder = node.get("schools", node) if isinstance(node, dict) else {}
    return (holder or {}).get(school) or {}


def money(v):
    if v is None:
        return None
    s = str(v)
    digits = "".join(ch for ch in s if ch.isdigit())
    return int(digits) if digits and len(digits) >= 6 else (v if isinstance(v, int) else None)


def tuition_pair(entry: dict):
    lo = money(entry.get("tuition_min")) or money(entry.get("tuition_semester"))
    hi = money(entry.get("tuition_max")) or lo
    if isinstance(lo, int) and isinstance(hi, int) and hi < lo:
        lo, hi = hi, lo
    return lo, hi


def tuition_str(entry: dict) -> str | None:
    for k in ("tuition_semester", "tuition_range", "tuition_min"):
        v = entry.get(k)
        # '학기' or '학기(대학알리미 공시 기준)' is a unit label, not an amount: 한양대 MA published
        # the string "학기" as its tuition. A usable value has to contain a number.
        if isinstance(v, str) and re.search(r"\d", v):
            return v
    lo, hi = tuition_pair(entry)
    if isinstance(lo, int):
        return f"₩{lo:,}~₩{hi:,}" if hi and hi != lo else f"₩{lo:,}"
    return None


_SYN = {"글로컬": "glocal", "glocal": "glocal"}


def norm_name(name: str) -> str:
    """Match KB campus spellings to data.js ones: '(ERICA)' vs ' ERICA캠퍼스', '(글로컬)' vs 'GLOCAL'."""
    s = str(name or "").lower()
    for a, b in _SYN.items():
        s = s.replace(a, b)
    for ch in "()[]·,.-_ ":
        s = s.replace(ch, "")
    return s.replace("캠퍼스", "")


def js_tuition_min(univ: dict, lvl: str):
    """data.js is loosely typed: tuition.ba is sometimes a plain number, sometimes {min,max,...}."""
    t = (univ.get("tuition") or {})
    if not isinstance(t, dict):
        return t if isinstance(t, int) else None
    b = t.get(lvl)
    if isinstance(b, int):
        return b
    if isinstance(b, dict):
        return b.get("min")
    return None


def majors_of(entry: dict) -> list:
    for k in ("majors", "majors_full", "majors_ba", "majors_sample"):
        v = entry.get(k)
        if isinstance(v, list) and v and all(isinstance(x, str) for x in v):
            return v
    return []


def scholarships_flat(entry: dict) -> list:
    """-> [{name, condition, benefit}] for data.js, and enroll/existing lists for consulting_db."""
    # The KB stores categorized scholarships as a dict keyed by the guide's own heading
    # ({'입학장학금': [{name, benefit}, ...]}) while older records use a list of dicts. Iterating the
    # dict yielded its keys (strings), so every such school published an empty scholarship list.
    cats = entry.get("scholarships_categorized")
    items = []
    if isinstance(cats, dict):
        for cat, val in cats.items():
            for it in (val if isinstance(val, list) else [val]):
                if isinstance(it, dict):
                    items.append({**it, "_cat": cat})
                elif isinstance(it, str) and it.strip():
                    items.append({"name": f"{cat}: {it}", "_cat": cat})
    elif isinstance(cats, list):
        items = [it for it in cats if isinstance(it, dict)]
    out = []
    for item in items:
        if isinstance(item, dict):
            tiers = item.get("tiers") or []
            cond = item.get("condition") or "; ".join(
                f"{t.get('score_type','')} {t.get('score','')}".strip() for t in tiers if isinstance(t, dict))
            ben = item.get("benefit") or "; ".join(
                str(t.get("amount", "")) for t in tiers if isinstance(t, dict))
            out.append(dict(name=item.get("name"), condition=cond, benefit=ben))
    if not out:
        flat = entry.get("scholarships")
        if isinstance(flat, dict):
            for typ in ("enroll", "existing"):
                for line in flat.get(typ) or []:
                    if isinstance(line, str):
                        name, _, rest = line.partition(":")
                        out.append(dict(name=name, condition=rest.strip(), benefit=""))
        elif isinstance(flat, list):
            for line in flat:
                if isinstance(line, str):
                    out.append(dict(name=line, condition="", benefit=""))
                elif isinstance(line, dict) and line.get("name"):
                    # Some records store scholarships as [{name, condition, benefit}] directly
                    # (신성대·오산대 lang): ignoring the dict shape published no scholarship at all.
                    out.append(dict(name=line.get("name"),
                                    condition=line.get("condition") or "",
                                    benefit=line.get("benefit") or ""))
    return [s for s in out if s.get("name")]


def consult_entry(name: str, level: str, entry: dict) -> dict:
    lo, hi = tuition_pair(entry)
    sch = scholarships_flat(entry)
    return {
        "name": name,
        "region": entry.get("region"),
        "rank": entry.get("rank"),
        "programs": {level: {
            "topik": entry.get("topik_req"),
            "ielts": entry.get("ielts_req"),
            "tuition": tuition_str(entry),
            "tuition_max": hi,
            "scholarship": {"enroll": [f"{s['name']}: {s['condition']}→{s['benefit']}" for s in sch],
                            "existing": []},
            "period": entry.get("period"),
            "majors": majors_of(entry),
            "_new": True,
        }},
    }


def datajs_entry(name: str, levels: list, entries: dict, kb: dict) -> dict:
    pri = entries.get("BA") or entries.get("MA") or entries.get("전문학사") or {}
    kind = "junior" if set(levels) == {"전문학사"} else "univ"
    ba = entries.get("BA") or {}
    ma = entries.get("MA") or {}
    lo_ba, hi_ba = tuition_pair(ba)
    lo_ma, hi_ma = tuition_pair(ma)
    sch = scholarships_flat(ba or ma or pri)
    return {
        "n": name,
        "loc": canonical_or_none(pri.get("region")),
        "t": (ba or ma).get("topik_req"),
        "i": (ba or ma).get("ielts_req"),
        "eng": "",
        "majors": [],
        "tuition": {"ba": {"min": lo_ba, "max": hi_ba, "fields": {}},
                    "ma": {"min": lo_ma, "max": hi_ma, "fields": {}}},
        "en": None, "es": None, "ek": name, "logo": None,
        "stu": pri.get("student_count"), "rk": pri.get("rank"), "type": kind,
        "majors_ba": majors_of(ba), "majors_ma": majors_of(ma),
        "req": {"topik": (ba or ma).get("topik_req"), "ielts": (ba or ma).get("ielts_req"),
                "kiip": None, "sejong": None, "selftest": pri.get("selftest"), "english": False},
        "req_note": (ba or ma).get("lang_req") or "",
        "cert": {"degree": bool(pri.get("ieqas_certified")), "language": False, "excellent": False,
                 "foreign": str(pri.get("foreign_students") or ""), "foreign_pct": ""},
        "period": (ba or ma).get("period"),
        "lang_bypass": None,
        "fstu": pri.get("foreign_students"),
        "scholarships": sch,
        "_new": True,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    kb = json.loads(KB.read_text(encoding="utf-8"))
    db = json.loads(DB.read_text(encoding="utf-8"))
    pending = json.loads(PENDING.read_text(encoding="utf-8")) if PENDING.exists() else []
    if not pending:
        print("nothing pending — backfill pass only (run _pending_publish.py to refresh the list)")

    by_school = {}
    for p in pending:
        by_school.setdefault(p["school"], []).append(p["level"])

    c_text, data_js, eol = load_datajs()
    existing_js = {u.get("n") for u in data_js}
    new_db, new_js = {}, []
    for school, levels in sorted(by_school.items()):
        entries = {lvl: kb_entry(kb, school, lvl) for lvl in levels}
        for lvl, e in entries.items():
            if not e:
                print(f"  !! {school} [{lvl}] not found in KB (level mapping: {KB_SEC[lvl]})")
        merged = dict(entries.get("BA") or entries.get("MA") or entries.get("전문학사") or {})
        for lvl, e in entries.items():
            for k, v in e.items():
                merged.setdefault(k, v)
        if school not in db["schools"]:
            ce = consult_entry(school, levels[0], merged)
            for lvl in levels[1:]:
                ce["programs"][lvl] = consult_entry(school, lvl, entries[lvl])["programs"][lvl]
            new_db[school] = ce
        else:                                    # school known, this level is not
            for lvl in levels:
                db["schools"][school].setdefault("programs", {}).setdefault(
                    lvl, consult_entry(school, lvl, entries[lvl])["programs"][lvl])
        if school not in existing_js:
            new_js.append(datajs_entry(school, levels, entries, kb))
        else:                                    # fill the missing level on the existing entry
            tgt = next(u for u in data_js if u.get("n") == school)
            if "BA" in levels:
                tgt["majors_ba"] = tgt.get("majors_ba") or majors_of(entries["BA"])
                lo, hi = tuition_pair(entries["BA"])
                tgt["tuition"] = tgt.get("tuition") or {}
                tgt["tuition"]["ba"] = tgt["tuition"].get("ba") or {"min": lo, "max": hi, "fields": {}}
                tgt["period"] = tgt.get("period") or entries["BA"].get("period")
                tgt["t"] = tgt.get("t") or entries["BA"].get("topik_req")
                tgt["i"] = tgt.get("i") or entries["BA"].get("ielts_req")
            if "MA" in levels:
                tgt["majors_ma"] = tgt.get("majors_ma") or majors_of(entries["MA"])
                lo, hi = tuition_pair(entries["MA"])
                tgt["tuition"] = tgt.get("tuition") or {}
                tgt["tuition"]["ma"] = tgt["tuition"].get("ma") or {"min": lo, "max": hi, "fields": {}}
            if not tgt.get("scholarships"):
                tgt["scholarships"] = scholarships_flat(merged)

    # Backfill pass: entries already present in data.js often lack the period/requirements the KB
    # has (sync_3layer only fills consulting_db). Fill only empty fields - never overwrite.
    from collections import defaultdict
    _by_norm = defaultdict(list)
    for u in data_js:
        _by_norm[norm_name(u.get("n"))].append(u)

    def find_js(school):
        for u in data_js:
            if u.get("n") == school:
                return u
        hits = _by_norm.get(norm_name(school)) or []
        return hits[0] if len(hits) == 1 else None

    filled = 0
    for lvl, key in (("BA", "schools"), ("MA", "schools")):
        holder = (kb.get(key) if lvl == "BA" else ((kb.get("master") or {}).get("schools"))) or {}
        for school, entry in holder.items():
            if not isinstance(entry, dict):
                continue
            tgt = find_js(school)
            if tgt is None:
                continue
            changed = False
            if lvl == "BA":
                if not tgt.get("period") and entry.get("period"):
                    tgt["period"] = entry["period"]; changed = True
                if tgt.get("t") is None and entry.get("topik_req") is not None:
                    tgt["t"] = entry["topik_req"]; changed = True
                if tgt.get("i") is None and entry.get("ielts_req") is not None:
                    tgt["i"] = entry["ielts_req"]; changed = True
                if not tgt.get("majors_ba") and majors_of(entry):
                    tgt["majors_ba"] = majors_of(entry); changed = True
                if not js_tuition_min(tgt, "ba"):
                    lo, hi = tuition_pair(entry)
                    if lo:
                        tgt["tuition"] = tgt.get("tuition") or {}
                        tgt["tuition"]["ba"] = {"min": lo, "max": hi, "fields": {}}
                        changed = True
            else:
                if not tgt.get("majors_ma") and majors_of(entry):
                    tgt["majors_ma"] = majors_of(entry); changed = True
                if not js_tuition_min(tgt, "ma"):
                    lo, hi = tuition_pair(entry)
                    if lo:
                        tgt["tuition"] = tgt.get("tuition") or {}
                        tgt["tuition"]["ma"] = {"min": lo, "max": hi, "fields": {}}
                        changed = True
            if not tgt.get("scholarships"):
                sch = scholarships_flat(entry)
                if sch:
                    tgt["scholarships"] = sch; changed = True
            filled += changed
    # 전문학사 (junior college) entries were never backfilled: data.js keeps their tuition in the
    # "ba" slot, so the BA branch above never matched them and 9 colleges published no tuition.
    for school, entry in ((kb.get("junior") or {}).get("schools") or {}).items():
        if not isinstance(entry, dict):
            continue
        tgt = find_js(school)
        if tgt is None:
            continue
        changed = False
        if not tgt.get("period") and entry.get("period"):
            tgt["period"] = entry["period"]; changed = True
        if tgt.get("t") is None and entry.get("topik_req") is not None:
            tgt["t"] = entry["topik_req"]; changed = True
        if tgt.get("i") is None and entry.get("ielts_req") is not None:
            tgt["i"] = entry["ielts_req"]; changed = True
        if not tgt.get("majors_ba") and majors_of(entry):
            tgt["majors_ba"] = majors_of(entry); changed = True
        if not js_tuition_min(tgt, "ba"):
            lo, hi = tuition_pair(entry)
            if lo:
                tgt["tuition"] = tgt.get("tuition") or {}
                tgt["tuition"]["ba"] = {"min": lo, "max": hi, "fields": {}}
                changed = True
        if not tgt.get("scholarships"):
            sch = scholarships_flat(entry)
            if sch:
                tgt["scholarships"] = sch; changed = True
        filled += changed
    print(f"data.js backfilled fields on {filled} entries")

    # consulting_db backfill: sync_3layer.py only fills some keys, so pull the rest from the KB.
    dbfill = 0
    for lvl in ("BA", "MA", "전문학사", "어학연수"):
        for school, entry in kb_schools_all(kb, lvl).items():
            if not isinstance(entry, dict):
                continue
            sc = db["schools"].get(school) or db_map_get(db, school)
            if not sc:
                continue
            prog = (sc.get("programs") or {}).get(lvl)
            if not isinstance(prog, dict):      # some legacy rows keep a bare string here
                continue
            changed = False
            if not prog.get("tuition") and not prog.get("tuition_max"):
                ts = tuition_str(entry)
                if ts:
                    prog["tuition"] = ts; changed = True
            if not prog.get("period") and entry.get("period"):
                prog["period"] = entry["period"]; changed = True
            sch_now = prog.get("scholarship")
            if isinstance(sch_now, dict):
                # Categorized dicts ({'입학장학금': [...]}) hold real data under the guide's own
                # headings; testing only enroll/existing treated them as empty and overwrote the
                # structure with a flat list.
                has_sch = bool(sch_now.get("enroll") or sch_now.get("existing")) or \
                    any(v for v in sch_now.values())
            else:                               # list, string or None — any value means it is filled
                has_sch = bool(sch_now)
            if not has_sch:
                flat = scholarships_flat(entry)
                if flat:
                    prog["scholarship"] = [f"{s['name']}: {s['condition']}→{s['benefit']}"
                                           for s in flat]
                    changed = True
            dbfill += changed
    print(f"consulting_db backfilled fields on {dbfill} programs")

    print(f"schools to add: consulting_db={len(new_db)}  data.js={len(new_js)} "
          f"(levels: {sum(len(v) for v in by_school.values())})")
    for name in list(new_db)[:2]:
        print("\n--- consulting_db sample:", name)
        print(json.dumps(new_db[name], ensure_ascii=False, indent=1)[:900])
    if new_js:
        print("\n--- data.js sample:", new_js[0].get("n"))
        print(json.dumps(new_js[0], ensure_ascii=False, indent=1)[:900])

    if not args.write:
        print("\nDRY RUN — review the samples, then re-run with --write.")
        return

    stamp = f"{datetime.now():%Y%m%d_%H%M%S}"
    shutil.copy2(DB, DB.with_suffix(f".json.bak_{stamp}"))
    shutil.copy2(DATA, DATA.with_suffix(f".js.bak_{stamp}"))
    for name, entry in new_db.items():
        db["schools"][name] = entry
    DB.write_text(json.dumps(db, ensure_ascii=False, indent=1), encoding="utf-8")

    data_js.extend(new_js)
    start = c_text.find("[")
    end = c_text.rfind("]")                       # keep whatever precedes/follows the array
    out = (c_text[:start] + json.dumps(data_js, ensure_ascii=False, indent=1) +
           c_text[end + 1:]).replace("\r\n", "\n").replace("\n", eol)
    with open(DATA, "w", encoding="utf-8", newline="") as fh:
        fh.write(out)
    print(f"\nwrote: consulting_db +{len(new_db)} schools, data.js +{len(new_js)} entries "
          f"(backups *_bak_{stamp})")
    print("next: python _pending_publish.py && python coverage_guard.py")


if __name__ == "__main__":
    main()