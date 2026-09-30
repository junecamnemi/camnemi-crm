#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Re-discover 전문대 어학연수 guides from each school's CURRENT homepage.

The 8 remaining schools have dead/rotten cached lang URLs, so start at the homepage and walk
the live menu tree (2 hops) toward 한국어교육원/국제교육원/어학연수, take a PDF attachment if
one exists, else render the destination page to A4 PDF (networkidle + scroll + print bg),
verify ≥250 chars, and file it as guides/lang/<year>/<school>_한국어교육원_<year>.pdf.

  python _discover_junior_lang.py --only 강동대학교
Log: backend/_junior_lang_discover_report.jsonl
"""
from __future__ import annotations
import argparse, json, os, re, sys, time
from pathlib import Path
from urllib.parse import urlparse

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pipeline_paths as pp  # noqa: E402
from _retry_htmlonly import live_links, render_strong, pdf_year, page_text  # noqa

REPORT = HERE / "_junior_lang_discover_report.jsonl"
LANGKW = re.compile(r"(한국어|어학|한국어교육원|국제교육원|국제교류|국제처|연수|유학생|외국인|korean|language|international|global)", re.I)
PDFHINT = re.compile(r"\.pdf($|\?|#)", re.I)
DLHINT = re.compile(r"(filedownload|downloadrun|down\.do|filedown|getfile|attach|download\.do|jfile|download)", re.I)
MIN = 250


def langscore(u, t):
    s = 0
    if LANGKW.search(t or ""):
        s += 3
    if LANGKW.search(u):
        s += 2
    if PDFHINT.search(u.lower()):
        s += 2
    if DLHINT.search(u.lower()):
        s += 1
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    idx = json.load(open(HERE / "unvcd_index.json", encoding="utf-8"))["schools"]
    missing = set(json.load(open(HERE / "_junior_lang_missing.json", encoding="utf-8")))
    tg = []
    for cd, v in idx.items():
        if v.get("school_type") != "junior" or v.get("excluded"):
            continue
        if v["name"] not in missing:
            continue
        home = v.get("homepage") or v.get("ipsi_homepage")
        if home:
            tg.append({"school": v["name"], "url": home})
    if args.only:
        tg = [t for t in tg if args.only in t["school"]]
    if args.limit:
        tg = tg[: args.limit]
    print(f"discovery targets: {len(tg)}", flush=True)

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
            school, home = t["school"], t["url"]
            row = {"school": school, "home": home, "status": None, "saved": None,
                   "ts": time.strftime("%Y-%m-%d %H:%M:%S")}
            try:
                data = status = used = None
                links = live_links(page, home)
                dom = urlparse(home).netloc.split(".")[-2:]
                ranked = sorted(((langscore(u, tx), u, tx) for u, tx in links if u), key=lambda x: -x[0])
                cand1 = [u for s, u, tx in ranked[:12]
                         if s >= 2 and urlparse(u).netloc.split(".")[-2:] == dom]
                for cu in cand1[:5]:                     # hop 1: menu page
                    for s, u, tx in sorted(((langscore(x, y), x, y) for x, y in live_links(page, cu)), key=lambda z: -z[0])[:6]:
                        if (PDFHINT.search(u.lower()) or DLHINT.search(u.lower())) and urlparse(u).netloc.split(".")[-2:] in (dom, urlparse(cu).netloc.split(".")[-2:]):
                            try:
                                import requests
                                rr = requests.get(u, headers={"User-Agent": "Mozilla/5.0"}, timeout=40)
                                if rr.status_code < 400 and rr.content[:4] == b"%PDF":
                                    data, status, used = rr.content, "pdf_via_menu", u
                                    break
                            except Exception:
                                pass
                    if data:
                        break
                if not data and cand1:
                    for ru in cand1[:3]:
                        probe = pp.library_root() / "lang" / "2027" / f".{school}.probe.pdf"
                        probe.parent.mkdir(parents=True, exist_ok=True)
                        data, status = render_strong(page, ru, probe)
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
                    row.update(status=status, saved=str(dest), source=used, year=yr)
                    ok += 1
                    print(f"  [{i}/{len(tg)}] OK  {school} -> {dest.name} ({status})", flush=True)
                else:
                    row["status"] = "not_found"
                    row["candidates"] = cand1[:6]
                    fail += 1
                    print(f"  [{i}/{len(tg)}] ---  {school} (candidates={len(cand1)})", flush=True)
            except Exception as e:
                row["status"] = f"error:{type(e).__name__}:{str(e)[:100]}"
                fail += 1
                print(f"  [{i}/{len(tg)}] ERR  {school}: {e}", flush=True)
            with open(REPORT, "a", encoding="utf-8") as f:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
        br.close()
    print(f"\nDONE discovery: ok={ok} fail={fail} of {len(tg)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())