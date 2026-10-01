#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Single, checked pipeline: guide detection/download -> parse -> KB -> consulting DB/data.js."""
from __future__ import annotations
import argparse
import datetime as dt
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

BACKEND = Path(__file__).resolve().parent
ROOT = BACKEND.parent
sys.path.insert(0, str(BACKEND))
import pipeline_paths as pp  # ONE data home (_pipeline_data) + ONE guide library

STATE = Path(pp.state_file())
KB = BACKEND / "verified_kb.json"
CDB = BACKEND / "consulting_db.json"
LOG = pp.LOG_DIR / "_guide_kb_pipeline.log"
LOCK = pp.DATA_HOME / ".guide_kb_pipeline.lock"


def _log(text: str) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"[{stamp}] {text}\n")


def _run(label: str, args: list[str], timeout: int, fatal: bool = True) -> str:
    cmd = [sys.executable, *args]
    _log(f"START {label}: {cmd!r}")
    try:
        result = subprocess.run(
            cmd, cwd=str(BACKEND), capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=timeout,
        )
    except Exception as exc:
        _log(f"FAIL {label}: {type(exc).__name__}: {exc}")
        raise
    output = (result.stdout or "") + ("\n" + result.stderr if result.stderr else "")
    _log(f"END {label}: rc={result.returncode}\n{output}")
    if result.returncode and fatal:
        raise RuntimeError(f"{label} failed (exit {result.returncode})\n{output[-5000:]}")
    if result.returncode:
        # Collection stages report per-school outcomes (some slots are simply not collectable);
        # never abort the pipeline before parse→merge→sync for that.
        print(f"\n--- {label}: rc={result.returncode} (non-fatal) ---")
        return output
    print(f"\n--- {label}: complete ---")
    print("Detailed subprocess output is in the pipeline log.")
    return output


def _load_counts() -> tuple[dict, dict, dict]:
    kb = json.loads(KB.read_text(encoding="utf-8"))
    cdb = json.loads(CDB.read_text(encoding="utf-8"))
    state = json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else {}
    return kb, cdb, state


def _acquire_lock() -> None:
    # ONE shared lock across every university-data entry point (this pipeline, the direct
    # collectors, the canonical publisher): a second runner must be refused instead of
    # interleaving writes into verified_kb.json / consulting_db.json / the guide library.
    # Raises SystemExit(9) when another run holds it.
    try:
        from univ_data_lock import acquire as _acquire_shared
    except ImportError:
        print("WARN: univ_data_lock unavailable; running without the shared university-data lock")
    else:
        _acquire_shared()
    payload = json.dumps({"pid": os.getpid(), "started": dt.datetime.now().astimezone().isoformat()})
    for attempt in range(2):
        try:
            with LOCK.open("x", encoding="utf-8") as f:
                f.write(payload)
            return
        except FileExistsError:
            age = time.time() - LOCK.stat().st_mtime
            if age < 6 * 3600:
                raise RuntimeError(f"Pipeline lock already exists ({LOCK}); another run may be active")
            LOCK.unlink()
            _log("Removed stale pipeline lock older than 6h")
    raise RuntimeError(f"Could not acquire pipeline lock: {LOCK}")


def _release_lock() -> None:
    try:
        LOCK.unlink()
    except FileNotFoundError:
        pass
    try:
        from univ_data_lock import release as _release_shared
    except ImportError:
        pass
    else:
        _release_shared()


