#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ONE page-URL collector for the Camnemi guide pipeline.

URL → (PDF attachment | rendered page) → verified PDF in the ONE guide library → pipeline state

This is the single management point for every "the guide is a web page, not a downloadable PDF"
case. Earlier ad-hoc collectors (_collect_htmlonly, _retry_htmlonly, _collect_junior_lang*,
_discover_junior_lang ...) are folded in here and archived; do not add new siblings.

Modes
  --build-targets            scan the KB for slots whose guide is NOT a real PDF → targets file
  --targets <json>           collect every {school, level, url, [dest]} in the file
  --repair-html-only         (implies --build-targets) convert those slots in place
  --url-map junior-lang      collect missing 전문대 어학연수 guides from unvcd_index lang URLs
  --url U --school S --level L [--year Y]   collect ONE page

Artifacts (all in the ONE data home)
  report   : _pipeline_data/reports/_page_collect_report.jsonl
  targets  : _pipeline_data/reports/_page_collect_targets.json
  backups  : _pipeline_data/reports/html_backups/
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import sys
from pathlib import Path
from urllib.parse import urljoin, urlparse

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pipeline_paths as pp  # noqa: E402

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
HEADERS = {"User-Agent": UA, "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8"}
PDF_MAGIC, HWP_MAGIC = b"%PDF", b"\xd0\xcf\x11\xe0"
MIN_CHARS = 250

REPORT = pp.REPORT_DIR / "_page_collect_report.jsonl"
TARGETS = pp.REPORT_DIR / "_page_collect_targets.json"
BACKUPS = pp.REPORT_DIR / "html_backups"

# link scoring
GUIDE_KEY = re.compile(r"(모집요강|외국인|유학생|입학안내|입학\s*안내|전형|등록안내|수강신청|수강\s*신청|"
                       r"신청서|안내문|브로슈어|한국어|어학|연수|admission|application|brochure|guide|"
                       r"international|foreign|korean|language)", re.I)
PDF_HINT = re.compile(r"\.pdf($|\?|#)", re.I)
DL_HINT = re.compile(r"(filedownload|downloadrun|down\.do|filedown|getfile|attach|download\.do|jfile|download)", re.I)
# a rendered page must actually be about the guide, not a CMS/placeholder/error screen
GOOD_TEXT = re.compile(r"(한국어|어학연수|한국어교육원|국제교육원|어학당|연수생|유학생|모집요강|등록금|수강료|"
                       r"원서접수|전형|Korean\s*(Language|Course|Program)|Language\s*(Course|Program|Institute)|"
                       r"Admission|International\s*(Office|Student))", re.I)
BAD_TEXT = re.compile(r"(웹표준|Lazy binding|CMS의 장점|페이지를 찾을 수 없|접속이 차단|비정상적인 접근|"
                      r"로그인이 필요|삭제된 게시물|존재하지 않는 페이지|Access Denied|404\s*Not Found)", re.I)

LEVEL_SUFFIX = {"ba": "외국인모집요강", "ma": "외국인모집요강", "junior": "외국인모집요강", "lang": "한국어교육원"}


def log(msg: str) -> None:
    print(msg, flush=True)


def write_row(row: dict) -> None:
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    with REPORT.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def safe(name: str) -> str:
    return re.sub(r'[\\/:*?"<>|\s]+', "_", (name or "school").strip()) or "school"


# ---------------------------------------------------------------- text / file helpers
def page_text(data: bytes) -> str:
    try:
        import pymupdf
        doc = pymupdf.open(stream=data, filetype="pdf")
        text = "".join(doc[i].get_text() for i in range(min(10, doc.page_count)))
        doc.close()
        return text
    except Exception:
        return ""


def is_real_pdf(path: Path) -> bool:
    """Magic-bytes check only: image-only/scanned guides are still real guides."""
    try:
        return path.is_file() and path.read_bytes()[:4] == PDF_MAGIC
    except OSError:
        return False


