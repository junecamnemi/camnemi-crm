#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Canonical locations for the ONE guide pipeline.

URL → download → parse → analyze → KB/consulting update → DB

ONE PDF library : <shared drive>/.../University_Project/guides/{ba|ma|junior|lang}/{2026|2027}/
ONE data home   : backend/_pipeline_data/{state,parsed,reports,logs}/

Every accumulating artifact lives in the data home. Legacy paths under `backend/`
are kept as NTFS hard links to the same inode so older read-only scripts keep
working; all writers go through this module so nothing drifts.
"""
from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path

BACKEND = Path(__file__).resolve().parent
ROOT = BACKEND.parent

DATA_HOME = BACKEND / "_pipeline_data"
STATE_DIR = DATA_HOME / "state"
PARSED_DIR = DATA_HOME / "parsed"
REPORT_DIR = DATA_HOME / "reports"
LOG_DIR = DATA_HOME / "logs"
BACKUP_DIR = DATA_HOME / "_legacy_backup"
INDEX_FILE = DATA_HOME / "INDEX.json"

DRIVE_CANDIDATES = [
    Path("G:/공유 드라이브/Hermes/Camnemi/02_Crawling_Sheet/University_Project"),
    Path.home() / "내 드라이브" / "02_Crawling_Sheet" / "University_Project",
]

# name -> (canonical path, legacy path in backend/)
ARTIFACTS: dict[str, tuple[Path, Path]] = {
    "state":        (STATE_DIR / "_guide_2027_detected.json", BACKEND / "_guide_2027_detected.json"),
    "parsed":       (PARSED_DIR / "guides_llm_parsed.jsonl", BACKEND / "guides_llm_parsed.jsonl"),
    "parsed_ocr":   (PARSED_DIR / "guides_llm_parsed_ocr.jsonl", BACKEND / "guides_llm_parsed_ocr.jsonl"),
    "parsed_real":  (PARSED_DIR / "guides_llm_parsed_real.jsonl", BACKEND / "guides_llm_parsed_real.jsonl"),
    "gap_report":   (REPORT_DIR / "_kb_gap_report.json", BACKEND / "_kb_gap_report.json"),
    "gap_queue":    (REPORT_DIR / "_kb_gap_queue.json", BACKEND / "_kb_gap_queue.json"),
    "query_gaps":   (REPORT_DIR / "_kb_query_gaps.jsonl", BACKEND / "_kb_query_gaps.jsonl"),
    "pipeline_log": (LOG_DIR / "_guide_kb_pipeline.log", BACKEND / "_guide_kb_pipeline.log"),
    "changes":      (LOG_DIR / "_scrape_changes.jsonl", BACKEND / "_scrape_changes.jsonl"),
    # page-URL collection (ONE collector: guide_page_collect.py) + holdings census
    "page_collect_report":  (REPORT_DIR / "_page_collect_report.jsonl", BACKEND / "_page_collect_report.jsonl"),
    "page_collect_targets": (REPORT_DIR / "_page_collect_targets.json", BACKEND / "_page_collect_targets.json"),
    "guide_census":         (REPORT_DIR / "_guide_census.json", BACKEND / "_guide_census.json"),
}

# Published tables stay where every consumer already reads them; they are listed
# in INDEX.json so the data home is the single place to look up "where is X".
PUBLISHED = {
    "verified_kb": BACKEND / "verified_kb.json",
    "consulting_db": BACKEND / "consulting_db.json",
    "data_js": ROOT / "data.js",
}


def drive_root() -> Path:
    for cand in DRIVE_CANDIDATES:
        if (cand / "guides").is_dir():
            return cand
    return DRIVE_CANDIDATES[0]


def library_root() -> Path:
    return drive_root() / "guides"


def library_manifest() -> Path:
    return library_root() / "_library_manifest.json"


def path(name: str) -> Path:
    """Canonical path for an artifact (falls back to the legacy path if the
    canonical file does not exist yet, so the pipeline still runs pre-migration)."""
    canonical, legacy = ARTIFACTS[name]
    return canonical if canonical.exists() or not legacy.exists() else legacy


def state_file() -> Path:
    return path("state")


def parsed_file() -> Path:
    return path("parsed")


def relink(name: str) -> bool:
    """Re-create the legacy hard link after a writer replaced the canonical file
    (tmp+os.replace breaks a hard link). Returns True when the link is in place."""
    canonical, legacy = ARTIFACTS[name]
    if not canonical.exists():
        return False
    try:
        if legacy.exists() and legacy.stat().st_ino == canonical.stat().st_ino:
            return True
        if legacy.exists():
            legacy.unlink()
        legacy.parent.mkdir(parents=True, exist_ok=True)
        os.link(canonical, legacy)
        return True
    except OSError:
        return False


def scaffold() -> None:
    for folder in (STATE_DIR, PARSED_DIR, REPORT_DIR, LOG_DIR):
        folder.mkdir(parents=True, exist_ok=True)


def _stat(path: Path) -> dict:
    if not path.exists():
        return {"exists": False}
    st = path.stat()
    return {"path": str(path), "exists": True, "bytes": st.st_size,
            "mtime": dt.datetime.fromtimestamp(st.st_mtime).isoformat(timespec="seconds"),
            "inode": st.st_ino, "links": st.st_nlink}


def build_index(extra: dict | None = None) -> dict:
    scaffold()
    index = {
        "generated": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "data_home": str(DATA_HOME),
        "library": str(library_root()),
        "library_manifest": str(library_manifest()),
        "artifacts": {},
        "published": {name: _stat(p) for name, p in PUBLISHED.items()},
    }
    for name, (canonical, legacy) in ARTIFACTS.items():
        entry = {"canonical": _stat(canonical), "legacy": _stat(legacy)}
        entry["linked"] = (
            entry["canonical"].get("inode") is not None
            and entry["canonical"].get("inode") == entry["legacy"].get("inode")
        )
        index["artifacts"][name] = entry
    if library_manifest().is_file():
        try:
            man = json.loads(library_manifest().read_text(encoding="utf-8"))
            index["library_counts"] = man.get("counts")
            index["library_levels"] = man.get("levels")
        except Exception as exc:  # never fail the index on a corrupt manifest
            index["library_error"] = str(exc)
    if extra:
        index.update(extra)
    tmp = INDEX_FILE.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, INDEX_FILE)
    return index


def status() -> dict:
    scaffold()
    index = build_index()
    print("=== CAMNEMI ONE PIPELINE — STATUS ===")
    print(f"library : {index['library']}")
    lc = index.get("library_counts")
    print(f"          manifest counts: {lc if lc else 'NO MANIFEST (run guide_library.py --apply)'}")
    if index.get("library_levels"):
        print(f"          levels: {index['library_levels']}")
    print(f"data    : {index['data_home']}")
    for name, entry in index["artifacts"].items():
        c = entry["canonical"]
        flag = "linked" if entry["linked"] else ("canonical-only" if c["exists"] else "legacy-only")
        size = c.get("bytes", 0) if c["exists"] else entry["legacy"].get("bytes", 0)
        print(f"  {name:<12} {flag:<14} {size:>10,} B")
    print("published tables:")
    for name, entry in index["published"].items():
        print(f"  {name:<14} {'ok' if entry['exists'] else 'MISSING':<7} {entry.get('bytes', 0):>10,} B  {entry.get('path','')}")
    print(f"index   : {INDEX_FILE}")
    return index


if __name__ == "__main__":
    status()