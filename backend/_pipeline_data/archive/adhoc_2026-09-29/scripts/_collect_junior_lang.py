#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Batch-collect 전문대 어학연수(한국어교육원) guides for junior colleges that already
have a knowledge-base lang URL but no guide file in the library.

  python _collect_junior_lang.py [--limit N] [--only "학교명"] [--workers 1]

Reads  backend/_junior_lang_targets.json   (school, url, ...)
Writes library  guides/lang/<year>/<school>_한국어교육원_<year>.pdf
Logs    backend/_junior_lang_collect_report.jsonl  (one row per school, appended live)
"""
from __future__ import annotations
import argparse, json, os, re, sys, time
from pathlib import Path
from urllib.parse import urljoin, urlparse

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pipeline_paths as pp  # noqa: E402

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
      "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8"}
HWP_MAGIC = b"\xd0\xcf\x11\xe0"
KEY = re.compile(r"(모집요강|입학안내|입학\s*안내|등록안내|수강신청|수강\s*신청|신청서|안내문|브로슈어|admission|application|guide|brochure|kurs|course|수강료|학사일정|연수생)", re.I)
PDFHINT = re.compile(r"\.pdf($|\?|#)", re.I)
DLHINT = re.compile(r"(filedownload|downloadrun|down\.do|filedown|getfile|attach|download\.do|jfile|download)", re.I)
REPORT = HERE / "_junior_lang_collect_report.jsonl"
TARGETS = HERE / "_junior_lang_targets.json"


def safe(n: str) -> str:
    return re.sub(r'[\\/:*?"<>|\s]+', "_", (n or "school").strip()) or "school"


def get_html(page_or_url, url, timeout=25000) -> str:
    """requests first, then playwright page (if given a page)."""
    try:
        import requests
        r = requests.get(url, headers=UA, timeout=timeout / 1000)
        if r.status_code < 400 and len(r.content) > 400:
            r.encoding = r.apparent_encoding or r.encoding
            return r.text
    except Exception:
        pass
    if page_or_url is not None:
        try:
            page_or_url.goto(url, timeout=timeout, wait_until="domcontentloaded")
            page_or_url.wait_for_timeout(1200)
            return page_or_url.content()
        except Exception:
            return ""
    return ""


def anchors(html: str, base: str):
    out = []
    for m in re.finditer(r"<a\b[^>]*?(?:href|data-href)\s*=\s*[\"']([^\"']+)[\"'][^>]*>(.*?)</a>", html, re.I | re.S):
        href, txt = m.group(1).strip(), re.sub(r"<[^>]+>", " ", m.group(2))
        txt = re.sub(r"\s+", " ", txt).strip()
        if href.lower().startswith(("javascript:", "mailto:", "#")):
            continue
        out.append((urljoin(base, href), txt))
    for m in re.finditer(r"(?:location\.href|window\.open)\s*[=(]\s*[\"']([^\"']+)[\"']", html, re.I):
        out.append((urljoin(base, m.group(1)), ""))
    for m in re.finditer(r"[\"']([^\"']*(?:FileDownload|filedown|download)[^\"']*\.(?:do|php|asp|jsp)[^\"']*)[\"']", html, re.I):
        out.append((urljoin(base, m.group(1)), "download"))
    return out


def pick(cands):
    """rank candidates: pdf first, then keyword hits."""
    seen, scored = set(), []
    for u, t in cands:
        ul = u.lower()
        if u in seen:
            continue
        seen.add(u)
        s = 0
        if PDFHINT.search(ul):
            s += 5
        if DLHINT.search(ul):
            s += 3
        if KEY.search(t or ""):
            s += 2
        if KEY.search(ul):
            s += 1
        if s:
            scored.append((s, u, t))
    scored.sort(key=lambda x: -x[0])
    return scored


def render_page(page, url: str, dest_dir: Path, school: str):
    """Render a live page to PDF; keep only if it carries real text."""
    try:
        page.goto(url, timeout=30000, wait_until="domcontentloaded")
        page.wait_for_timeout(2500)
        tmp = dest_dir / f".render_{safe(school)}.tmp.pdf"
        page.pdf(path=str(tmp), format="A4", print_background=True)
        data = tmp.read_bytes()
        tmp.unlink(missing_ok=True)
        if data[:4] != b"%PDF":
            return None
        import fitz
        d = fitz.open(stream=data, filetype="pdf")
        txt = "".join(d[i].get_text() for i in range(min(6, d.page_count)))
        d.close()
        if len(txt.strip()) < 250:
            return None
        yr = pdf_year(data)
        out = dest_dir / f"{safe(school)}_한국어교육원_{yr}_캡처.pdf"
        out.write_bytes(data)
        return out
    except Exception:
        return None


def pdf_year(data: bytes, fallback="2027") -> str:
    try:
        import fitz
        d = fitz.open(stream=data, filetype="pdf")
        txt = "".join(d[i].get_text() for i in range(min(4, d.page_count)))
        d.close()
        m = re.search(r"(20\d\d)\s*학년도", txt)
        if m:
            return m.group(1)
        yrs = re.findall(r"(20\d\d)", txt)
        if yrs:
            c = max(set(yrs), key=yrs.count)
            if c in ("2025", "2026", "2027", "2028"):
                return c
    except Exception:
        pass
    return fallback


def try_download(page, url, dest_dir: Path, school: str, tag: str):
    """download url; return saved Path if it is a real PDF/HWP."""
    data = None
    try:
        import requests
        r = requests.get(url, headers=UA, timeout=40)
        if r.status_code < 400:
            data = r.content
    except Exception:
        pass
    if (not data or data[:4] not in (b"%PDF", HWP_MAGIC)) and page is not None:
        try:
            with page.expect_download(timeout=20000) as dl:
                page.goto(url, timeout=25000, wait_until="domcontentloaded")
            p = dest_dir / f".dl_{safe(school)}_{tag}.tmp"
            dl.value.save_as(str(p))
            data = p.read_bytes()
            p.unlink(missing_ok=True)
        except Exception:
            pass
    if not data:
        return None, "no_data"
    if data[:4] == b"%PDF":
        yr = pdf_year(data)
        out = dest_dir / f"{safe(school)}_한국어교육원_{yr}.pdf"
        if out.exists() and out.stat().st_size > 1000:
            out = dest_dir / f"{safe(school)}_한국어교육원_{yr}_{abs(hash(url)) % 9973}.pdf"
        out.write_bytes(data)
        return out, "pdf"
    if data[:4] == HWP_MAGIC:
        out = dest_dir / f"{safe(school)}_한국어교육원_unknown.hwp"
        out.write_bytes(data)
        return out, "hwp"
    return None, "not_pdf"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--only", default="")
    args = ap.parse_args()

    targets = json.load(open(TARGETS, encoding="utf-8"))
    if args.only:
        targets = [t for t in targets if args.only in t["school"]]
    if args.limit:
        targets = targets[: args.limit]
    print(f"targets: {len(targets)}", flush=True)

    from playwright.sync_api import sync_playwright
    lib = pp.library_root()
    ok = hwp = fail = 0
    rows = []
    with sync_playwright() as p:
        br = p.chromium.launch(channel="chrome", headless=True)
        ctx = br.new_context(user_agent=UA["User-Agent"], accept_downloads=True,
                             locale="ko-KR", ignore_https_errors=True)
        page = ctx.new_page()
        page.set_default_timeout(25000)
        for i, t in enumerate(targets, 1):
            school, url = t["school"], t["url"]
            row = {"school": school, "url": url, "status": None, "saved": None,
                   "candidate": None, "ts": time.strftime("%Y-%m-%d %H:%M:%S")}
            try:
                data = None
                try:
                    import requests
                    r = requests.get(url, headers=UA, timeout=40)
                    if r.status_code < 400:
                        data = r.content
                except Exception:
                    pass
                if data and data[:4] in (b"%PDF", HWP_MAGIC):
                    saved, tag = try_download(page, url, lib / "lang" / "2027", school, "direct")
                    row.update(status=tag, saved=str(saved) if saved else None, candidate=url)
                    ok += tag == "pdf"
                    hwp += tag == "hwp"
                    print(f"  [{i}/{len(targets)}] OK  {school} (direct file) -> {saved.name if saved else None}", flush=True)
                    rows.append(row)
                    with open(REPORT, "a", encoding="utf-8") as f:
                        f.write(json.dumps(row, ensure_ascii=False) + "\n")
                    continue
                html = data.decode("utf-8", "ignore") if data else ""
                if len(html) < 400:
                    html = get_html(page, url)
                cands = anchors(html, url)
                ranked = pick(cands)
                saved = tag = None
                used = None
                for s, u, txt in ranked[:6]:
                    saved, tag = try_download(page, u, lib / "lang" / "2027", school, f"c{ranked.index((s,u,txt))}")
                    if saved:
                        used = u
                        break
                # one hop into same-site keyword pages if nothing yet
                if not saved:
                    hops = [u for s, u, txt in ranked if not PDFHINT.search(u.lower())
                            and urlparse(u).netloc.split(".")[-2:] == urlparse(url).netloc.split(".")[-2:]][:4]
                    for h in hops:
                        h2 = get_html(page, h)
                        r2 = pick(anchors(h2, h))
                        for s, u, txt in r2[:4]:
                            saved, tag = try_download(page, u, lib / "lang" / "2027", school, "h1")
                            if saved:
                                used = u
                                break
                        if saved:
                            break
                # last resort: render the best on-site page to PDF (many 전문대 어학원 publish
                # the admissions info as a page, not a downloadable file)
                if not saved:
                    render_url = url
                    cand_pages = [u for s, u, txt in ranked
                                  if urlparse(u).netloc.split(".")[-2:] == urlparse(url).netloc.split(".")[-2:]]
                    if cand_pages:
                        render_url = cand_pages[0]
                    saved = render_page(page, render_url, lib / "lang" / "2027", school)
                    if saved:
                        tag = "page_render"
                        used = render_url
                if saved:
                    row.update(status=tag, saved=str(saved), candidate=used)
                    ok += tag == "pdf"
                    hwp += tag == "hwp"
                    print(f"  [{i}/{len(targets)}] OK  {school} -> {saved.name}", flush=True)
                else:
                    row["status"] = f"no_pdf ({len(cands)} anchors)"
                    fail += 1
                    print(f"  [{i}/{len(targets)}] ---  {school} ({len(cands)} anchors, {len(ranked)} scored)", flush=True)
            except Exception as e:
                row["status"] = f"error: {type(e).__name__}: {e}"[:200]
                fail += 1
                print(f"  [{i}/{len(targets)}] ERR  {school}: {e}", flush=True)
            rows.append(row)
            with open(REPORT, "a", encoding="utf-8") as f:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
        br.close()
    print(f"\nDONE  pdf={ok} hwp={hwp} fail={fail} of {len(targets)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())