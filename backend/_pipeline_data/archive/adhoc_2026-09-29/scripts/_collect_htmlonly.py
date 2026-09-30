#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""HTML-only → PDF 모집요강 converter (all 4 levels).

For every KB slot whose guide is not a real PDF:
  1. fetch the known page URL; if it IS a PDF → save it (best case);
  2. else scan the page (and 1 hop into guide/모집요강 notice links) for a PDF attachment → download;
  3. else render the best on-site page to a multi-page A4 PDF (print background), text-verified;
  4. if there is no URL at all, render the saved HTML stub itself (file://).
The original HTML stub is backed up first, then replaced by the real PDF at the SAME
library path so every existing KB reference stays valid.

  python _collect_htmlonly.py [--limit N] [--only 학교] [--level ba|ma|junior|lang]

Log: backend/_htmlonly_collect_report.jsonl
"""
from __future__ import annotations
import argparse, json, os, re, shutil, sys, time
from pathlib import Path
from urllib.parse import urljoin, urlparse

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
      "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8"}
HWP_MAGIC = b"\xd0\xcf\x11\xe0"
KEY = re.compile(r"(모집요강|외국인|유학생|입학안내|입학\s*안내|전형|등록안내|수강신청|수강\s*신청|신청서|안내문|brochure|admission|application|guide|international|foreign)", re.I)
PDFHINT = re.compile(r"\.pdf($|\?|#)", re.I)
DLHINT = re.compile(r"(filedownload|downloadrun|down\.do|filedown|getfile|attach|download\.do|jfile|download)", re.I)
BAD = re.compile(r"(페이지를 찾을 수 없|접속이 차단|로그인이 필요|비정상적인 접근|404\s*Not Found|오류가 발생|서비스 일시|error page|Access Denied)", re.I)

TARGETS = HERE / "_htmlonly_collect_targets.json"
REPORT = HERE / "_htmlonly_collect_report.jsonl"
BACKUP = HERE / "_pipeline_data" / "reports" / "html_backups"


def safe(n): return re.sub(r'[\\/:*?"<>|\s]+', "_", (n or "school").strip()) or "school"


def anchors(html, base):
    out = []
    for m in re.finditer(r"<a\b[^>]*?(?:href|data-href)\s*=\s*[\"']([^\"']+)[\"'][^>]*>(.*?)</a>", html, re.I | re.S):
        href, txt = m.group(1).strip(), re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", m.group(2))).strip()
        if href.lower().startswith(("javascript:", "mailto:", "#")):
            continue
        out.append((urljoin(base, href), txt))
    for m in re.finditer(r"[\"']([^\"']*(?:FileDownload|filedown|download)[^\"']*\.(?:do|php|asp|jsp)[^\"']*)[\"']", html, re.I):
        out.append((urljoin(base, m.group(1)), "download"))
    for m in re.finditer(r"(?:location\.href|window\.open)\s*[= (]\s*[\"']([^\"']+)[\"']", html, re.I):
        out.append((urljoin(base, m.group(1)), ""))
    return out


def rank(cands):
    seen, sc = set(), []
    for u, t in cands:
        ul = u.lower()
        if u in seen:
            continue
        seen.add(u)
        s = 5 * bool(PDFHINT.search(ul)) + 3 * bool(DLHINT.search(ul)) + \
            2 * bool(KEY.search(t or "")) + bool(KEY.search(ul))
        if s:
            sc.append((s, u, t))
    sc.sort(key=lambda x: -x[0])
    return sc


def page_text(data: bytes):
    try:
        import pymupdf
        d = pymupdf.open(stream=data, filetype="pdf")
        t = "".join(d[i].get_text() for i in range(min(8, d.page_count)))
        d.close()
        return t
    except Exception:
        return ""


def pdf_year(data, fallback):
    t = page_text(data)
    m = re.search(r"(20\d\d)\s*학년도", t)
    if m:
        return m.group(1)
    ys = [y for y in re.findall(r"(20\d\d)", t) if y in ("2025", "2026", "2027", "2028")]
    return max(set(ys), key=ys.count) if ys else fallback


def render(page, url, dest: Path, level: str):
    try:
        page.goto(url, timeout=35000, wait_until="domcontentloaded")
        page.wait_for_timeout(2500)
        try:
            page.mouse.wheel(0, 12000)
            page.wait_for_timeout(1200)
        except Exception:
            pass
        tmp = dest.with_suffix(".tmp.pdf")
        page.pdf(path=str(tmp), format="A4", print_background=True)
        data = tmp.read_bytes()
        tmp.unlink(missing_ok=True)
        if data[:4] != b"%PDF":
            return None, "render_not_pdf"
        txt = page_text(data)
        if len(txt.strip()) < 250 or BAD.search(txt):
            return None, f"render_thin({len(txt.strip())})"
        return data, "page_render"
    except Exception as e:
        return None, f"render_err:{type(e).__name__}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--only", default="")
    ap.add_argument("--level", default="")
    args = ap.parse_args()
    tg = json.load(open(TARGETS, encoding="utf-8"))
    if args.only:
        tg = [t for t in tg if args.only in t["school"]]
    if args.level:
        tg = [t for t in tg if t["level"] == args.level]
    if args.limit:
        tg = tg[: args.limit]
    print(f"targets: {len(tg)}", flush=True)

    from playwright.sync_api import sync_playwright
    BACKUP.mkdir(parents=True, exist_ok=True)
    ok = fail = 0
    with sync_playwright() as p:
        br = p.chromium.launch(channel="chrome", headless=True)
        ctx = br.new_context(user_agent=UA["User-Agent"], accept_downloads=True,
                             locale="ko-KR", ignore_https_errors=True)
        page = ctx.new_page()
        page.set_default_timeout(30000)
        for i, t in enumerate(tg, 1):
            school, lv, url, dest = t["school"], t["level"], t["url"], Path(t["dest"])
            row = {"school": school, "level": lv, "url": url, "dest": str(dest),
                   "status": None, "ts": time.strftime("%Y-%m-%d %H:%M:%S")}
            try:
                dest.parent.mkdir(parents=True, exist_ok=True)
                data = status = used = None
                if url:
                    try:
                        import requests
                        r = requests.get(url, headers=UA, timeout=45)
                        if r.status_code < 400 and r.content[:4] in (b"%PDF", HWP_MAGIC):
                            data, status, used = r.content, "pdf_link", url
                        elif r.status_code < 400:
                            html = r.content.decode("utf-8", "ignore")
                            ranked = rank(anchors(html, url))
                            for s, u, txt in ranked[:6]:
                                try:
                                    rr = requests.get(u, headers=UA, timeout=45)
                                    if rr.status_code < 400 and rr.content[:4] == b"%PDF":
                                        data, status, used = rr.content, "pdf_from_page", u
                                        break
                                except Exception:
                                    continue
                            if not data:
                                hops = [u for s, u, txt in ranked
                                        if urlparse(u).netloc.split(".")[-2:] == urlparse(url).netloc.split(".")[-2:]][:3]
                                for h in hops:
                                    try:
                                        r2 = requests.get(h, headers=UA, timeout=45)
                                        for s, u, txt in rank(anchors(r2.text, h))[:3]:
                                            rr = requests.get(u, headers=UA, timeout=45)
                                            if rr.status_code < 400 and rr.content[:4] == b"%PDF":
                                                data, status, used = rr.content, "pdf_deep", u
                                                break
                                    except Exception:
                                        continue
                                    if data:
                                        break
                    except Exception:
                        pass
                    if not data:
                        rurl = url
                        data, status = render(page, rurl, dest, lv)
                        used = rurl
                if not data and f"file:///{str(dest).replace(chr(92), '/')}" and t.get("exists_html"):
                    data, status = render(page, "file:///" + str(dest).replace("\\", "/"), dest, lv)
                    used = "local_html_stub"
                if data:
                    if dest.exists() and dest.read_bytes()[:4] != b"%PDF":
                        shutil.copy2(dest, BACKUP / dest.name)
                    dest.write_bytes(data)
                    row.update(status=status, source=used, bytes=len(data),
                               year=pdf_year(data, t.get("year") or "2026"))
                    ok += 1
                    print(f"  [{i}/{len(tg)}] OK  {lv:6s} {school} -> {dest.name} ({status})", flush=True)
                else:
                    row["status"] = status or "no_source"
                    fail += 1
                    print(f"  [{i}/{len(tg)}] ---  {lv:6s} {school} ({row['status']})", flush=True)
            except Exception as e:
                row["status"] = f"error:{type(e).__name__}:{str(e)[:120]}"
                fail += 1
                print(f"  [{i}/{len(tg)}] ERR  {school}: {e}", flush=True)
            with open(REPORT, "a", encoding="utf-8") as f:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
        br.close()
    print(f"\nDONE html-only: ok={ok} fail={fail} of {len(tg)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())