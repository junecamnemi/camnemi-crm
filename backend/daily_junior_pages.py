#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Junior-college foreigner-guide PAGE discovery (not just PDF-download URLs).
Goal (user 2026-09-22): find each school's 모집요강 page/notice URL so that
HTML-only announcements are captured too, not just PDF links.

For each junior college's guide_url (from verified_kb): navigate with Playwright,
locate the page(s) that announce the 외국인/순수외국인 모집요강 (2027 or 2026),
and record the PAGE url (a notice/article/board URL) + any PDF attachment link.

Saves into `_junior_guide_pages.json`:
  {
    "school": {"page_url": "notice/article URL", "pdf_url": "optional PDF",
               "year": "2027|2026|unknown", "title": "notice title",
               "html_only": true_if_no_pdf, "checked": date, "status": ...}
  }
"""
import os, re, json, datetime
from collections import Counter

BASE = r"C:\Users\wisew\camnemi-crm\backend"
UP = r"C:\Users\wisew\내 드라이브\02_Crawling_Sheet\University_Project"
OUT = os.path.join(BASE, "_junior_guide_pages.json")

TITLE_KW = re.compile(r"(외국인|순수외국인|유학생|국제).{0,8}(모집|입학|요강)", re.I)
YEAR_KW = re.compile(r"(20\d\d)")

def load_juniors():
    kb = json.load(open(os.path.join(BASE, "verified_kb.json"), encoding="utf-8"))
    jun = kb.get("junior", {}).get("schools", {})
    return {n: v.get("guide_url", "") for n, v in jun.items()}

def main():
    from playwright.sync_api import sync_playwright
    juniors = load_juniors()
    print(f"전문대 {len(juniors)} | guide_url 보유 {sum(1 for u in juniors.values() if u)}")
    result = {}
    today = datetime.date.today().isoformat()

    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome", headless=True)
        ctx = b.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
                            accept_downloads=True)
        pg = ctx.new_page()
        for name, url in juniors.items():
            if not url or not url.startswith("http"):
                result[name] = {"status": "no_url", "checked": today}
                continue
            rec = {"status": "no_guide_page", "url": url, "checked": today}
            try:
                try:
                    pg.goto(url, timeout=20000, wait_until="domcontentloaded")
                except Exception:
                    pg.wait_for_timeout(2000)
                pg.wait_for_timeout(2000)
                # gather all links (title + href)
                links = pg.eval_on_selector_all(
                    "a", "els => els.map(e => ({t:(e.innerText||'').trim(), h:e.href})).filter(x => x.t && x.h)")
                # candidate notice/article links mentioning foreigner/guide
                cands = [x for x in links if TITLE_KW.search(x["t"]) or re.search(r"(외국인|foreign|international)", x["h"], re.I)]
                if not cands:
                    # broader: any page whose text contains 모집요강 title via hero links
                    cands = [x for x in links if re.search(r"모집|입학|요강", x["t"], re.I)]
                if not cands:
                    rec["title_sample"] = pg.title()[:60]
                    result[name] = rec
                    continue
                # pick the most on-topic (prefer foreigner, then 2027)
                def score(x):
                    s = 0
                    if re.search(r"(외국인|순수외국인|유학생|foreign|international)", x["t"] + x["h"], re.I): s += 3
                    if re.search(r"(2027|2026)", x["t"] + x["h"]): s += 1
                    if ".pdf" in x["h"].lower(): s += 1
                    return s
                best = sorted(cands, key=score, reverse=True)[0]
                rec["page_url"] = best["h"]
                rec["title"] = best["t"][:80]
                m = YEAR_KW.search(best["t"] + best["h"])
                rec["year"] = m.group(1) if m else "unknown"
                rec["pdf_url"] = best["h"] if ".pdf" in best["h"].lower() else None
                rec["html_only"] = rec["pdf_url"] is None
                rec["status"] = "page_found"
            except Exception as e:
                rec["status"] = f"error:{type(e).__name__}"
                rec["err"] = str(e)[:80]
            result[name] = rec
        b.close()

    json.dump(result, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    st = Counter(v["status"] for v in result.values())
    found = sum(1 for v in result.values() if v["status"] == "page_found")
    html_only = sum(1 for v in result.values() if v.get("html_only"))
    pdf = sum(1 for v in result.values() if v.get("pdf_url"))
    print(f"완료: {len(result)} | page_found {found} | 상태 {dict(st)}")
    print(f"  모집요강 페이지 찾음: {found} (이 중 HTML공지만 {html_only}, PDF첨부 {pdf})")

if __name__ == "__main__":
    main()