def file_ok(path: Path, require_good: bool = False) -> bool:
    """Real PDF with extractable text (and, optionally, guide-ish content)."""
    try:
        if not is_real_pdf(path):
            return False
        text = page_text(path.read_bytes()).strip()
    except OSError:
        return False
    if len(text) < MIN_CHARS or BAD_TEXT.search(text):
        return False
    return GOOD_TEXT.search(text) is not None if require_good else True


def pdf_year(data: bytes, fallback: str) -> str:
    text = page_text(data)
    m = re.search(r"(20\d\d)\s*학년도", text)
    if m:
        return m.group(1)
    years = [y for y in re.findall(r"(20\d\d)", text) if y in ("2025", "2026", "2027", "2028")]
    return max(set(years), key=years.count) if years else fallback


def backup(path: Path) -> None:
    if path.is_file() and path.read_bytes()[:4] != PDF_MAGIC:
        BACKUPS.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, BACKUPS / path.name)


# ---------------------------------------------------------------- browser link/PDF discovery
def live_links(page, url: str):
    try:
        page.goto(url, timeout=35000, wait_until="domcontentloaded")
        try:
            page.wait_for_load_state("networkidle", timeout=12000)
        except Exception:
            pass
        page.wait_for_timeout(2200)
        return [(u, t) for u, t in page.eval_on_selector_all(
            "a", "els => els.map(e => [e.href || '', (e.innerText || '').replace(/\\s+/g,' ').trim().slice(0,60)])") if u]
    except Exception:
        return []


def score(u: str, t: str) -> int:
    low = u.lower()
    return (5 * bool(PDF_HINT.search(low)) + 3 * bool(DL_HINT.search(low))
            + 2 * bool(GUIDE_KEY.search(t or "")) + bool(GUIDE_KEY.search(u)))


def pdf_health(data: bytes):
    """(pages, chars, has_images) of a PDF byte string; (0, 0, False) when unreadable."""
    try:
        import pymupdf
        doc = pymupdf.open(stream=data, filetype="pdf")
        pages = doc.page_count
        if pages == 0:
            return 0, 0, False
        text, has_img = "", False
        for i in range(min(pages, 12)):
            text += doc[i].get_text()
            if not has_img and doc[i].get_images(full=True):
                has_img = True
        doc.close()
        return pages, len(text.strip()), has_img
    except Exception:
        return 0, 0, False


def unusable_reason(data: bytes) -> str | None:
    """Why a fetched/rendered PDF must NOT enter the library (None = usable).

    A 0-page file is a truncated write; a text-less file with no images is a blank render.
    A text-less file WITH images is a real scanned guide and is kept (OCR is a separate track).
    `guide_library.py --validate` fails the pipeline on exactly these, so reject them here.
    """
    pages, chars, has_img = pdf_health(data)
    if pages == 0:
        return "zero_pages"
    if chars < MIN_CHARS and not has_img:
        return "blank"
    return None


def fetch_pdf(url: str):
    try:
        import requests
        r = requests.get(url, headers=HEADERS, timeout=45)
        if r.status_code < 400 and r.content[:4] in (PDF_MAGIC, HWP_MAGIC):
            return r.content
    except Exception:
        pass
    return None


