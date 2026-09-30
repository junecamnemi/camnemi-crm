#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ONE place for every 외국인 모집요강 PDF.

`guides/{ba|ma|junior|lang}/{2026|2027}/` on the shared drive is the canonical
library. This tool scans every scattered PDF store on the host, dedupes by md5,
copies the missing foreigner guides into the library and writes one manifest
(`guides/_library_manifest.json`) that the rest of the pipeline reads.

Usage:
  python guide_library.py --report          # read-only inventory (no writes)
  python guide_library.py --apply           # ingest missing PDFs + write manifest
  python guide_library.py --verify          # manifest vs disk consistency check
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pipeline_paths as pp  # ONE data home

BACKEND = Path(__file__).resolve().parent
ROOT = BACKEND.parent

DRIVE_CANDIDATES = [
    Path("G:/공유 드라이브/Hermes/Camnemi/02_Crawling_Sheet/University_Project"),
    Path.home() / "내 드라이브" / "02_Crawling_Sheet" / "University_Project",
]


def drive_root() -> Path:
    for cand in DRIVE_CANDIDATES:
        if (cand / "guides").is_dir():
            return cand
    return DRIVE_CANDIDATES[0]


LEVEL_DIRS = ("ba", "ma", "junior", "lang")
YEARS = ("2026", "2027")
CURRENT_YEAR = "2027"   # the working set; older years live in _archive/

# Every place a 모집요강 PDF has historically piled up.
SCATTER_SOURCES = [
    (BACKEND / "_guide_pdfs", "ba"),
    (BACKEND / "_foreign_ba_pdf", "ba"),
    (BACKEND / "_foreign_ma_pdf", "ma"),
    (BACKEND / "_foreign_lang_pdf", "lang"),
    (BACKEND / "_foreign_batch10_pdf", None),
    (BACKEND / "daily_guide_pdf", "ba"),
    (BACKEND / "_foreign_junior_pdf", "junior"),
    (BACKEND / "_ownsite_daily", None),          # level from filename
    (ROOT / "guides_all", None),
    (ROOT / "_new_guides", None),                # operator drop-box: manual downloads land here
    (ROOT / "junior_guides", "junior"),
    (ROOT / "gks_guides", "ba"),
    (ROOT / "backend" / "_ownsite_daily", None),
]

NON_FOREIGN_TOKENS = ("재외국민", "수시", "정시", "편입학_국내", "국내고")


def norm(v: str) -> str:
    return re.sub(r"[\s_\-\.]+", "", (v or "").lower())


def level_for(path: Path, default: str | None = None) -> str:
    text = norm(str(path))
    if any(t in text for t in ("junior", "전문대", "전문학사", "전문대학")):
        return "junior"
    if any(t in text for t in ("어학", "lang", "language", "연수")):
        return "lang"
    if any(t in text for t in ("_ma", "대학원", "graduate", "석사")):
        return "ma"
    if any(t in text for t in ("_ba", "학부", "bachelor", "학사")):
        return "ba"
    return default or "ba"


def year_for(path: Path) -> str:
    m = re.search(r"(20\d\d)", path.name)
    if m:
        return m.group(1)
    m = re.search(r"(20\d\d)", str(path.parent))
    return m.group(1) if m else "2026"


def is_foreign_guide(path: Path) -> bool:
    text = norm(str(path))
    return not any(norm(t) in text for t in NON_FOREIGN_TOKENS)


def is_pdf(path: Path) -> bool:
    try:
        with path.open("rb") as f:
            return f.read(4) == b"%PDF"
    except OSError:
        return False


def md5(path: Path, limit: int = 8 << 20) -> str:
    h = hashlib.md5()
    with path.open("rb") as f:
        while chunk := f.read(1 << 20):
            h.update(chunk)
    return h.hexdigest()


def iter_library_pdfs(lib: Path):
    """Yield (level, year, path, archived) for the active tree and `_archive/`."""
    for level in LEVEL_DIRS:
        for year in list(YEARS) + ["2025", "unknown"]:
            folder = lib / level / year
            if folder.is_dir():
                for file in sorted(folder.glob("*.pdf")):
                    yield level, year, file, False
    archive = lib / "_archive"
    if archive.is_dir():
        for year_dir in sorted(p for p in archive.iterdir() if p.is_dir()):
            for level_dir in sorted(p for p in year_dir.iterdir() if p.is_dir()):
                for file in sorted(level_dir.glob("*.pdf")):
                    yield level_dir.name, year_dir.name, file, True


