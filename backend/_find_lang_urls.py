# -*- coding: utf-8 -*-
"""Find Korean-language-institute (한국어교육원) URLs for the 29 lang schools
missing guide_url. For each: visit the school homepage, find international/
language-institute link. Save into _lang_url_backfill.json."""
import os, re, json, datetime

BASE = r"C:\Users\USER\camnemi-crm\backend"
OUT = os.path.join(BASE, "_lang_url_backfill.json")

HOMEPAGES = {  # 29 schools -> guess homepage (school domain)
    "강남대": "https://www.kangnam.ac.kr/",
    "경동대": "https://www.kduniv.ac.kr/",
    "김포대학교": "https://www.kimpo.ac.kr/",
    "대림대학교": "https://www.daelim.ac.kr/",
    "동남보건대학교": "https://www.dongnam.ac.kr/",
    "동아방송예술대학교": "https://www.dima.ac.kr/",
    "동양미래대학교": "https://www.dongyang.ac.kr/",
    "동원대학교": "https://www.tw.ac.kr/",
    "명지전문대학": "https://www.mjc.ac.kr/",
    "배화여자대학교": "https://www.baewha.ac.kr/",
    "부천대학교": "https://www.bc.ac.kr/",
    "삼육보건대학교": "https://www.shu.ac.kr/",
    "서울장신대": "https://www.sjpc.ac.kr/",
    "서정대학교": "https://www.seojeong.ac.kr/",
    "숭의여자대학교": "https://www.sewu.ac.kr/",
    "신경주대": "https://www.sgu.ac.kr/",
    "신구대학교": "https://www.singu.ac.kr/",
    "안양대": "https://www.anyang.ac.kr/",
    "용인예술과학대학교": "https://www.ysc.ac.kr/",
    "우송정보대학": "https://www.wsi.ac.kr/",
    "인덕대학교": "https://www.induk.ac.kr/",
    "청운대": "https://www.chungwoon.ac.kr/",
    "충청대학교": "https://www.ok.ac.kr/",
    "한양여자대학교": "https://www.hywoman.ac.kr/",
    "한일장신대": "https://www.hanil.ac.kr/",
    "경인여자대학교": "https://www.kiwu.ac.kr/",
    "재능대학교": "https://www.jeiu.ac.kr/",
    "경복대": "https://www.kbu.ac.kr/",
    "서일대학교": "https://www.seoil.ac.kr/",
}

KW = re.compile(r"(어학|한국어|international|foreign|global|교류|language|klc|klec|klli|korean)", re.I)

def main():
    from playwright.sync_api import sync_playwright
    result = {}
    today = datetime.date.today().isoformat()
    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome", headless=True)
        ctx = b.new_context(user_agent="Mozilla/5.0")
        pg = ctx.new_page()
        for name, url in HOMEPAGES.items():
            rec = {"status": "no_link", "homepage": url, "checked": today}
            try:
                try:
                    pg.goto(url, timeout=20000, wait_until="domcontentloaded")
                except Exception:
                    pg.wait_for_timeout(2000)
                pg.wait_for_timeout(2000)
                links = pg.eval_on_selector_all(
                    "a", "els => els.map(e => ({t:(e.innerText||'').trim(), h:e.href})).filter(x => x.t && x.h)")
                cands = [x for x in links if KW.search(x["t"]) and not x["h"].startswith("javascript")]
                # prefer ones that also mention 어학/한국어
                def s(x):
                    t = x["t"] + x["h"]
                    sc = 0
                    if re.search(r"어학|한국어교육|language institute|KLI", t, re.I): sc += 3
                    if re.search(r"외국인|international|교류", t, re.I): sc += 1
                    return sc
                cands.sort(key=s, reverse=True)
                if cands and s(cands[0]) > 0:
                    best = cands[0]
                    rec["lang_url"] = best["h"]
                    rec["title"] = best["t"][:50]
                    rec["status"] = "found"
            except Exception as e:
                rec["status"] = f"error:{type(e).__name__}"
            result[name] = rec
        b.close()
    json.dump(result, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    from collections import Counter
    st = Counter(v["status"] for v in result.values())
    found = sum(1 for v in result.values() if v.get("lang_url"))
    print(f"완료: {len(result)} | 찾음 {found} | 상태 {dict(st)}")

if __name__ == "__main__":
    main()