def render_strong(page, url: str, level: str):
    """Render a live page to A4 PDF; return (bytes, status) or (None, reason)."""
    try:
        page.goto(url, timeout=40000, wait_until="domcontentloaded")
        try:
            page.wait_for_load_state("networkidle", timeout=15000)
        except Exception:
            pass
        page.wait_for_timeout(2500)
        for _ in range(3):
            page.mouse.wheel(0, 15000)
            page.wait_for_timeout(800)
        page.emulate_media(media="screen")
        tmp = pp.REPORT_DIR / f".render_{safe(urlparse(url).netloc)}.tmp.pdf"
        page.pdf(path=str(tmp), format="A4", print_background=True, scale=0.9)
        data = tmp.read_bytes()
        tmp.unlink(missing_ok=True)
        if data[:4] != PDF_MAGIC:
            return None, "render_not_pdf"
        why = unusable_reason(data)
        if why:
            return None, f"render_{why}"
        text = page_text(data).strip()
        if len(text) < MIN_CHARS:
            return None, f"render_thin({len(text)})"
        if BAD_TEXT.search(text):
            return None, "render_placeholder"
        if not GOOD_TEXT.search(text):
            return None, "render_offtopic"
        return data, "page_render"
    except Exception as exc:
        return None, f"render_err:{type(exc).__name__}"


def collect_one(page, school: str, level: str, url: str, year: str = "2027", dest: Path | None = None):
    """Try, in order: direct PDF → PDF attachment via live DOM (2 hops) → render the best page."""
    tried: list[str] = []
    data = status = used = None
    direct = fetch_pdf(url) if url else None
    if direct and direct[:4] == PDF_MAGIC:
        data, status, used = direct, "pdf_direct", url
    elif direct and direct[:4] == HWP_MAGIC:
        return None, {"school": school, "level": level, "status": "hwp_needs_conversion",
                      "url": url, "tried": tried}

    if not data and url:
        dom = urlparse(url).netloc.split(".")[-2:]
        pages, visited = [url], set()
        for hop in range(2):
            nxt = []
            for pu in pages:
                if pu in visited:
                    continue
                visited.add(pu)
                ranked = sorted(((score(u, t), u, t) for u, t in live_links(page, pu)), key=lambda x: -x[0])
                for s, u, t in ranked[:8]:
                    if s < 3:
                        continue
                    got = fetch_pdf(u)
                    if got and got[:4] == PDF_MAGIC and len(page_text(got).strip()) >= MIN_CHARS:
                        data, status, used = got, "pdf_attachment", u
                        break
                if data:
                    break
                nxt += [u for s, u, t in ranked[:4]
                        if urlparse(u).netloc.split(".")[-2:] == dom and not PDF_HINT.search(u.lower())]
            if data or hop == 1:
                break
            pages = nxt[:5]

    if not data and url:
        ranked = sorted(((score(u, t), u, t) for u, t in live_links(page, url)), key=lambda x: -x[0])
        dom = urlparse(url).netloc.split(".")[-2:]
        cands = [u for s, u, t in ranked if s >= 2 and urlparse(u).netloc.split(".")[-2:] == dom]
        for target in (cands[:3] or []) + [url]:
            data, status = render_strong(page, target, level)
            used = target
            if data:
                break
            tried.append(f"{status}:{target[:80]}")

    if not data:
        return None, {"school": school, "level": level, "status": status or "not_found",
                      "url": url, "tried": tried}
    why = unusable_reason(data)
    if why:
        # Never let a truncated download or blank render into the library; the pipeline's
        # --validate guard fails the whole run on exactly these files.
        return None, {"school": school, "level": level, "status": f"unusable_{why}",
                      "url": url, "dest": str(dest) if dest else None, "tried": tried}

    yr = pdf_year(data, year)
    if dest is None:
        folder = pp.library_root() / level / yr
        folder.mkdir(parents=True, exist_ok=True)
        dest = folder / f"{safe(school)}_{LEVEL_SUFFIX.get(level, '모집요강')}_{yr}.pdf"
    else:
        dest = Path(dest)
        # Never destroy a guide we already hold: an existing real PDF (scanned guides included)
        # is protected. Only HTML stubs / missing files may be replaced.
        if is_real_pdf(dest):
            return None, {"school": school, "level": level, "status": "skipped_real_pdf_present",
                          "url": url, "dest": str(dest), "tried": tried}
        dest.parent.mkdir(parents=True, exist_ok=True)
        yr = pdf_year(data, year)
    backup(dest)
    dest.write_bytes(data)
    back = dest.read_bytes()                     # verify what actually landed on the drive
    why = unusable_reason(back)
    if back[:4] != PDF_MAGIC or why:
        dest.unlink(missing_ok=True)
        return None, {"school": school, "level": level,
                      "status": f"write_unusable_{why or 'not_pdf'}", "url": url,
                      "tried": tried}
    try:
        import guide_fetch
        guide_fetch.register(school, level, yr, used or url, dest)
    except Exception:
        pass
    return dest, {"school": school, "level": level, "status": status, "saved": str(dest),
                  "source": used, "year": yr, "chars": len(page_text(data).strip()),
                  "url": url, "tried": tried}


