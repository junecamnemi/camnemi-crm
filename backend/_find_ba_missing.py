# -*- coding: utf-8 -*-
"""Find admission (ipsi) page URLs for the 19 BA schools still missing ba_url.
Visits each school's main homepage (domain inferred) and locates the 입학/
admission menu link via Playwright. Save _ba_missing_urls.json."""
import json, os, re, datetime

BASE = r"C:\Users\wisew\camnemi-crm\backend"
OUT = os.path.join(BASE, "_ba_missing_urls.json")

# 19 schools -> homepage; use web-search/known domain, fallback to .ac.kr guess
HOMEPAGES = {
    "감리교신학대학교": "https://www.kwtu.ac.kr/",
    "국립공주대학교": "https://www.kongju.ac.kr/",
    "국립창원대학교": "https://www.changwon.ac.kr/",
    "나사렛대학교": "https://www.kornu.ac.kr/",
    "동신대학교": "https://www.dsu.ac.kr/",
    "루터대학교": "https://www.ltu.ac.kr/",
    "명지대학교": "https://www.mju.ac.kr/",
    "부산외국어대학교": "https://www.bufs.ac.kr/",
    "부산장신대학교": "https://www.busanshin.ac.kr/",
    "서울기독대학교": "https://www.kcu.ac.kr/",
    "영남신학대학교": "https://www.ytus.ac.kr/",
    "영산선학대학교": "https://www.ysu.ac.kr/",
    "을지대학교": "https://www.eulji.ac.kr/",
    "이화여자대학교": "https://www.ewha.ac.kr/",
    "장로회신학대학교": "https://www.pcts.ac.kr/",
    "중원대학교": "https://www.jwu.ac.kr/",
    "창신대학교": "https://www.cs.ac.kr/",
    "한국침례신학대학교": "https://www.kbtus.ac.kr/",
    "한양대학교": "https://www.hanyang.ac.kr/",
}

# ipsi link keywords
ADM = re.compile(r"(입학|admission|ipsi|iphak|enter|admis)", re.I)
BAD = re.compile(r"(대학원|graduate|편입|수시|정시)", re.I)

def main():
    from playwright.sync_api import sync_playwright
    result = {}
    today = datetime.date.today().isoformat()
    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome", headless=True)
        ctx = b.new_context(user_agent="Mozilla/5.0")
        pg = ctx.new_page()
        for name, url in HOMEPAGES.items():
            rec = {"homepage": url, "status": "no_ipsi_link", "checked": today}
            try:
                try:
                    pg.goto(url, timeout=18000, wait_until="domcontentloaded")
                except Exception:
                    pg.wait_for_timeout(1500)
                pg.wait_for_timeout(1500)
                links = pg.eval_on_selector_all(
                    "a", "els => els.map(e => ({t:(e.innerText||'').trim(), h:e.href})).filter(x => x.t && x.h)")
                # admission links: title has 입학, not graduate/편입/수시
                cands = [x for x in links if ADM.search(x["t"]) and not BAD.search(x["t"])]
                if not cands:
                    cands = [x for x in links if ADM.search(x["h"]) and not BAD.search(x["h"])]
                if not cands:
                    result[name] = rec; continue
                def score(x):
                    s = 0
                    if re.search(r"(입학|admission)", x["t"], re.I): s += 2
                    if re.search(r"(외국인|유학생|international)", x["t"] + x["h"], re.I): s += 2
                    return s
                best = sorted(cands, key=score, reverse=True)[0]
                rec["ipsi_url"] = best["h"]
                rec["title"] = best["t"][:40]
                rec["status"] = "found"
            except Exception as e:
                rec["status"] = f"error:{type(e).__name__}"
            result[name] = rec
        b.close()
    json.dump(result, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    from collections import Counter
    print("상태:", dict(Counter(v["status"] for v in result.values())))
    for n, v in result.items():
        if v.get("ipsi_url"): print(f"  {n} -> {v['ipsi_url'][:65]}")

if __name__ == "__main__":
    main()