def scan_library(lib: Path) -> dict[str, dict]:
    """md5 -> record for every PDF already inside the canonical library."""
    index: dict[str, dict] = {}
    for level in LEVEL_DIRS:
        for year in list(YEARS) + ["2025", "unknown"]:
            folder = lib / level / year
            if not folder.is_dir():
                continue
            for file in sorted(folder.iterdir()):
                if file.suffix.lower() != ".pdf" or not file.is_file():
                    continue
                digest = md5(file)
                index.setdefault(digest, {
                    "md5": digest, "path": str(file), "name": file.name,
                    "level": level, "year": year, "bytes": file.stat().st_size,
                    "mtime": file.stat().st_mtime, "source": "library", "status": "present",
                })
    return index


def scan_scatter() -> list[dict]:
    found: list[dict] = []
    seen_paths = set()
    drive = drive_root()
    sources = list(SCATTER_SOURCES)
    for name in LEVEL_DIRS:
        for year in YEARS:
            sources.append((drive / f"adiga_{year}_{'전문대학' if name == 'junior' else {'ba': '외국인', 'ma': '대학원', 'lang': '어학연수'}[name]}_모집요강", name))
    sources.append((drive / "_ownsite_daily", None))
    for base, default_level in sources:
        if not base.is_dir():
            continue
        for file in base.rglob("*"):
            if not file.is_file() or file.suffix.lower() != ".pdf":
                continue
            if str(file) in seen_paths:
                continue
            seen_paths.add(str(file))
            if not is_foreign_guide(file):
                continue
            real = is_pdf(file)
            found.append({
                "path": str(file), "name": file.name,
                "level": level_for(file, default_level), "year": year_for(file),
                "status": "foreign" if real else "not_a_pdf",
                "source": base.name,
                "bytes": file.stat().st_size,
            })
    return found


def cmd_report(lib: Path) -> int:
    existing = scan_library(lib)
    found = scan_scatter()
    by_status: dict[str, int] = {}
    for rec in found:
        by_status[rec["status"]] = by_status.get(rec["status"], 0) + 1
    print(f"LIBRARY {lib}")
    for level in LEVEL_DIRS:
        row = [f"{level}: " + " ".join(f"{y}={len(list((lib / level / y).glob('*.pdf'))) if (lib / level / y).is_dir() else 0}" for y in YEARS)]
        print("  " + row[0])
    print(f"  unique PDFs in library: {len(existing)}")
    print(f"SCATTER scanned: {len(found)} foreign-named PDFs ({by_status})")
    new = [r for r in found if r["status"] == "foreign"]
    print(f"SCATTER files to hash/dedupe against library: {len(new)}")
    return 0


def cmd_apply(lib: Path, do_copy: bool = True) -> int:
    existing = scan_library(lib)
    found = scan_scatter()
    copied, dup, skipped, errors = [], [], [], []
    for rec in found:
        if rec["status"] != "foreign":
            skipped.append(rec)
            continue
        src = Path(rec["path"])
        try:
            digest = md5(src)
        except OSError as exc:
            errors.append({**rec, "error": str(exc)})
            continue
        if digest in existing:
            dup.append({**rec, "md5": digest, "dupe_of": existing[digest]["path"]})
            continue
        dest_dir = lib / rec["level"] / (rec["year"] if rec["year"] in YEARS else "unknown")
        dest = dest_dir / f"{rec['name']}"
        if dest.exists():
            dest = dest_dir / f"{src.stem}_{digest[:6]}{src.suffix}"
        if do_copy:
            try:
                dest_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dest)
            except OSError as exc:
                errors.append({**rec, "error": f"copy: {exc}"})
                continue
        entry = {**rec, "md5": digest, "library_path": str(dest), "status": "ingested"}
        existing[digest] = entry
        copied.append(entry)
    manifest = {
        "generated": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "library": str(lib),
        "counts": {
            "library_before": len(existing) - len(copied),
            "ingested": len(copied),
            "already_present": len(dup),
            "skipped_non_pdf": len(skipped),
            "errors": len(errors),
            "library_after": len(existing),
        },
        "levels": {
            level: {y: len(list((lib / level / y).glob("*.pdf"))) if (lib / level / y).is_dir() else 0 for y in list(YEARS) + ["unknown"]}
            for level in LEVEL_DIRS
        },
        "entries": sorted(existing.values(), key=lambda r: (r.get("level", ""), r.get("year", ""), r.get("name", ""))),
    }
    out = lib / "_library_manifest.json"
    tmp = out.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, out)
    print(json.dumps(manifest["counts"], ensure_ascii=False, indent=2))
    print("levels:", json.dumps(manifest["levels"], ensure_ascii=False))
    for rec in errors[:10]:
        print("ERROR", rec["name"], rec["error"])
    print(f"manifest -> {out}")
    return 0 if not errors else 1


