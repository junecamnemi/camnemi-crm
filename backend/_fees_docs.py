#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Find and download the 등록금 DOCUMENTS for schools whose fee info is inside a file, not HTML.

For each target: Naver search → visit official pages on the school's own domain → collect links to
pdf/hwp/hwpx/jpg/png whose anchor text, URL, or containing page mentions 등록금/수업료/학비/일람표 →
download into backend/_fees_docs/<school>/.

Then a PDF with a text layer is parsed deterministically (pymupdf); only image-only files go to
vision. That split keeps the expensive model out of the easy cases.
  python _fees_docs.py --limit 5
Writes _fees_docs.json
"""
import os, re, json, sys, urllib.parse, urllib.request
from playwright.sync_api import sync_playwright

B = os.path.dirname(os.path.abspath(__file__))
TBD = os.path.join(B, "tuition_by_department.json")
OUT = os.path.join(B, "_fees_docs.json")
DL = os.path.join(B, "_fees_docs")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/124.0 Safari/537.36")
DOC = re.compile(r"\.(pdf|hwpx?|xlsx?|jpe?g|png)$", re.I)
WANT = re.compile(r"등록금|수업료|학비|일람표")
NOISE = re.compile(r"회의록|심의위|브로슈어|brochure|인증서|품질인증|약관|개인정보|동의서|"
                   r"입학원서|모집요강|장학|규정|정관|요람|신문|카탈로그|catalog|배치도|안내문\(별\)",
                   re.I)
# UI chrome flooded the first run: logos, board icons, menu/search buttons, sns glyphs
ASSET = re.compile(r"logo|icon|btn_|_btn|btn-|header|banner|_ic\b|\bic_|arrow|menu|search|sns|"
                   r"kakao|insta|facebook|youtube|naver|spinner|loading|bg_|pattern|favicon|"
                   r"thumb|blank|dot\.|line\.|bullet", re.I)

LINKS_JS = """(() => {
  const out = [];
  for (const a of document.querySelectorAll('a[href]')) {
    const t = (a.innerText||'').replace(/\\s+/g,' ').trim().slice(0,90);
    out.push([t, a.href]);
  }
  for (const im of document.querySelectorAll('img[src]')) {
    out.push(['<img>', im.src]);
  }
  return out;
})()"""


def token(name):
    n = re.sub(r"\(.*?\)|\[.*?\]", "", name)
    return re.sub(r"(대학교|대학|학교|캠퍼스|본교|분교|성신교정)$", "", n.strip()).strip()


def own(href, tok):
    m = re.search(r"https?://([^/]+)", href or "")
    if not m:
        return False
    h = m.group(1).lower()
    if re.search(r"naver|google|youtube|daum|facebook|instagram|wikipedia|adiga|academyinfo|"
                 r"uni-?moa|junkang|blog|cafe|kin\.|tistory|tistory", h):
        return False
    return h.endswith(".kr") or ".ac.kr" in h


def get(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Referer": url})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read(12_000_000), r.headers.get("Content-Disposition", "")


def work(page, school, level):
    res = {"school": school, "level": level, "docs": [], "pages": [], "errors": []}
    tok = token(school)
    try:
        q = urllib.parse.quote(f"{school} 등록금 일람표")
        page.goto(f"https://search.naver.com/search.naver?query={q}", timeout=45000)
        page.wait_for_timeout(2200)
        hits = page.eval_on_selector_all("a[href^='http']",
                                         "els=>els.map(e=>[e.innerText.trim().slice(0,70), e.href])")
    except Exception as e:
        res["errors"].append(f"search:{type(e).__name__}")
        return res
    cands = []
    for text, href in hits:
        if not own(href, tok):
            continue
        sc = 2 if WANT.search(text + href) else 0
        cands.append((sc, href))
    cands.sort(key=lambda x: -x[0])
    seen = set()
    pages = []
    for _, h in cands:
        if h in seen:
            continue
        seen.add(h)
        pages.append(h)
        if len(pages) >= 4:
            break
    for p in pages:
        try:
            page.goto(p, timeout=40000, wait_until="domcontentloaded")
            page.wait_for_timeout(1500)
            title = page.title()
            body = page.inner_text("body")[:6000]
            page_hint = bool(WANT.search(title + " " + body))
            for text, href in page.evaluate(LINKS_JS):
                if not href or not href.startswith("http"):
                    continue
                if not own(href, tok):
                    continue
                if not DOC.search(urllib.parse.urlparse(href).path or href):
                    continue
                blob = f"{text} {href}"
                if NOISE.search(blob) and not WANT.search(text):
                    continue
                if ASSET.search(os.path.basename(urllib.parse.urlparse(href).path)):
                    continue
                if not (WANT.search(blob) or (page_hint and re.search(r"등록금|수업료", title + body))):
                    continue
                if href not in [d["url"] for d in res["docs"]]:
                    res["docs"].append({"url": href, "label": text[:80], "from_page": p,
                                        "page_title": title[:80]})
            res["pages"].append({"url": p, "title": title[:80], "등록금": page_hint})
        except Exception as e:
            res["errors"].append(f"{type(e).__name__}:{p[:40]}")
    return res


def main():
    doc = json.load(open(TBD, encoding="utf-8"))
    pending = [(n, lv) for n, lvs in doc["schools"].items() for lv, e in lvs.items()
               if isinstance(e, dict) and not e.get("rows")]
    prev = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else {}
    todo = [p for p in pending if f"{p[0]}|{p[1]}" not in prev]
    if "--limit" in sys.argv:
        todo = todo[:int(sys.argv[sys.argv.index("--limit") + 1])]
    print(f"pending={len(pending)} done={len(prev)} this run={len(todo)}")
    os.makedirs(DL, exist_ok=True)
    with sync_playwright() as p:
        br = p.chromium.launch(headless=True)
        ctx = br.new_context(locale="ko-KR", user_agent=UA)
        page = ctx.new_page()
        for school, level in todo:
            r = work(page, school, level)
            key = f"{school}|{level}"
            got = 0
            d = os.path.join(DL, re.sub(r'[\\/:*?"<>|]', "_", key))
            for dd in r["docs"][:6]:
                try:
                    raw, disp = get(dd["url"])
                except Exception as e:
                    dd["dl_error"] = type(e).__name__
                    continue
                name = os.path.basename(urllib.parse.urlparse(dd["url"]).path) or "file"
                if m := re.search(r'filename="?([^";]+)', disp or ""):
                    name = urllib.parse.unquote(m.group(1))
                if not DOC.search(name):
                    ext = re.search(r"\.(pdf|hwpx?|xlsx?|jpe?g|png)", dd["url"], re.I)
                    name += ext.group(0) if ext else ".bin"
                os.makedirs(d, exist_ok=True)
                fp = os.path.join(d, name[:110])
                open(fp, "wb").write(raw)
                dd["path"] = fp
                dd["bytes"] = len(raw)
                got += 1
            r["downloaded"] = got
            prev[key] = r
            print(f"  {'✔' if got else '·'} {school[:15]:17}[{level:7}] pages={len(r['pages'])} "
                  f"docs={len(r['docs'])} downloaded={got}")
            json.dump(prev, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        br.close()
    print("WROTE", OUT)


if __name__ == "__main__":
    main()