# ---------------------------------------------------------------- target builders
def kb_sections():
    kb = json.loads((HERE / "verified_kb.json").read_text(encoding="utf-8"))
    return {"ba": kb.get("schools", {}), "ma": kb.get("master", {}).get("schools", {}),
            "junior": kb.get("junior", {}).get("schools", {}),
            "lang": kb.get("lang_programs", {}).get("schools", {})}


def build_html_only_targets() -> list[dict]:
    """Every KB slot whose effective guide file is not a real PDF (HTML stub, HWP or missing)."""
    targets = []
    for level, section in kb_sections().items():
        for school, rec in section.items():
            if not isinstance(rec, dict):
                continue
            # Closed / no-foreigner-track / visa-excluded schools are out of scope: never spend a
            # collection pass on them (신경주대학교 was retried on every build otherwise).
            if rec.get("recommend_exclude") or rec.get("status") in ("closed", "no_foreigner_track"):
                continue
            dest = None
            for field in ("guide_effective_pdf", "guide_pdf"):
                value = rec.get(field)
                if isinstance(value, str) and value.lower().endswith((".pdf", ".hwp")):
                    dest = value
                    break
            # A real PDF is a real PDF — even an image-only scan. Only HTML stubs / missing
            # files / HWP need page collection; never queue a slot we already hold.
            if dest and is_real_pdf(Path(dest)):
                continue
            url = next((rec.get(f) for f in ("guide_url", "guide_page_url", "lang_src")
                        if isinstance(rec.get(f), str) and rec[f].startswith("http")), None)
            if not url and dest and Path(dest).is_file():
                head = Path(dest).read_text(encoding="utf-8", errors="ignore")[:4000]
                m = re.search(r"""https?://[^"'\s>)]+""", head)
                url = m.group(0) if m else None
                if url and not re.match(r"https?://(?!www\.w3\.org)", url):
                    url = None
            targets.append({"school": school, "level": level,
                            "year": rec.get("guide_effective_year") or rec.get("guide_year") or "2026",
                            "url": url, "dest": dest})
    return targets


def junior_lang_targets() -> list[dict]:
    """전문대 어학연수: from the unvcd_index lang URL map, every school without a real guide file."""
    idx = json.loads((HERE / "unvcd_index.json").read_text(encoding="utf-8"))["schools"]
    have = set()
    for folder in (pp.library_root() / "lang").glob("*"):
        for f in folder.glob("*.pdf"):
            if file_ok(f):
                have.add(f.name.split("_")[0])
    out = []
    for rec in idx.values():
        if rec.get("school_type") != "junior" or rec.get("excluded"):
            continue
        url = (rec.get("foreign_links") or {}).get("lang_foreign")
        name = rec.get("name", "")
        if url and name.split("_")[0] not in have:
            out.append({"school": name, "level": "lang", "year": "2027", "url": url, "dest": None})
    return out


def write_targets(targets: list[dict]) -> Path:
    TARGETS.parent.mkdir(parents=True, exist_ok=True)
    TARGETS.write_text(json.dumps(targets, ensure_ascii=False, indent=1), encoding="utf-8")
    return TARGETS