def cmd_refresh(lib: Path) -> int:
    """Cheap incremental manifest update: files whose path+size+mtime already
    match the manifest are not re-hashed (a network-drive full hash takes ~10 min)."""
    path = lib / "_library_manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {"entries": []}
    known = {}
    for e in manifest.get("entries", []):
        known[e.get("library_path") or e.get("path")] = e
    entries, hashed, reused = [], 0, 0
    for level, year, file, archived in iter_library_pdfs(lib):
        key = str(file)
        stat = file.stat()
        old = known.pop(key, None)
        if old and old.get("bytes") == stat.st_size and old.get("mtime") == stat.st_mtime:
            old["archived"] = archived
            old["library_path"] = key          # keep the schema uniform: every entry
            old["path"] = key                  # (reused or rehashed) carries both keys
            entries.append(old)
            reused += 1
            continue
        entries.append({
            "md5": md5(file), "path": key, "library_path": key, "name": file.name,
            "level": level, "year": year, "bytes": stat.st_size, "mtime": stat.st_mtime,
            "archived": archived,
            "source": old.get("source", "library") if old else "library",
            "status": "archived" if archived else "present",
        })
        hashed += 1
    dropped = len(known)
    levels = {level: {y: sum(1 for e in entries if e.get("level") == level and e.get("year") == y
                                          and not e.get("archived"))
                      for y in list(YEARS) + ["unknown"]} for level in LEVEL_DIRS}
    archived = {level: sum(1 for e in entries if e.get("level") == level and e.get("archived"))
                for level in LEVEL_DIRS}
    manifest.update({
        "generated": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "library": str(lib),
        "counts": {"library_after": len(entries), "rehashed": hashed, "unchanged": reused,
                   "removed_missing": dropped},
        "levels": levels,
        "archive_counts": archived,
        "entries": entries,
    })
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, path)
    print(json.dumps({"rehashed": hashed, "unchanged": reused, "removed_missing": dropped,
                      "total": len(entries), "active_levels": levels,
                      "archived": archived}, ensure_ascii=False))
    return 0


def _referenced_paths() -> set[str]:
    """Library files that published data or the pipeline state actually points at —
    these are never removed by dedupe."""
    protected: set[str] = set()
    targets = [pp.PUBLISHED["verified_kb"], pp.PUBLISHED["consulting_db"], pp.state_file()]
    for target in targets:
        try:
            text = Path(target).read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        blob = text.replace("\\\\", "\\")
        for m in re.finditer(r"[A-Za-z]:[\\/][^\"\n]+\.(?:pdf|hwp)", blob):
            protected.add(m.group(0))
    return protected


