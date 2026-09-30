#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ONE 보유현황 census: 모집요강 holdings by category and year, counting ONLY real guides.

Categories (operator's five buckets): 학사 / 석사 / 어학연수(대학교) / 전문학사 / 어학연수(전문대학교)

A file counts only when it is a real PDF (%PDF) with extractable text and guide-ish content;
HTML saved as .pdf, CMS placeholders and blank renders are reported separately as NOT guides —
that is the distinction that made earlier counts look wrong.

  python guide_census.py [--json]
Writes _pipeline_data/reports/_guide_census.json
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pipeline_paths as pp  # noqa: E402

GOOD_TEXT = re.compile(r"(한국어|어학연수|한국어교육원|국제교육원|어학당|연수생|유학생|모집요강|원서접수|전형|"
                       r"등록금|수강료|장학|Korean\s*(Language|Course|Program)|Language\s*(Course|Program)|"
                       r"Admission|International)", re.I)
BAD_TEXT = re.compile(r"(웹표준|Lazy binding|CMS의 장점|페이지를 찾을 수 없|접속이 차단|비정상적인 접근|"
                      r"로그인이 필요|삭제된 게시물|Access Denied)", re.I)
MIN_CHARS = 250

LEVEL_NAME = {"ba": "학사", "ma": "석사", "junior": "전문학사", "lang": "어학연수"}
ORDER = ["학사", "석사", "어학연수(대학교)", "전문학사", "어학연수(전문대학교)"]


def _norm(name: str) -> str:
    return re.sub(r"\[.*?\]|\(.*?\)", "", name or "").strip()


def _key(name: str) -> str:
    return re.sub(r"(대학교|대학|대)$", "", _norm(name))


def school_of(filename: str) -> str:
    parts = [p for p in re.sub(r"\.(pdf|hwp|html|do|php|asp|jsp)$", "", filename, flags=re.I).split("_")
             if not re.fullmatch(r"\d{4,}", p)]
    for p in parts:
        if _norm(p).endswith(("대학교", "대학")):
            return _norm(p)
    for p in parts:
        if _norm(p).endswith("대") and len(_norm(p)) >= 2:
            return _norm(p)
    return _norm(parts[0]) if parts else filename


def load_school_sets():
    univ = json.loads((HERE / "_adiga_univ_list.json").read_text(encoding="utf-8"))
    junior = json.loads((HERE / "_adiga_junior_list.json").read_text(encoding="utf-8"))
    kb = json.loads((HERE / "verified_kb.json").read_text(encoding="utf-8"))
    kb_short = {_key(s) for s in kb.get("master", {}).get("schools", kb)}
    return ({_key(v) for v in univ.values()}, {_key(v) for v in junior.values()}, kb_short)


def classify(filename: str, univ: set, junior: set, kb_short: set) -> str:
    k = _key(school_of(filename))
    if k in junior:
        return "junior"
    if k in univ or k in kb_short:
        return "univ"
    return "unknown"


def scan():
    univ, junior, kb_short = load_school_sets()
    rows = []
    for base in (pp.library_root(),):
        for root, _dirs, files in os.walk(base):
            for f in files:
                if not f.lower().endswith((".pdf", ".hwp")):
                    continue
                p = Path(root) / f
                rel = str(p.relative_to(base)).replace("\\", "/")
                parts = rel.split("/")
                rest = parts[parts.index("_archive") + 1:] if "_archive" in parts else parts
                level = next((x for x in rest if x in LEVEL_NAME), None)
                year = next((x for x in rest if re.fullmatch(r"20\d\d", x)), None) or \
                    (re.search(r"(20\d\d)", f).group(1) if re.search(r"(20\d\d)", f) else "unknown")
                rows.append({"name": f, "rel": rel, "level": level, "year": year,
                             "sk": _key(school_of(f)),
                             "kind": classify(f, univ, junior, kb_short)})
    return rows


def _cache_path() -> Path:
    return pp.REPORT_DIR / "_guide_verdict_cache.json"


def _load_cache() -> dict:
    try:
        return json.loads(_cache_path().read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_cache(cache: dict) -> None:
    try:
        pp.REPORT_DIR.mkdir(parents=True, exist_ok=True)
        _cache_path().write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
    except OSError:
        pass


def verdict(path: Path, cache: dict | None = None, key: str | None = None) -> tuple[str, int]:
    """('guide'|'html'|'thin'|'placeholder'|'error', chars) — cached on (size, mtime) so
    repeat censuses over the network drive stay fast."""
    try:
        st = path.stat()
    except OSError:
        return "error", 0
    if cache is not None and key:
        hit = cache.get(key)
        if hit and hit.get("size") == st.st_size and hit.get("mtime") == int(st.st_mtime):
            return hit["verdict"], hit["chars"]
    result = ("error", 0)
    try:
        if path.read_bytes()[:4] != b"%PDF":
            result = ("html", 0)
        else:
            import pymupdf
            doc = pymupdf.open(path)
            text = "".join(doc[i].get_text() for i in range(min(10, doc.page_count))).strip()
            doc.close()
            if len(text) < MIN_CHARS:
                result = ("guide_no_text", len(text))
            elif BAD_TEXT.search(text) and not GOOD_TEXT.search(text[:800]):
                result = ("placeholder", len(text))
            else:
                result = ("guide", len(text))
    except Exception:
        result = ("error", 0)
    if cache is not None and key:
        cache[key] = {"size": st.st_size, "mtime": int(st.st_mtime),
                      "verdict": result[0], "chars": result[1]}
    return result


def bucket(row) -> str:
    if row["level"] == "lang":
        return {"univ": "어학연수(대학교)", "junior": "어학연수(전문대학교)"}.get(row["kind"], "어학연수(미분류)")
    return LEVEL_NAME.get(row["level"], "기타")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true", help="print the machine-readable result")
    args = ap.parse_args()
    rows = scan()
    cache = _load_cache()
    counts = defaultdict(lambda: {"2026": [], "2027": [], "other": []})
    bad = []
    HELD = ("guide", "guide_no_text", "thin")  # a real PDF is a held guide; scan-only needs OCR

    for row in rows:
        path = pp.library_root() / row["rel"]
        kind, chars = verdict(path, cache, row["rel"])
        if kind == "thin":                      # legacy cache value
            kind = "guide_no_text"
        row["verdict"], row["chars"] = kind, chars
        if kind not in HELD:
            bad.append(row)
            continue
        year = row["year"] if row["year"] in ("2026", "2027") else "other"
        counts[bucket(row)][year].append(row)
    _save_cache(cache)

    table = {}
    print("%-22s %18s %18s %10s" % ("category", "2026 (건/교)", "2027 (건/교)", "total"))
    ocr_total = 0
    for name in ORDER:
        got = counts.get(name)
        if not got:
            continue
        f26, f27 = len(got["2026"]), len(got["2027"])
        s26 = len({r["sk"] for r in got["2026"]})
        s27 = len({r["sk"] for r in got["2027"]})
        total = f26 + f27 + len(got["other"])
        scantext = sum(1 for y in got.values() for r in y if r["verdict"] == "guide_no_text")
        ocr_total += scantext
        table[name] = {"2026": {"files": f26, "schools": s26}, "2027": {"files": f27, "schools": s27},
                       "total_files": total, "no_text_layer": scantext}
        print("%-22s %8d / %-8d %8d / %-8d %10d" % (name, f26, s26, f27, s27, total))
    tot26 = sum(v["2026"]["files"] for v in table.values())
    tot27 = sum(v["2027"]["files"] for v in table.values())
    all_schools = {r["sk"] for got in counts.values() for y in got.values() for r in y}
    print("%-22s %8d / %-8d %8d / %-8d %10d" % ("TOTAL", tot26,
          len({r["sk"] for v in counts.values() for r in v["2026"]}), tot27,
          len({r["sk"] for v in counts.values() for r in v["2027"]}),
          sum(v["total_files"] for v in table.values())))
    print("\ndistinct schools (all years):", len(all_schools))
    print("image-only (no text layer, needs OCR):", ocr_total)
    if bad:
        print("\nNOT counted as guides: %d files" % len(bad))
        breakdown = Counter((r["verdict"], bucket(r)) for r in bad)
        for k in sorted(breakdown, key=str):
            print("   %-12s %-20s %d" % (k[0], k[1], breakdown[k]))
    result = {"generated": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
              "library": str(pp.library_root()), "table": table,
              "totals": {"2026_files": tot26, "2027_files": tot27},
              "not_guides": len(bad),
              "not_guide_files": [{"file": r["rel"], "verdict": r["verdict"]} for r in bad]}
    pp.REPORT_DIR.mkdir(parents=True, exist_ok=True)
    (pp.REPORT_DIR / "_guide_census.json").write_text(json.dumps(result, ensure_ascii=False, indent=1),
                                                     encoding="utf-8")
    if args.json:
        print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())