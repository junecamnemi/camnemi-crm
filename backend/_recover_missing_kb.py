"""Recover parsed guides that never reached the KB.

`_merge_llm_into_kb.py` is fill-only: it updates existing school entries but never CREATES one. So a
guide that was parsed for a (school, level) the KB had no entry for silently disappeared — 제주대 MA
(84 majors from 제주대학교_MA_2027.pdf) was one, while the live `universities` table still had it.

This script finds those parsed-but-unmerged records and creates the missing KB entries.
Nothing is invented: every field comes from the parse record, and `source` records the PDF it came
from. Dry-run by default.

  python _recover_missing_kb.py            # report
  python _recover_missing_kb.py --write    # add to verified_kb.json (with backup)
"""
from __future__ import annotations

import argparse
import glob
import json
import pathlib
import shutil
from datetime import datetime

BACKEND = pathlib.Path(__file__).parent
KB_PATH = BACKEND / "verified_kb.json"
PARSED_GLOBS = ["_pipeline_data/parsed/*.jsonl", "_parse_library.jsonl"]
SECTION = {"ba": ("schools", "schools"), "ma": ("master", "schools"),
           "junior": ("junior", "schools"), "lang": ("lang", "lang_programs")}


def norm(name: str) -> str:
    """Loose key so '국립한밭대학교' == '한밭대학교' == '한밭대' and '한양대학교(ERICA)' == '한양대학교 ERICA'.

    Without this, every parsed record whose school name is spelled slightly differently would be
    'recovered' as a brand-new school and re-create the duplicate rows we just cleaned up.
    """
    s = (name or "").strip()
    s = s.replace("국립", "").replace("(", " ").replace(")", " ").replace("·", "")
    s = "".join(ch for ch in s if ch.isalnum() or ch.isspace())
    s = s.replace(" ", "").lower()
    for suf in ("대학교", "대학원", "대학", "대"):
        if s.endswith(suf) and len(s) > len(suf):
            s = s[: -len(suf)]
            break
    return s


def kb_index(kb: dict) -> tuple[dict, dict]:
    """-> ({(norm_name, level): kb_name}, {norm_name: kb_name})"""
    by_level, by_name = {}, {}
    for level, (sec, key) in SECTION.items():
        node = kb.get(sec) or {}
        holder = node.get(key) if key in node else node
        for name in (holder or {}):
            by_level.setdefault((norm(name), level), name)
            by_name.setdefault(norm(name), name)
    return by_level, by_name


def load_parsed() -> dict:
    """(school, level) -> best record (most majors wins)."""
    best: dict = {}
    for pattern in PARSED_GLOBS:
        for path in glob.glob(str(BACKEND / pattern)):
            for line in pathlib.Path(path).read_text(encoding="utf-8", errors="ignore").splitlines():
                line = line.strip()
                if not line.startswith("{"):
                    continue
                try:
                    r = json.loads(line)
                except json.JSONDecodeError:
                    continue
                school = r.get("school")
                level = (r.get("program") or r.get("_prog_hint") or "").lower()
                if not school or level not in SECTION:
                    continue
                n = len(r.get("majors") or [])
                key = (school, level)
                if key not in best or n > len(best[key].get("majors") or []):
                    best[key] = {**r, "_from": pathlib.Path(path).name}
    return best