def _preflight() -> list[str]:
    problems = []
    required = ["daily_2027_detect.py", "daily_2027_download.py", "parse_unparsed_pro.py",
                "_merge_llm_into_kb.py", "_apply_2027_downloads.py", "_apply_new_lang_guides.py",
                "sync_3layer.py", "coverage_guard.py",
                "guide_page_collect.py", "guide_census.py"]
    for name in required:
        if not (BACKEND / name).is_file():
            problems.append(f"missing script: {BACKEND / name}")
    for name in ("verified_kb.json", "consulting_db.json", "_guide_2027_detected.json"):
        path = BACKEND / name
        if name != "_guide_2027_detected.json" and not path.is_file():
            problems.append(f"missing data: {path}")
        elif path.is_file():
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except Exception as exc:
                problems.append(f"invalid JSON {path}: {exc}")
    drive_roots = [Path(r"G:/공유 드라이브/Hermes/Camnemi/02_Crawling_Sheet/University_Project"),
                   Path.home() / "내 드라이브" / "02_Crawling_Sheet" / "University_Project"]
    drive = next((p for p in drive_roots if (p / "guides").is_dir()), drive_roots[-1])
    if not (drive / "guides").is_dir():
        problems.append(f"guide corpus unavailable: {drive}")
    try:
        import playwright.sync_api  # noqa: F401
    except Exception as exc:
        problems.append(f"Playwright unavailable in {sys.executable}: {exc}")
    try:
        import pymupdf  # noqa: F401
    except Exception as exc:
        problems.append(f"PyMuPDF unavailable in {sys.executable}: {exc}")
    auth_candidates = [Path.home() / "AppData" / "Local" / "hermes" / "shared" / "nous_auth.json",
                       Path.home() / "AppData" / "Local" / "hermes" / "auth.json"]
    if not any(p.is_file() for p in auth_candidates):
        problems.append("Nous inference auth file not found")
    return problems


def _counts() -> tuple[int, int, int]:
    kb, cdb, state = _load_counts()
    downloaded = 0
    for item in state.values():
        saved = item.get("saved", "")
        if not item.get("downloaded") or not saved or not os.path.isfile(saved):
            continue
        try:
            with open(saved, "rb") as f:
                downloaded += int(f.read(4) == b"%PDF")
        except OSError:
            continue
    return len(kb.get("schools", {})), len(cdb.get("schools", {})), downloaded


def _stale_download_count() -> int:
    _, _, state = _load_counts()
    marked = sum(1 for item in state.values() if item.get("downloaded"))
    return marked - _counts()[2]


