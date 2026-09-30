#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Phase 2 — from a located 등록금 page, find and download the 일람표 attachment.

Board HTML usually renders the table as an attachment (hwp/hwpx/xlsx/pdf), so the page itself shows
nothing useful — the file is the payload. Handles:
  · direct anchors       href="…/download.do?file=…" / "…fileDown.do…" / "…Download…"
  · onclick JS handlers  javascript:fileDownload('123')  (common in Korean board skins)
  · .xlsx/.hwp/.hwpx/.pdf/.zip targets
  python _fees_crawl.py --list              # what is discoverable right now
  python _fees_crawl.py --download          # fetch candidate attachments into backend/_fees_dl/
Writes _fees_attachments.json
"""
import os, re, json, sys, urllib.request, urllib.parse, urllib.error, concurrent.futures
import html as htmllib   # NOT `html`: the page-source variable shadows the module inside crawl_one

B = os.path.dirname(os.path.abspath(__file__))
DL = os.path.join(B, "_fees_dl")
LOC = os.path.join(B, "_fees_locate.json")
OUT = os.path.join(B, "_fees_attachments.json")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/124.0 Safari/537.36")
EXT = re.compile(r"\.(hwpx?|xlsx?|pdf|zip|csv)$", re.I)
FILEISH = re.compile(r"(download|fileDown|file_down|attach|filedown|atchfile|bbsFile)", re.I)
# the board carries everything; only the 일람표 is the payload. 회의록/브로슈어/인증서 are noise
WANT = re.compile(r"등록금|일람표|수업료|학비")
# an actual table file, whatever else its name says — this wins over NOISE
WANT_TABLE = re.compile(r"일람표|수업료|등록금\s*일람|학과별")
NOISE = re.compile(r"회의록|심의위|브로슈어|brochure|인증서|품질인증|약관|개인정보|동의서|"
                   r"입학전형|모집요강|장학|규정|정관|요람|신문|\bbro\b|_?bro\.pdf|카탈로그|catalog", re.I)


def get(url, timeout=15, binary=False):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "ko,en;q=0.8",
                                               "Referer": url})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read(6_000_000 if binary else 900_000)
        if binary:
            return raw, r.headers.get("Content-Disposition", ""), r.geturl()
        enc = r.headers.get_content_charset() or "utf-8"
        return raw.decode(enc, "replace"), "", r.geturl()


def parse_page(url, html):
    """All candidate attachment URLs on the page."""
    found = []

    def add(u, label=""):
        u = htmllib.unescape(u.strip())          # board URLs arrive as &amp;fileSn=1 → download 404s
        u = urllib.parse.urljoin(url, u)
        if not u.startswith("http"):
            return
        if u in [f["url"] for f in found]:
            return
        blob = u + " " + label
        score = 2 if WANT.search(label) else (1 if WANT.search(urllib.parse.unquote(u)) else 0)
        # 회의록·브로슈어·인증서 only LOOK relevant (their title contains 등록금); a real table file
        # says 일람표/수업료. Reject noise unless it is demonstrably the table.
        if NOISE.search(blob) and not WANT_TABLE.search(blob):
            return
        if score == 0 and label and not (EXT.search(label) or FILEISH.search(u)):
            return
        if score == 0 and not EXT.search(urllib.parse.urlparse(u).path) and not FILEISH.search(u):
            return
        found.append({"url": u, "label": re.sub(r"\s+", " ", label)[:80], "score": score})

    # The anchor TEXT is the filename/제목; the href is usually an opaque download.do token. Without this
# the noise filter had nothing to judge and saved 회의록·브로슈어·인증서.
    for m in re.finditer(r'<a\b[^>]*href="([^"]+)"[^>]*>(.*?)</a>', html, re.S | re.I):
        href = m.group(1)
        text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", m.group(2))).strip()
        if EXT.search(href) or FILEISH.search(href) or EXT.search(text):
            add(href, text)
    for m in re.finditer(r'href="([^"]+\.(?:hwpx?|xlsx?|pdf|zip|csv))"', html, re.I):
        add(m.group(1), m.group(1).split("/")[-1])
    for m in re.finditer(r'href="([^"]*(?:download|fileDown|filedown|attach)[^"]*)"', html, re.I):
        add(m.group(1), m.group(1)[-60:])
    for m in re.finditer(r"""(?:fileDownload|fnFileDown|downFile|fileDown)\s*\(\s*['"]([^'"]+)['"]""",
                         html, re.I):
        token = m.group(1)
        for pat in (f"fileNo={token}", f"file_no={token}", f"fileSn={token}", f"atchFileId={token}"):
            add(url.split("?")[0] + "?" + pat, f"js:{token}")
    found.sort(key=lambda f: -f["score"])
    return found


def crawl_one(school, info):
    """Try each located candidate page, return its attachments."""
    cands = [c for c in info.get("candidates", []) if c.get("status") == 200]
    # prefer pages that already showed fee links, then those with 등록금 in the title
    cands.sort(key=lambda c: (not c.get("fee_links"), "등록금" not in (c.get("title") or "")))
    pages = []
    for c in cands:
        pages.append(c["url"])
        for fl in c.get("fee_links") or []:
            pages.append(urllib.parse.urljoin(c["url"], fl["href"]))
    atts = []
    for p in pages[:4]:
        try:
            html, _, final = get(p)
        except Exception:
            continue
        for a in parse_page(final, html):
            if a["url"] not in [x["url"] for x in atts]:
                a["from_page"] = final
                atts.append(a)
        if len(atts) >= 6:
            break
    return {"school": school, "level": info.get("level"), "domain": info.get("domain"),
            "pages_tried": pages[:4], "attachments": atts}


def main():
    loc = json.load(open(LOC, encoding="utf-8"))
    todo = {k: v for k, v in loc.items()
            if any(c.get("fee_links") for c in v.get("candidates", []))}
    if "--limit" in sys.argv:
        todo = dict(list(todo.items())[:int(sys.argv[sys.argv.index("--limit") + 1])])
    print(f"schools with fee links: {len(todo)}")
    res = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        for r in ex.map(lambda kv: crawl_one(*kv), todo.items()):
            res[r["school"]] = r
            print(f"  {r['school'][:16]:18} pages={len(r['pages_tried'])} attachments={len(r['attachments'])}")
            for a in r["attachments"][:4]:
                print("      ", a["url"][:120])
    json.dump(res, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    if "--download" in sys.argv:
        os.makedirs(DL, exist_ok=True)
        got, rejected = 0, []
        for school, r in res.items():
            d = os.path.join(DL, re.sub(r'[\\/:*?"<>|]', "_", school))
            os.makedirs(d, exist_ok=True)
            for a in r["attachments"]:
                name = os.path.basename(urllib.parse.urlparse(a["url"]).path) or "file"
                if not EXT.search(name):
                    name += ".bin"
                try:
                    raw, disp, _ = get(a["url"], binary=True)
                    # the board serves the REAL filename in Content-Disposition; the anchor label was
                    # often empty (JS-driven links), so judge the served name here, after the fact.
                    if m := re.search(r'filename="?([^";]+)', disp or ""):
                        name = urllib.parse.unquote(m.group(1))
                    blob = name + " " + (a.get("label") or "")
                    if NOISE.search(blob) and not WANT_TABLE.search(blob):
                        rejected.append(name)
                        continue
                    if len(raw) < 20_000:          # HTML error page dressed as a file
                        rejected.append(name + f" (too small {len(raw)}B)")
                        continue
                    p = os.path.join(d, name[:120])
                    open(p, "wb").write(raw)
                    got += 1
                    print(f"    saved {len(raw):>9,}B {os.path.basename(p)[:70]}")
                except Exception as e:
                    print(f"    dl-fail {type(e).__name__} {a['url'][:80]}")
        print(f"downloaded {got} | rejected as noise/short: {len(rejected)}")
        for n in rejected[:10]:
            print("    reject:", n[:70])
    print("WROTE", OUT)


if __name__ == "__main__":
    main()