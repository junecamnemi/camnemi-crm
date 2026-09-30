#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Retry pass for HTML-only slots that produced a thin/blank render.

Stronger strategy: render the page in a real browser with networkidle, read the LIVE DOM
anchor list, follow the best guide/모집요강 link (up to 2 hops) for a PDF attachment, and
only then render the final page — screen media, full scroll, print background.
Source of truth for "still failing" = the file on disk, not the earlier report.

  python _retry_htmlonly.py [--limit N] [--level ma]
Log: backend/_htmlonly_retry_report.jsonl
"""
from __future__ import annotations
import argparse, json, os, shutil, sys, time
from pathlib import Path
from urllib.parse import urlparse

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from _collect_htmlonly import KEY, PDFHINT, DLHINT, BAD, UA, BACKUP, page_text, pdf_year, anchors  # noqa

TARGETS = HERE / "_htmlonly_collect_targets.json"
REPORT = HERE / "_htmlonly_retry_report.jsonl"
MIN_CHARS = 250


def needs_retry(dest: Path) -> bool:
    if not dest.exists() or dest.read_bytes()[:4] != b"%PDF":
        return True
    return len(page_text(dest.read_bytes()).strip()) < MIN_CHARS


def live_links(page, url):
    try:
        page.goto(url, timeout=35000, wait_until="domcontentloaded")
        try:
            page.wait_for_load_state("networkidle", timeout=12000)
        except Exception:
            pass
        page.wait_for_timeout(2500)
        return page.eval_on_selector_all(
            "a", "els => els.map(e => [e.href || '', (e.innerText || '').trim().slice(0,80)])")
    except Exception:
        return []


def score(u, t):
    ul = u.lower()
    return 5 * bool(PDFHINT.search(ul)) + 3 * bool(DLHINT.search(ul)) + 2 * bool(KEY.search(t or "")) + bool(KEY.search(ul))


def render_strong(page, url, dest: Path):
    try:
        page.goto(url, timeout=40000, wait_until="domcontentloaded")
        try:
            page.wait_for_load_state("networkidle", timeout=15000)
        except Exception:
            pass
        page.wait_for_timeout(3000)
        for _ in range(3):
            page.mouse.wheel(0, 15000)
            page.wait_for_timeout(900)
        page.emulate_media(media="screen")
        tmp = dest.with_suffix(".retry.pdf")
        page.pdf(path=str(tmp), format="A4", print_background=True, scale=0.9)
        data = tmp.read_bytes()
        tmp.unlink(missing_ok=True)
        if data[:4] != b"%PDF":
            return None, "not_pdf"
        txt = page_text(data)
        if len(txt.strip()) < MIN_CHARS or BAD.search(txt):
            return None, f"thin({len(txt.strip())})"
        return data, "page_render"
    except Exception as e:
        return None, f"err:{type(e).__name__}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--level", default="")
    ap.add_argument("--targets", default="")
    args = ap.parse_args()
    if args.targets:
        tg = json.load(open(args.targets, encoding="utf-8"))
    else:
        tg = json.load(open(TARGETS, encoding="utf-8"))
    if args.level:
        tg = [t for t in tg if t["level"] == args.level]
    todo = [t for t in tg if needs_retry(Path(t["dest"]))]
    if args.limit:
        todo = todo[: args.limit]
    print(f"retry targets: {len(todo)}", flush=True)

    from playwright.sync_api import sync_playwright
    ok = fail = 0
    with sync_playwright() as p:
        br = p.chromium.launch(channel="chrome", headless=True)
        ctx = br.new_context(user_agent=UA["User-Agent"], accept_downloads=True,
                             locale="ko-KR", ignore_https_errors=True, viewport={"width": 1400, "height": 1000})
        page = ctx.new_page()
        page.set_default_timeout(35000)
        for i, t in enumerate(todo, 1):
            school, lv, url, dest = t["school"], t["level"], t["url"], Path(t["dest"])
            row = {"school": school, "level": lv, "url": url, "dest": str(dest), "status": None,
                   "ts": time.strftime("%Y-%m-%d %H:%M:%S")}
            try:
                dest.parent.mkdir(parents=True, exist_ok=True)
                data = status = used = None
                # 1) live DOM link discovery, up to 2 hops, prefer PDF attachments
                pages = [url] if url else []
                visited = set()
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
                                    rr = requests.get(u, headers=UA, timeout=45)
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
                # 2) strong render of the best page (guide link first, else the URL)
                if not data:
                    cands = [u for u, tx in live_links(page, url) if score(u, tx) >= 2
                             and urlparse(u).netloc.split(".")[-2:] == urlparse(url).netloc.split(".")[-2:]]
                    for ru in ([cands[0]] if cands else []) + ([url] if url else []):
                        data, status = render_strong(page, ru, dest)
                        used = ru
                        if data:
                            break
                # 3) local HTML stub
                if not data and t.get("exists_html") and dest.exists():
                    data, status = render_strong(page, "file:///" + str(dest).replace("\\", "/"), dest)
                    used = "local_html_stub"
                if data:
                    if dest.exists() and dest.read_bytes()[:4] != b"%PDF":
                        shutil.copy2(dest, BACKUP / dest.name)
                    dest.write_bytes(data)
                    row.update(status=status, source=used, bytes=len(data), year=pdf_year(data, t.get("year") or "2026"))
                    ok += 1
                    print(f"  [{i}/{len(todo)}] OK  {lv:6s} {school} ({status})", flush=True)
                else:
                    row["status"] = status or "no_source"
                    fail += 1
                    print(f"  [{i}/{len(todo)}] ---  {lv:6s} {school} ({row['status']})", flush=True)
            except Exception as e:
                row["status"] = f"error:{type(e).__name__}:{str(e)[:100]}"
                fail += 1
                print(f"  [{i}/{len(todo)}] ERR  {school}: {e}", flush=True)
            with open(REPORT, "a", encoding="utf-8") as f:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
        br.close()
    print(f"\nDONE retry: ok={ok} fail={fail} of {len(todo)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())