# ---------------------------------------------------------------- runner
def run(targets: list[dict], limit: int = 0) -> tuple[int, int]:
    from playwright.sync_api import sync_playwright
    if limit:
        targets = targets[:limit]
    log(f"[page-collect] targets: {len(targets)}")
    ok = fail = 0
    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel="chrome", headless=True)
        ctx = browser.new_context(user_agent=UA, accept_downloads=True, locale="ko-KR",
                                  ignore_https_errors=True, viewport={"width": 1400, "height": 1000})
        page = ctx.new_page()
        page.set_default_timeout(35000)
        for i, t in enumerate(targets, 1):
            school, level = t["school"], t.get("level", "ba")
            url, dest = t.get("url"), t.get("dest")
            try:
                saved, row = collect_one(page, school, level, url, t.get("year") or "2027",
                                         Path(dest) if dest else None)
                row["ts"] = dt.datetime.now().astimezone().isoformat(timespec="seconds")
                write_row(row)
                if saved:
                    ok += 1
                    log(f"  [{i}/{len(targets)}] OK  {level:6s} {school} -> {Path(row['saved']).name} ({row['status']}, {row['chars']}c)")
                else:
                    fail += 1
                    log(f"  [{i}/{len(targets)}] ---  {level:6s} {school} ({row['status']})")
            except Exception as exc:
                fail += 1
                write_row({"school": school, "level": level, "url": url,
                           "status": f"error:{type(exc).__name__}:{exc}"[:200],
                           "ts": dt.datetime.now().astimezone().isoformat(timespec="seconds")})
                log(f"  [{i}/{len(targets)}] ERR  {school}: {exc}")
        browser.close()
    log(f"[page-collect] DONE ok={ok} fail={fail} of {len(targets)} | report: {REPORT}")
    return ok, fail


def main() -> int:
    pp.scaffold()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--build-targets", action="store_true", help="Scan the KB for non-PDF guide slots")
    ap.add_argument("--targets", help="Targets JSON ({school, level, url, dest})")
    ap.add_argument("--repair-html-only", action="store_true", help="Build targets and convert them in place")
    ap.add_argument("--url-map", choices=["junior-lang"], help="Collect missing 전문대 어학연수 guides")
    ap.add_argument("--url"), ap.add_argument("--school")
    ap.add_argument("--level", default="ba", choices=["ba", "ma", "junior", "lang"])
    ap.add_argument("--year", default="2027")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    targets: list[dict] = []
    if args.url_map == "junior-lang":
        targets = junior_lang_targets()
        log(f"[page-collect] 전문대 어학연수 missing guides: {len(targets)}")
    elif args.repair_html_only:
        targets = build_html_only_targets()
        write_targets(targets)
        log(f"[page-collect] KB slots with a non-PDF guide: {len(targets)} | targets: {TARGETS}")
    elif args.targets:
        targets = json.loads(Path(args.targets).read_text(encoding="utf-8"))
    elif args.build_targets:
        targets = build_html_only_targets()
        write_targets(targets)
        log(f"[page-collect] wrote {len(targets)} targets → {TARGETS}")
        log("[page-collect] build only — nothing collected (use --repair-html-only to convert)")
        return 0
    elif args.url:
        if not args.school:
            log("--url requires --school")
            return 2
        targets = [{"school": args.school, "level": args.level, "url": args.url, "year": args.year, "dest": None}]
    else:
        ap.print_help()
        return 2

    if not targets:
        log("[page-collect] nothing to do")
        return 0
    ok, fail = run(targets, args.limit)
    # A partially-failed batch is a reportable OUTCOME, not a pipeline failure: the per-target
    # status is in _page_collect_report.jsonl. Exiting non-zero here once aborted the whole
    # guide→KB pipeline before parse/merge/sync could run.
    if fail:
        log(f"[page-collect] WARNING {fail} of {len(targets)} targets could not be collected "
            f"(see the report); continuing")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())