def cmd_dedupe(lib: Path, dry: bool = True) -> int:
    """Remove byte-identical copies of a guide (same md5), keeping the copy the KB
    or the pipeline state references, else the active/current/[본교] one."""
    manifest_path = lib / "_library_manifest.json"
    if not manifest_path.is_file():
        print("no manifest — run --apply first")
        return 2
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    entries = [e for e in manifest.get("entries", []) if e.get("md5")]
    protected = _referenced_paths()
    # Group by content AND (school, level): byte-identical files that serve different
    # levels (숭실대 ba vs ma) or different schools must both survive, because the
    # pipeline resolves guides per level.
    groups: dict[tuple, list[dict]] = {}
    for e in entries:
        path = Path(e.get("library_path") or e.get("path", ""))
        if not path.is_file():
            continue
        from guide_watchlist import school_of as _school_of
        key = (e["md5"], _school_of(e.get("name", "")) or e.get("name", ""), e.get("level", ""))
        groups.setdefault(key, []).append(e)

    def rank(e: dict) -> tuple:
        path = str(e.get("library_path") or e.get("path", ""))
        name = e.get("name", "")
        return (0 if path in protected else 1,
                1 if e.get("archived") else 0,
                0 if e.get("year") == CURRENT_YEAR else 1,
                0 if "[본교]" in name else 1,
                0 if "외국인" in name else 1,
                len(name))

    # Guard: never remove the only current-year guide a school/level still relies on
    # (a byte-identical twin filed under an older year must not cost the school its
    # current guide — see 백석대학교 2027-09-28).
    from guide_watchlist import school_of as _school_of
    current_by_school = {( _school_of(e.get("name", "")), e.get("level"))
                         for e in entries if e.get("year") == CURRENT_YEAR}
    current_by_school.discard((None, None))

    removed, kept_groups, bytes_freed, skipped = [], 0, 0, []
    for digest, group in groups.items():
        if len(group) < 2:
            continue
        ordered = sorted(group, key=rank)
        keeper, dupes = ordered[0], ordered[1:]
        kept_groups += 1
        for e in dupes:
            key = (_school_of(e.get("name", "")), e.get("level"))
            keeper_key = (_school_of(keeper.get("name", "")), keeper.get("level"))
            if (e.get("year") == CURRENT_YEAR and key in current_by_school
                    and keeper_key not in current_by_school):
                skipped.append({"kept": str(e.get("library_path") or e.get("path")),
                                "reason": "sole current-year entry for this school/level",
                                "would_remove": str(keeper.get("library_path") or keeper.get("path"))})
                continue
            path = Path(e.get("library_path") or e.get("path", ""))
            removed.append({"removed": str(path), "kept": str(keeper.get("library_path") or keeper.get("path")),
                            "md5": digest, "name": e.get("name"), "bytes": e.get("bytes", 0)})
            bytes_freed += e.get("bytes", 0) or 0
            if not dry:
                try:
                    path.unlink()
                except OSError as exc:
                    removed[-1]["error"] = str(exc)
    print(json.dumps({"action": "would-remove" if dry else "removed",
                      "duplicate_groups": kept_groups, "files_removed": len(removed),
                      "mb_freed": round(bytes_freed / 1e6, 1),
                      "protected_referenced_files": len(protected),
                      "skipped_sole_current_year": len(skipped)}, ensure_ascii=False))
    for rec in skipped:
        print("  SKIP", Path(rec["kept"]).name, "->", rec["reason"])
    for rec in removed[:6]:
        print("  DUP", Path(rec["removed"]).name, "-> keep", Path(rec["kept"]).name)
    if not dry and removed:
        out = pp.REPORT_DIR / "_dedupe_removed.json"
        pp.scaffold()
        out.write_text(json.dumps({"at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
                                   "removed": removed}, ensure_ascii=False, indent=1), encoding="utf-8")
        print("log ->", out)
    return 0


def cmd_curate(lib: Path, current: str = "2027", dry: bool = True) -> int:
    """Keep only the CURRENT year in the active library; move older years into
    `_archive/<year>/<level>/`. Files are moved, never deleted, so a re-parse can
    still reach them (point the parser at the archive folder or move back)."""
    archive = lib / "_archive"
    moved, kept, exists = [], 0, 0
    for level in LEVEL_DIRS:
        folder = lib / level
        if not folder.is_dir():
            continue
        for year_dir in sorted(p for p in folder.iterdir() if p.is_dir()):
            year = year_dir.name
            if year == current:
                kept += len(list(year_dir.glob("*.pdf")))
                continue
            dest_dir = archive / year / level
            for file in sorted(year_dir.glob("*.pdf")):
                dest = dest_dir / file.name
                if dest.exists():
                    exists += 1
                    continue
                if not dry:
                    dest_dir.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(file), str(dest))
                moved.append({"from": str(file), "to": str(dest), "level": level, "year": year})
            if not dry and not any(year_dir.iterdir()):
                year_dir.rmdir()
    print(json.dumps({"action": "would-archive" if dry else "archived",
                      "moved": len(moved), "already_archived": exists,
                      "current_year_kept": kept, "archive": str(archive),
                      "by_level": {lv: sum(1 for m in moved if m["level"] == lv) for lv in LEVEL_DIRS}},
                     ensure_ascii=False))
    for rec in moved[:5]:
        print("  ", rec["from"], "->", rec["to"])
    return 0


