#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Strong (live-DOM) collector for 전문대 어학연수 guides — the 78-URL set.

For each junior college lang URL: open it in a real browser, read the LIVE DOM anchor list,
follow the best 모집요강/입학 link (up to 2 hops) for a PDF attachment, else render the best
page to A4 PDF (networkidle + scroll + screen media + print background), verify ≥250 chars of
real text, then file it as guides/lang/<year>/<school>_한국어교육원_<year>.pdf.

  python _collect_junior_lang_strong.py [--limit N] [--only 학교]
Log: backend/_junior_lang_strong_report.jsonl
"""
from __future__ import annotations
import argparse, json, os, sys, time
from pathlib import Path
from urllib.parse import urlparse

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pipeline_paths as pp  # noqa: E402
from _retry_htmlonly import live_links, render_strong, score, pdf_year, page_text, KEY, PDFHINT, DLHINT  # noqa

TARGETS = HERE / "_junior_lang_targets.json"
REPORT = HERE / "_junior_lang_strong_report.jsonl"
MIN = 250


def existing(school: str):
    lib = pp.library_root() / "lang"
    for yr in lib.glob("*"):
        for f in yr.glob(f"{school}_한국어교육원_*.pdf"):
            if f.stat().st_size > 2000 and len(page_text(f.read_bytes()).strip()) >= MIN:
                return f
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--only", default="")
    args = ap.parse_args()
    tg = json.load(open(TARGETS, encoding="utf-8"))
    if args.only:
        tg = [t for t in tg if args.only in t["school"]]
    tg = [t for t in tg if not existing(t["school"])]
    if args.limit:
        tg = tg[: args.limit]
    print(f"strong targets: {len(tg)}", flush=True)

    from playwright.sync_api import sync_playwright
    ok = fail = 0
    with sync_playwright() as p:
        br = p.chromium.launch(channel="chrome", headless=True)
        ctx = br.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
                             accept_downloads=True, locale="ko-KR", ignore_https_errors=True,
                             viewport={"width": 1400, "height": 1000})
        page = ctx.new_page()
        page.set_default_timeout(30000)
        for i, t in enumerate(tg, 1):
            school, url = t["school"], t["url"]
            row = {"school": school, "url": url, "status": None, "saved": None,
                   "ts": time.strftime("%Y-%m-%d %H:%M:%S")}
            try:
                data = status = used = None
                pages, visited = [url], set()
                for hop in range(2):
                    nxt = []
                    for pu in pages:
                        if pu in visited:
                            continue
                        visited.add(pu)
                        links = live_links(page, pu)
                        ranked = sorted(((score(u, tx), u, tx) for u, tx in links if u), key=lambda x: -x[0])
                        for s, u, tx in ranked[:8]:
                            if PDFHINT.search(u.lower()) or DLHINT.search(u.lower()):
                                try:
                                    import requests
                                    rr = requests.get(u, headers={"User-Agent": "Mozilla/5.0"}, timeout=40)
                                    if rr.status_code < 400 and rr.content[:4] == b"%PDF":
                                        data, status, used = rr.content, "pdf_via_live_dom", u
                                        break
                                except Exception:
                                    pass
                        if data:
                            break
                        nxt += [u for s, u, tx in ranked[:4]
                                if urlparse(u).netloc.split(".")[-2:] == urlparse(pu).netloc.split(".")[-2:]
                                and not PDFHINT.search(u.lower())]
                    if data or hop == 1:
                        break
                    pages = nxt[:5]
                if not data:
                    links = live_links(page, url)
                    cands = [u for u, tx in links if score(u, tx) >= 2
                             and urlparse(u).netloc.split(".")[-2:] == urlparse(url).netloc.split(".")[-2:]]
                    for ru in ([cands[0]] if cands else []) + [url]:
                        libdir = pp.library_root() / "lang" / "2027"
                        libdir.mkdir(parents=True, exist_ok=True)
                        tmp_dest = libdir / f".{school}.probe.pdf"
                        data, status = render_strong(page, ru, tmp_dest)
                        used = ru
                        if data:
                            break
                if data:
                    yr = pdf_year(data, "2027")
                    libdir = pp.library_root() / "lang" / yr
                    libdir.mkdir(parents=True, exist_ok=True)
                    dest = libdir / f"{school}_한국어교육원_{yr}.pdf"
                    dest.write_bytes(data)
                    for junk in (pp.library_root() / "lang" / "2027").glob(f".{school}.probe*"):
                        junk.unlink(missing_ok=True)
                    row.update(status=status, saved=str(dest), source=used, year=yr, bytes=len(data))
                    ok += 1
                    print(f"  [{i}/{len(tg)}] OK  {school} -> {dest.name} ({status})", flush=True)
                else:
                    row["status"] = status or "no_source"
                    fail += 1
                    print(f"  [{i}/{len(tg)}] ---  {school} ({row['status']})", flush=True)
            except Exception as e:
                row["status"] = f"error:{type(e).__name__}:{str(e)[:100]}"
                fail += 1
                print(f"  [{i}/{len(tg)}] ERR  {school}: {e}", flush=True)
            with open(REPORT, "a", encoding="utf-8") as f:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
        br.close()
    print(f"\nDONE strong junior-lang: ok={ok} fail={fail} of {len(tg)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())