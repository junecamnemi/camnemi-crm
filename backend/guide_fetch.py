#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fetch ONE 모집요강 (guide) from a URL into the single library and register it
in the pipeline state, so `run_guide_kb_pipeline.py --url ...` can carry it all
the way to the KB.

  python guide_fetch.py --url <URL> --school 가천대학교 --level ba --year 2027

Result is printed as one JSON line: {"ok":bool,"saved":path,"bytes":n,"magic":"%PDF"|"HWP"|...}
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
from pathlib import Path
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pipeline_paths as pp  # noqa: E402

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
      "Accept-Language": "ko-KR,ko;q=0.9"}

HWP_MAGIC = b"\xd0\xcf\x11\xe0"


def safe(name: str) -> str:
    return re.sub(r'[\\/:*?"<>|\s]+', "_", (name or "school").strip()) or "school"


def target_path(level: str, year: str, school: str, ext: str = ".pdf") -> Path:
    folder = pp.library_root() / (level if level in ("ba", "ma", "junior", "lang") else "ba") / year
    folder.mkdir(parents=True, exist_ok=True)
    return folder / f"{safe(school)}_외국인모집요강_{year}{ext}"


def try_requests(url: str) -> bytes | None:
    try:
        import requests
    except Exception:
        return None
    try:
        r = requests.get(url, headers=UA, timeout=60)
        r.raise_for_status()
        return r.content
    except Exception:
        return None


def try_playwright(url: str, dest: Path) -> bytes | None:
    try:
        from playwright.sync_api import sync_playwright
    except Exception:
        return None
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(channel="chrome", headless=True)
            ctx = b.new_context(user_agent="Mozilla/5.0", accept_downloads=True)
            pg = ctx.new_page()
            try:
                with pg.expect_download(timeout=25000) as dl:
                    pg.goto(url, timeout=30000, wait_until="domcontentloaded")
                dl.value.save_as(str(dest))
            except Exception:
                resp = pg.goto(url, timeout=30000, wait_until="domcontentloaded")
                if resp is not None:
                    body = resp.body()
                    b.close()
                    return body
            b.close()
        return dest.read_bytes() if dest.is_file() else None
    except Exception:
        return None


def register(school: str, level: str, year: str, page_url: str, saved: Path, note: str | None = None) -> None:
    state_path = Path(pp.state_file())
    state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.is_file() else {}
    entry = state.get(school, {})
    entry.update({
        "level": level, "year": year, "page_url": page_url,
        "downloaded": True, "saved": str(saved),
        "downloaded_on": dt.date.today().isoformat(), "source": "manual_url",
    })
    if note:
        entry["note"] = note
    else:
        entry.pop("note", None)
    state[school] = entry
    tmp = state_path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, state_path)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--school", required=True)
    ap.add_argument("--level", default="ba", choices=["ba", "ma", "junior", "lang"])
    ap.add_argument("--year", default="2027")
    ap.add_argument("--no-register", action="store_true", help="download only, do not touch state")
    args = ap.parse_args()

    dest = target_path(args.level, args.year, args.school)
    data = try_requests(args.url)
    if not data:
        data = try_playwright(args.url, dest)
    result = {"ok": False, "school": args.school, "level": args.level, "year": args.year,
              "url": args.url, "saved": str(dest)}
    if not data:
        result["error"] = "fetch_failed (requests + playwright)"
        print(json.dumps(result, ensure_ascii=False))
        return 1
    magic = data[:4]
    if magic == b"%PDF":
        dest.write_bytes(data)
        result.update(ok=True, magic="%PDF", bytes=len(data))
        if not args.no_register:
            register(args.school, args.level, args.year, args.url, dest)
    elif magic == HWP_MAGIC:
        hwp = dest.with_suffix(".hwp")
        hwp.write_bytes(data)
        result.update(ok=False, magic="HWP", bytes=len(data), saved=str(hwp),
                      error="HWP attachment — convert with hwp5html then render to PDF")
        state_note = "downloaded_hwp_needs_conversion"
        if not args.no_register:
            register(args.school, args.level, args.year, args.url, hwp, note=state_note)
    else:
        html = dest.with_suffix(".bin")
        html.write_bytes(data[:2 << 20])
        result.update(ok=False, magic=magic.hex(), bytes=len(data), saved=str(html),
                      error="not a PDF (page/HTML or redirect)")
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())