def _repair_detection_state() -> tuple[int, int]:
    """Correct legacy false year labels and requeue downloaded records with missing files."""
    if not STATE.exists():
        return 0, 0
    state = json.loads(STATE.read_text(encoding="utf-8"))
    relabeled = 0
    requeued = 0
    for item in state.values():
        # The detector only creates records when the page contains 2027 + admission keywords.
        if item.get("year") != "2027":
            item["year"] = "2027"
            relabeled += 1
        if item.get("downloaded"):
            saved = item.get("saved", "")
            valid = False
            if saved and os.path.isfile(saved):
                try:
                    with open(saved, "rb") as f:
                        valid = f.read(4) == b"%PDF"
                except OSError:
                    valid = False
            if not valid:
                item["downloaded"] = False
                item.pop("saved", None)
                item.pop("downloaded_on", None)
                item.pop("download_attempted_on", None)
                item["note"] = "stale_saved_path_requeued"
                requeued += 1
    if relabeled or requeued:
        backup = STATE.with_name(f"{STATE.stem}_bak_repair_{dt.datetime.now():%Y%m%d_%H%M%S}{STATE.suffix}")
        backup.write_text(json.dumps(json.loads(STATE.read_text(encoding="utf-8")), ensure_ascii=False, indent=2), encoding="utf-8")
        temp = STATE.with_suffix(".json.tmp")
        temp.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(temp, STATE)
        pp.relink("state")
    return relabeled, requeued


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true", help="Read-only dependency/data preflight")
    ap.add_argument("--sync-only", action="store_true", help="Skip detection/download/parsing; apply saved guides and sync KB/DB")
    ap.add_argument("--status", action="store_true", help="Show the one-library / one-data-home dashboard and exit")
    ap.add_argument("--ingest-library", action="store_true", help="Consolidate every scattered PDF into the single guide library first")
    ap.add_argument("--curate", action="store_true", help="Archive non-current guide years in the library (current stays active)")
    ap.add_argument("--current", default="2027", help="Current guide year (working set)")
    ap.add_argument("--url", help="Ad-hoc: fetch ONE 모집요강 from this URL and run it through parse→KB→consulting→DB")
    ap.add_argument("--school", help="School name for --url (canonical adiga key preferred)")
    ap.add_argument("--level", default="ba", choices=["ba", "ma", "junior", "lang"], help="Level for --url / --ingest-library")
    ap.add_argument("--year", default="2027", help="Guide year for --url")
    # --- page-URL collection lives in ONE module (guide_page_collect.py); these are the switches ---
    ap.add_argument("--repair-html-only", action="store_true",
                    help="Convert every KB slot whose guide is a web page (not a real PDF) into a PDF")
    ap.add_argument("--collect-junior-lang", action="store_true",
                    help="Collect missing 전문대 어학연수 guides from the unvcd_index lang URL map")
    ap.add_argument("--collect-targets", help="Collect from an explicit targets JSON ({school, level, url, dest})")
    # --- the direct school-URL collectors (previously the separate 06:00 'Camnemi 모집요강
    # 데일리 체크' job) run inside THIS pipeline so a guide collected at night is parsed and
    # merged in the same pass instead of waiting ~22h for the next 04:00 run. ---
    ap.add_argument("--collect-direct", action="store_true",
                    help="Run the direct school-URL collectors (BA/MA/lang scraper + homepage 2027 check + junior direct) first")
    # --- the canonical → Supabase publish tail (previously the separate 08:00 'Camnemi 데이터
    # 파이프라인' job) runs at the END of this pipeline, on the KB this run just refreshed. ---
    ap.add_argument("--publish-canonical", action="store_true",
                    help="Publish the tail: build/enrich/validate canonical → Supabase + KB/consulting DB")
    ap.add_argument("--census", action="store_true", help="Print the 모집요강 보유현황 census (real guides only) and exit")
    args = ap.parse_args()

    print(f"Guide→KB pipeline | {dt.datetime.now().astimezone():%Y-%m-%d %H:%M:%S %Z}")
    if args.census:
        out = _run("모집요강 보유현황 census (real guides only)",
                   [str(BACKEND / "guide_census.py")], timeout=1800)
        for line in (out or "").splitlines():
            if "MuPDF" in line or line.startswith("START ") or line.startswith("END "):
                continue
            print(line)
        pp.build_index()
        return 0
    if args.status:
        pp.status()
        return 0
    if args.url and not args.school:
        print("--url requires --school <name>")
        return 2
    problems = _preflight()
    if problems:
        print("PREFLIGHT FAILED:")
        for problem in problems:
            print(" -", problem)
        return 2
    kb_before, db_before, downloaded_before = _counts()
    stale_downloads = _stale_download_count()
    print(f"Preflight OK | KB BA schools={kb_before} | consulting DB schools={db_before} | valid downloaded PDFs={downloaded_before} | stale saved paths={stale_downloads}")
    if args.check:
        print("CHECK ONLY: no files or network state changed.")
        return 0

    _acquire_lock()
    started = time.monotonic()
    parsed_count = 0
    detected_output = ""
    download_output = ""
    publish_outputs: list[tuple[str, str]] = []
    try:
        if args.curate:
            _run("Curate the guide library (keep only the current year active)",
                 [str(BACKEND / "guide_library.py"), "--curate", "--current", args.current], timeout=7200)
        if args.ingest_library:
            _run("Consolidate all scattered 모집요강 PDFs into the single library",
                 [str(BACKEND / "guide_library.py"), "--apply"], timeout=7200)
        # Direct school-URL collection (BA/MA/lang scraper + homepage 2027 check + junior
        # direct). Previously a separate 06:00 cron; running it HERE means everything it
        # downloads is parsed and merged into the KB in this same pass. Non-fatal: some
        # schools simply have no collectable guide and must not abort the night's run.
        if args.collect_direct:
            for label, script, timeout in (
                ("Collect BA/MA/lang guides directly from school URLs", "daily_guide_scraper.py", 3600),
                ("Detect 2027 notices on school homepages", "daily_homepage_2027_check.py", 3600),
                ("Collect 전문대 foreign guides directly from school URLs", "daily_junior_direct.py", 3600),
            ):
                _run(label, [str(BACKEND / script)], timeout=timeout, fatal=False)
        # Page-URL collection: the ONE collector module (guide_page_collect.py). Runs before the
        # parse stage so anything collected here is parsed in the same run.
        if args.repair_html_only:
            _run("Convert KB slots whose guide is a web page into real PDFs",
                 [str(BACKEND / "guide_page_collect.py"), "--repair-html-only"], timeout=21600, fatal=False)
        if args.collect_junior_lang:
            _run("Collect missing 전문대 어학연수 guides from the lang URL map",
                 [str(BACKEND / "guide_page_collect.py"), "--url-map", "junior-lang"], timeout=21600, fatal=False)
        if args.collect_targets:
            _run(f"Collect guides from {args.collect_targets}",
                 [str(BACKEND / "guide_page_collect.py"), "--targets", args.collect_targets], timeout=21600, fatal=False)
        if not args.sync_only:
            relabeled, requeued = _repair_detection_state()
            if relabeled or requeued:
                note = f"Repaired legacy state: relabeled {relabeled} years, requeued {requeued} missing/non-PDF downloads"
                print(note)
                _log(note)
            if args.url:
                fetch = _run(f"Fetch guide for {args.school} from explicit URL",
                             [str(BACKEND / "guide_fetch.py"), "--url", args.url,
                              "--school", args.school, "--level", args.level, "--year", args.year],
                             timeout=900)
                if '"ok": true' not in fetch:
                    print("\nPIPELINE STOPPED: explicit URL did not yield a valid PDF")
                    print(fetch.strip()[-800:])
                    return 3
            else:
                detected_output = _run("Detect new 2027 foreign-admission notices",
                                       [str(BACKEND / "daily_2027_detect.py")], timeout=3600)
            # Do not stop on [SILENT]: prior detected notices may still be waiting to download.
            download_output = "" if args.url else _run("Download pending 2027 guides (verify %PDF)",
                                                       [str(BACKEND / "daily_2027_download.py")], timeout=3600)
            # Supabase 2027 guide rows (was the tail of the separate 06:00 job): runs after
            # detection/download so the rows reflect this run's collected guides. Non-fatal.
            _run("Upsert 2027 guide rows → Supabase university_guides",
                 [str(BACKEND / "upsert_2027_guides.py")], timeout=1800, fatal=False)
            # Parse every unparsed CURRENT-YEAR guide in the library, not just the ones this
            # run downloaded: a collected-but-unparsed 2027 guide otherwise keeps serving 2026
            # facts forever (121 files were in that state on 2026-09-28).
            parse_output = _run("Parse unparsed current-year guides with DeepSeek Pro",
                                [str(BACKEND / "parse_unparsed_pro.py")], timeout=21600)
            match = re.search(r"완료:\s*(\d+)/(\d+)\s*파싱", parse_output)
            parsed_count = int(match.group(1)) if match else 0
            if parsed_count:
                _run("Merge verified guide facts into KB (fill-only + year upgrade)",
                     [str(BACKEND / "_merge_llm_into_kb.py"), "--write", "--upgrade-years"], timeout=3600)

        _run("Refresh the single guide-library manifest (incremental)",
             [str(BACKEND / "guide_library.py"), "--refresh"], timeout=3600)
        # Broken file guard: a 0-page/corrupt PDF must never count as a school's current
        # guide, or it looks covered while nothing can be parsed from it. Feeds the
        # watch list (_invalid_pdfs.json) and is report-only here.
        # fatal=False: a single bad PDF must NOT fail the whole run — the guard already
        # records it in _invalid_pdfs.json + stdout; the operator quarantines it explicitly.
        _run("Validate current-year PDFs (0-page/corrupt guard)",
             [str(BACKEND / "guide_library.py"), "--validate"], timeout=1800, fatal=False)
        # Reference integrity: if a guide was moved/renamed, KB + published tables must be
        # repointed or the links silently rot. Report-only here; the fix is explicit.
        refs = _run("Guide reference integrity check (KB + published tables)",
                    [str(BACKEND / "repoint_guide_paths.py"), "--quiet"], timeout=1800, fatal=False)
        refs_pub = _run("Guide reference integrity check (consulting_db + data.js)",
                        [str(BACKEND / "repoint_published.py")], timeout=1800, fatal=False)
        for label, out in (("KB", refs), ("published", refs_pub)):
            m = re.search(r'"repointed":\s*(\d+)', out) or re.search(r'"repointable":\s*(\d+)', out)
            if m and int(m.group(1)):
                print(f"WARNING: {m.group(1)} {label} guide refs need repointing — run "
                      f"repoint_guide_paths.py --apply / repoint_published.py --apply")
        _run("Resolve effective guide year per school (current year, else newest held)",
             [str(BACKEND / "guide_resolve.py"), "--apply"], timeout=1800)
        _run("Apply verified 2027 guide file/page links to KB",
             [str(BACKEND / "_apply_2027_downloads.py")], timeout=900)
        # Newly collected language-course guides whose school is not in the KB yet are
        # dropped by the fill-only merger, so the row has to be created before the sync.
        _run("Create KB rows for newly collected 어학연수 guides (additive, evidence-gated)",
             [str(BACKEND / "_apply_new_lang_guides.py"), "--write"], timeout=1800)
        _run("Sync verified_kb → consulting_db → data.js",
             [str(BACKEND / "sync_3layer.py")], timeout=3600)
        _run("3-layer coverage regression guard",
             [str(BACKEND / "coverage_guard.py")], timeout=900)
        watch_output = _run("Current-year guide watch list (2026-only schools stay watched)",
                            [str(BACKEND / "guide_watchlist.py"), "--year", args.current], timeout=1800)
        pp.build_index()

        # Publish tail (was the separate 08:00 'Camnemi 데이터 파이프라인' job). Canonical is
        # rebuilt from the KB/consulting DB THIS run just refreshed, validated, then published
        # to Supabase and merged back into the KB. Non-fatal by design: a publish hiccup must
        # never discard the night's collection/parse work — each stage is reported below.
        if args.publish_canonical:
            for label, script, timeout in (
                ("Build canonical 정본 (schools.jsonl)", "build_canonical.py", 3600),
                ("Enrich canonical", "enrich_canonical.py", 3600),
                ("Validate canonical (publish gate)", "validate_canonical.py", 1800),
                ("Publish canonical → Supabase universities.programs", "publish_all.py", 3600),
                ("Publish canonical → verified_kb + consulting_db", "publish_kb.py", 1800),
            ):
                publish_outputs.append((label, _run(label, [str(BACKEND / script)],
                                                    timeout=timeout, fatal=False)))

        kb_after, db_after, downloaded_after = _counts()
        elapsed = int(time.monotonic() - started)
        detected_n = len(re.findall(r"^\s*\[[^]]+\]\s+.+?\s+->", detected_output, re.M))
        new_download_n = no_foreign_pdf = download_errors = 0
        stats = re.search(r"DOWNLOAD_SUMMARY attempted=(\d+) downloaded=(\d+) no_foreign_pdf=(\d+) errors=(\d+)", download_output)
        if stats:
            new_download_n = int(stats.group(2))
            no_foreign_pdf = int(stats.group(3))
            download_errors = int(stats.group(4))
        print("\nPIPELINE VERIFIED")
        print(f"Newly detected: {detected_n} | New valid PDFs: {new_download_n} | New guide parses: {parsed_count}")
        print(f"Collection exceptions: no foreign PDF link={no_foreign_pdf} | other errors={download_errors}")
        print(f"Downloaded guide records: {downloaded_before} → {downloaded_after}")
        print(f"KB BA schools: {kb_before} → {kb_after} | consulting DB schools: {db_before} → {db_after}")
        watch = re.search(r"\[KB universe\] current=(\d+) \| watch=(\d+) \| needs_url=(\d+) \| no_guide=(\d+)",
                          watch_output)
        if watch:
            cur, watching, needs_url, no_guide = (int(x) for x in watch.groups())
            print(f"Guide year {args.current}: current={cur} | watched(older-only)={watching} | "
                  f"needs_url={needs_url} | no_guide={no_guide}")
        print(f"Coverage guard: PASS | Elapsed: {elapsed}s | Log: {LOG}")
        if publish_outputs:
            print("PUBLISH TAIL (canonical → Supabase + KB):")
            for label, out in publish_outputs:
                tail = [ln for ln in (out or "").splitlines() if ln.strip()][-2:]
                print(f"  · {label}: " + (" | ".join(tail) if tail else "no output"))
        _log(f"PIPELINE VERIFIED detected={detected_n} downloaded={new_download_n} parsed={parsed_count} kb_ba={kb_before}->{kb_after} consulting_schools={db_before}->{db_after} elapsed={elapsed}s")
        return 0
    except Exception as exc:
        print(f"\nPIPELINE FAILED: {exc}")
        _log(f"PIPELINE FAILED: {type(exc).__name__}: {exc}")
        return 1
    finally:
        _release_lock()


if __name__ == "__main__":
    raise SystemExit(main())
