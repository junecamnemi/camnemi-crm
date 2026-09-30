#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Download pending 2027 foreign-admission PDFs for run_guide_kb_pipeline.py.
The unified orchestrator owns parsing, KB merge, consulting_db/data.js sync, and QC.
"""
import os, re, json, datetime, sys, requests
from pathlib import Path

BASE = os.path.dirname(os.path.abspath(__file__))
_DRIVE_ROOTS = [Path(r"G:/공유 드라이브/Hermes/Camnemi/02_Crawling_Sheet/University_Project"),
                Path.home() / "내 드라이브" / "02_Crawling_Sheet" / "University_Project"]
UP = str(next((p for p in _DRIVE_ROOTS if (p / "guides").is_dir()), _DRIVE_ROOTS[-1]))
sys.path.insert(0, BASE)
import pipeline_paths as _pp  # ONE data home (_pipeline_data/state)
STATE = str(_pp.state_file())

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
           "Accept-Language": "ko-KR,ko;q=0.9"}

def fetch(url, timeout=30):
    response = requests.get(url, headers=HEADERS, timeout=timeout)
    response.raise_for_status()
    return response.content

def main():
    from playwright.sync_api import sync_playwright
    state = json.load(open(STATE, encoding="utf-8"))
    # Retry failures weekly, but do not revisit no-PDF pages on every daily run.
    today = datetime.date.today()
    todo = {}
    for name, item in state.items():
        if item.get("year") != "2027" or item.get("downloaded"):
            continue
        tried = item.get("download_attempted_on")
        if item.get("note") in ("no_pdf_link", "no_foreign_pdf_link", "download_not_pdf", "invalid_pdf_url") and tried:
            try:
                if (today - datetime.date.fromisoformat(tried)).days < 7:
                    continue
            except ValueError:
                pass
        todo[name] = item
    print(f"다운로드 대상(재시도 주기 적용): {len(todo)}교")
    downloaded = 0
    no_foreign_pdf = 0
    errors = 0

    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome", headless=True)
        ctx = b.new_context(user_agent="Mozilla/5.0", accept_downloads=True)
        pg = ctx.new_page()
        for name, v in todo.items():
            url = v.get("page_url", "")
            level = v.get("level", "ba")
            if not url.startswith("http"):
                errors += 1
                continue
            try:
                try:
                    pg.goto(url, timeout=20000, wait_until="domcontentloaded")
                except Exception:
                    pg.wait_for_timeout(1500)
                pg.wait_for_timeout(1500)
                # Select only an explicitly foreign-student guide; never fall back to a
                # generic domestic-admission PDF just because its URL ends in .pdf.
                links = pg.eval_on_selector_all(
                    "a",
                    "els => els.map(e => ({href:e.href, label:(e.innerText||'')+' '+(e.title||'')+' '+(e.getAttribute('aria-label')||'')}))",
                )
                pdfs = [x for x in links if ".pdf" in (x.get("href", "").lower())]
                foreign = [x for x in pdfs if re.search(
                    r"외국인|유학생|international|foreign", x.get("href", "") + " " + x.get("label", ""), re.I)]
                if not foreign:
                    state[name]["note"] = "no_foreign_pdf_link"
                    state[name]["download_attempted_on"] = today.isoformat()
                    no_foreign_pdf += 1
                    continue
                foreign.sort(key=lambda x: ("2027" not in (x.get("href", "") + x.get("label", "")), x.get("href", "")))
                src = foreign[0]["href"]
                if not src.startswith("http"):
                    state[name]["note"] = "invalid_pdf_url"
                    state[name]["download_attempted_on"] = today.isoformat()
                    errors += 1
                    continue
                d = os.path.join(UP, "guides", level, "2027")
                os.makedirs(d, exist_ok=True)
                fname = f"{name}_외국인모집요강_2027.pdf"
                path = os.path.join(d, fname)
                if not os.path.exists(path) or open(path, "rb").read(4) != b"%PDF":
                    try:
                        b2 = fetch(src)
                        if b2[:4] == b"%PDF":
                            with open(path, "wb") as f:
                                f.write(b2)
                        else:
                            with pg.expect_download(timeout=15000) as dl:
                                pg.goto(src, timeout=20000)
                            dl.value.save_as(path)
                    except Exception:
                        with pg.expect_download(timeout=15000) as dl:
                            pg.goto(src, timeout=20000)
                        dl.value.save_as(path)
                if not os.path.isfile(path) or open(path, "rb").read(4) != b"%PDF":
                    try:
                        os.remove(path)
                    except OSError:
                        pass
                    state[name]["note"] = "download_not_pdf"
                    state[name]["download_attempted_on"] = today.isoformat()
                    errors += 1
                    continue
                state[name]["downloaded"] = True
                state[name]["saved"] = path
                state[name]["downloaded_on"] = datetime.date.today().isoformat()
                state[name].pop("note", None)
                downloaded += 1
            except Exception as e:
                state[name]["note"] = f"error:{type(e).__name__}"
                state[name]["download_attempted_on"] = today.isoformat()
                errors += 1
        b.close()

    json.dump(state, open(STATE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"다운로드 완료: {downloaded}교 (실제 PDF 매직바이트 검증 완료)")
    print(f"DOWNLOAD_SUMMARY attempted={len(todo)} downloaded={downloaded} no_foreign_pdf={no_foreign_pdf} errors={errors}")
    # Parsing and KB/consulting_db sync are owned by run_guide_kb_pipeline.py.

if __name__ == "__main__":
    main()