def cmd_validate(lib: Path, current: str = "2027") -> int:
    """Open every active current-year PDF and flag unreadable ones (0 pages / corrupt).

    Such a file must never count as a school's current guide: 5 sat in
    ba|ma|junior|lang/2027 with page_count 0 -- empty downloads the collector accepted
    on magic bytes alone -- so the OCR pass reported them as "scanned, no text layer"
    instead of "broken file" (2026-09-29).
    """
    try:
        import pymupdf
    except Exception as exc:
        print(f"validate needs pymupdf: {exc}")
        return 2
    bad, ok = [], 0
    for level, year, path, _archived in iter_library_pdfs(lib):
        if year != current or not path.is_file():
            continue
        reason = ""
        try:
            doc = pymupdf.open(str(path))
            pages = doc.page_count
            if pages > 0:
                # Blank-content guard: a guide whose pages hold no text, no images and no
                # vector drawing carries nothing (두원공과대학교: 4 pages, all empty) and must
                # not count as coverage any more than a 0-page file (2026-09-29).
                content = 0
                for i in range(min(pages, 3)):
                    pg = doc[i]
                    content += len(pg.get_text().strip()) + len(pg.get_images()) + len(pg.get_drawings())
                if content == 0:
                    reason = "blank"
            doc.close()
        except Exception:
            pages, reason = -1, "unreadable"
        if pages <= 0 or reason:
            bad.append({"name": path.name, "level": level, "year": year, "pages": pages,
                        "reason": reason or "zero_pages",
                        "rel": str(path.relative_to(lib)).replace("\\", "/")})
        else:
            ok += 1
    pp.scaffold()
    out = pp.REPORT_DIR / "_invalid_pdfs.json"
    tmp = out.with_suffix(".json.tmp")
    tmp.write_text(json.dumps({"generated": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
                               "current_year": current, "unreadable": bad},
                              ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(tmp, out)
    print(f"validate: readable current-year PDFs={ok} | unusable (0 pages / corrupt / blank)={len(bad)}")
    for b in bad:
        print(f"   [{b['level']}] {b['name']} pages={b['pages']} reason={b.get('reason')}")
    print(f"report -> {out}")
    return 1 if bad else 0


def cmd_verify(lib: Path) -> int:
    path = lib / "_library_manifest.json"
    if not path.is_file():
        print(f"missing manifest: {path}")
        return 2
    manifest = json.loads(path.read_text(encoding="utf-8"))
    def where(e):
        return e.get("library_path") or e.get("path", "")
    missing = [e for e in manifest["entries"] if not Path(where(e)).is_file()]
    print(f"manifest entries={len(manifest['entries'])} missing_on_disk={len(missing)}")
    for e in missing[:10]:
        print("  MISSING", where(e))
    print(f"levels on disk: " + json.dumps({
        level: {y: len(list((lib / level / y).glob("*.pdf"))) if (lib / level / y).is_dir() else 0 for y in list(YEARS) + ["unknown"]}
        for level in LEVEL_DIRS
    }, ensure_ascii=False))
    return 1 if missing else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--report", action="store_true", help="read-only inventory")
    group.add_argument("--apply", action="store_true", help="ingest missing PDFs + write manifest")
    group.add_argument("--verify", action="store_true", help="check manifest vs disk")
    group.add_argument("--refresh", action="store_true", help="cheap incremental manifest update (no full rehash)")
    group.add_argument("--curate", action="store_true", help="archive non-current years (keep only --current active)")
    group.add_argument("--curate-dry", action="store_true", help="show what --curate would archive")
    group.add_argument("--dedupe", action="store_true", help="remove byte-identical duplicate guides")
    group.add_argument("--dedupe-dry", action="store_true", help="show what --dedupe would remove")
    group.add_argument("--validate", action="store_true", help="flag unreadable current-year PDFs (0 pages/corrupt)")
    group.add_argument("--dry-run", action="store_true", help="hash+plan without copying")
    ap.add_argument("--library", default=None, help="override library root")
    ap.add_argument("--current", default="2027", help="current guide year kept active by --curate")
    args = ap.parse_args()
    lib = Path(args.library) if args.library else drive_root() / "guides"
    if not lib.parent.is_dir():
        print(f"library parent unreachable: {lib.parent}")
        return 2
    if args.report:
        return cmd_report(lib)
    if args.validate:
        return cmd_validate(lib, args.current)
    if args.verify:
        return cmd_verify(lib)
    if args.refresh:
        return cmd_refresh(lib)
    if args.curate or args.curate_dry:
        return cmd_curate(lib, args.current, dry=args.curate_dry)
    if args.dedupe or args.dedupe_dry:
        return cmd_dedupe(lib, dry=args.dedupe_dry)
    return cmd_apply(lib, do_copy=args.apply)


if __name__ == "__main__":
    raise SystemExit(main())