def entry_from(rec: dict, level: str) -> dict:
    pdf = rec.get("_pdf") or rec.get("_source_pdf") or rec.get("_file")
    e = {
        "name": rec["school"],
        "region": rec.get("region"),
        "rank": rec.get("rank"),
        "n_majors": len(rec.get("majors") or []),
        "majors": rec.get("majors") or [],
        "majors_sample": (rec.get("majors") or [])[:12],
        "tuition_min": rec.get("tuition_min"),
        "tuition_max": rec.get("tuition_max"),
        "period": rec.get("period"),
        "lang_req": rec.get("lang_req"),
        "topik_req": rec.get("topik"),
        "ielts_req": rec.get("ielts"),
        "toefl_req": rec.get("toefl"),
        "guide_year": rec.get("year"),
        "guide_effective_year": rec.get("year"),
        "guide_pdf": pdf,
        "source": f"recovered from parse: {rec.get('_from')} ({pdf})",
        "_llm_parsed": {k: "LLM(parse-record)" for k in ("majors", "period", "lang_req") if rec.get(k)},
        "_recovered": {"by": "_recover_missing_kb.py",
                       "at": datetime.now().strftime("%Y-%m-%d"),
                       "parse_id": rec.get("_id"), "from": rec.get("_from")},
    }
    return {k: v for k, v in e.items() if v is not None}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--levels", default="ba,ma,junior",
                    help="levels to recover (default: ba,ma,junior; lang needs a different mapping)")
    ap.add_argument("--min-majors", type=int, default=1)
    ap.add_argument("--require-year", action="store_true",
                    help="only recover records that state a guide year")
    args = ap.parse_args()

    kb = json.loads(KB_PATH.read_text(encoding="utf-8"))
    parsed = load_parsed()
    by_level, by_name = kb_index(kb)
    missing, alias_hits = [], []
    for (school, level), rec in sorted(parsed.items()):
        sec, key = SECTION[level]
        node = kb.get(sec) or {}
        holder = node.get(key) if key in node else node
        holder = holder or {}
        if school in holder:
            continue
        n = norm(school)
        if (n, level) in by_level:       # same school+level, different spelling -> no new entry
            alias_hits.append((school, level, by_level[(n, level)], level))
            continue
        if n in by_name:                 # school known, but this level has no entry yet
            missing.append((by_name[n], level, rec))
            continue
        if not (rec.get("majors") or rec.get("period")):
            continue
        missing.append((school, level, rec))

    # one entry per (school, level): keep the newest year, then the most majors
    dedup = {}
    for school, level, rec in missing:
        key = (norm(school), level)          # '건국대학교 GLOCAL 캠퍼스' == '건국대학교 GLOCAL캠퍼스'
        yr = rec.get("year")
        yr = int(yr) if str(yr).isdigit() else 0
        score = (yr, len(rec.get("majors") or []))
        if key not in dedup or score > dedup[key][0]:
            dedup[key] = (score, school, rec)   # keep the real name, not the normalised key
    missing = [(name, lv, rec) for (_n, lv), (_s, name, rec) in sorted(dedup.items())]

    keep_levels = {x.strip() for x in args.levels.split(",") if x.strip()}
    before = len(missing)
    missing = [m for m in missing
               if m[1] in keep_levels
               and len(m[2].get("majors") or []) >= args.min_majors
               and (not args.require_year or str(m[2].get("year", "")).isdigit())]
    print(f"filtered by --levels/--min-majors/--require-year: {before} -> {len(missing)}")

    print(f"parsed (school, level) pairs: {len(parsed)}")
    print(f"same school, different spelling in KB (skipped, no new entry): {len(alias_hits)}")
    for a in alias_hits[:10]:
        print(f"    parsed '{a[0]}' ({a[1]}) == KB '{a[2]}' ({a[3]})")
    print(f"genuinely missing from KB: {len(missing)}")
    for school, level, rec in missing:
        print(f"  {level:6s} {school:22s} majors={len(rec.get('majors') or []):3d} "
              f"year={rec.get('year')} from={rec.get('_from')}")

    if not args.write or not missing:
        if not args.write:
            print("\nDRY RUN — re-run with --write to create these KB entries.")
        return

    backup = KB_PATH.with_suffix(f".json.bak_{datetime.now():%Y%m%d_%H%M%S}")
    shutil.copy2(KB_PATH, backup)
    added = 0
    for school, level, rec in missing:
        sec, key = SECTION[level]
        kb.setdefault(sec, {})
        if key in kb[sec]:
            kb[sec][key][school] = entry_from(rec, level)
        else:
            kb[sec][school] = entry_from(rec, level)
        added += 1
    kb.setdefault("meta", {})["recovered_entries"] = {
        "count": added, "at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "pairs": [f"{s}|{l}" for s, l, _ in missing]}
    KB_PATH.write_text(json.dumps(kb, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nadded {added} entries. backup: {backup.name}")
    print("next: python _merge_llm_into_kb.py --write --upgrade-years && python sync_3layer.py "
          "&& python coverage_guard.py")


if __name__ == "__main__":
    main()