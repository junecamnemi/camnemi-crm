#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""fees finding v2 — seed from the KB's OWN source URLs, not guessed domains.

Why v1 failed: it guessed fees.<domain> and read only 5 KB keys. The records actually carry the
등록금 page URL (tuition_source), the 입학처 page (apply_source), the guide page (guide_page_url),
and many homepages are JS-rendered (0 static 등록금 mentions), so a site search is needed.

For every target with no per-college rows yet:
  1. collect every http(s) URL in the KB record (priority: tuition_source → guide_page_url →
     apply_source → source → any other string field)
  2. walk those pages (+1 level into links whose text/path says 등록금/일람표/수업료/재무/입학)
  3. download candidate attachments (hwp/hwpx/xlsx/pdf), keeping only 일람표-shaped files
     (served Content-Disposition name decides), into backend/_fees_dl2/<school>/
Writes _fees_v2_found.json  ·  python _fees_v2.py [--limit N] [--download]
"""
import os, re, json, sys, time, urllib.request, urllib.parse, urllib.error, concurrent.futures
import html as htmllib

B = os.path.dirname(os.path.abspath(__file__))
DL = os.path.join(B, "_fees_dl2")
OUT = os.path.join(B, "_fees_v2_found.json")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/124.0 Safari/537.36")
EXT = re.compile(r"\.(hwpx?|xlsx?|pdf|zip)$", re.I)
FILEISH = re.compile(r"(download|fileDown|file_down|attach|filedown|atchfile|bbsFile|Down)", re.I)
WANT_TABLE = re.compile(r"일람표|수업료|등록금\s*일람|학과별|학비|등록금")
NOISE = re.compile(r"회의록|심의위|브로슈어|brochure|인증서|품질인증|약관|개인정보|동의서|"
                   r"입학전형|모집요강|장학|규정|정관|요람|신문|\bbro\b|카탈로그|catalog|"
                   r"결산|예산|감사|채용|입찰|공고문\(일반\)", re.I)
SEED_KEYS = ("tuition_source", "guide_page_url", "apply_source", "source", "guide_url",
             "guide_year_source", "scholarship_source", "ieqas_source", "_student_source")


def load_kb():
    import importlib.util
    spec = importlib.util.spec_from_file_location("tpf", os.path.join(B, "_tuition_pro_fill.py"))
    tpf = importlib.util.module_from_spec(spec)
    argv = sys.argv[:]; sys.argv = ["x"]
    try:
        spec.loader.exec_module(tpf)
    except SystemExit:
        pass
    sys.argv = argv
    return tpf.load_kb()


def get(url, timeout=15, binary=False):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "ko,en;q=0.8",
                                               "Referer": url})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read(8_000_000 if binary else 900_000)
        if binary:
            return raw, r.headers.get("Content-Disposition", ""), r.geturl()
        enc = r.headers.get_content_charset() or "utf-8"
        return raw.decode(enc, "replace"), "", r.geturl()


def urls_in(rec):
    """Every http(s) URL the KB record holds, in priority order."""
    found = []
    def push(v):
        if isinstance(v, str):
            for m in re.finditer(r"https?://[^\s\"'<>)]+", v):
                if m.group(0) not in found:
                    found.append(m.group(0))
        elif isinstance(v, list):
            for x in v:
                push(x)
        elif isinstance(v, dict):
            for x in v.values():
                push(x)
    for k in SEED_KEYS:
        push(rec.get(k))
    for k, v in rec.items():
        if k not in SEED_KEYS:
            push(v)
    return found


def host(u):
    m = re.search(r"https?://([^/]+)", u)
    return m.group(1).lower() if m else ""


def page_candidates(url, htmltext):
    """Attachment URLs on a page, judged by neighbouring anchor text."""
    out = []

    def add(u, label):
        u = htmllib.unescape(u.strip())
        u = urllib.parse.urljoin(url, u)
        if not u.startswith("http") or u in [x["url"] for x in out]:
            return
        blob = u + " " + label
        if NOISE.search(blob) and not WANT_TABLE.search(blob):
            return
        if not (EXT.search(u) or FILEISH.search(u) or EXT.search(label)):
            return
        out.append({"url": u, "label": re.sub(r"\s+", " ", label)[:90],
                    "score": 2 if WANT_TABLE.search(label or "") else 0})

    for m in re.finditer(r'<a\b[^>]*href="([^"]+)"[^>]*>(.*?)</a>', htmltext, re.S | re.I):
        txt = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", m.group(2))).strip()
        add(m.group(1), txt)
    for m in re.finditer(r"""(?:fileDownload|fnFileDown|downFile|fileDown)\s*\(\s*['"]([^'"]+)['"]""",
                         htmltext, re.I):
        tok = m.group(1)
        for pat in (f"fileNo={tok}", f"fileSn={tok}", f"atchFileId={tok}", f"file_no={tok}"):
            add(url.split("?")[0] + "?" + pat, "")
    out.sort(key=lambda x: -x["score"])
    return out


def sublinks(url, htmltext):
    """Links worth one more hop: menu/sub pages about 등록금/수업료/재무/입학."""
    out = []
    for m in re.finditer(r'<a\b[^>]*href="([^"]+)"[^>]*>(.*?)</a>', htmltext, re.S | re.I):
        href = m.group(1)
        txt = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", m.group(2))).strip()
        if re.search(r"등록금|수업료|학비|일람표|재무|입학안내|입학처|신입생|장학", txt + href):
            if not re.search(r"장학", txt):        # 장학 pages are a different table
                u = urllib.parse.urljoin(url, htmllib.unescape(href))
                if u.startswith("http") and host(u) == host(url) and u not in out:
                    out.append(u)
    return out[:6]


def work(item, rec):
    school, lvl = item["school"], item["level"]
    seeds = urls_in(rec)
    res = {"school": school, "level": lvl, "seeds": seeds[:8], "pages": [], "attachments": []}
    seen = set()
    frontier = seeds[:4]
    while frontier and len(res["pages"]) < 8:
        u = frontier.pop(0)
        if u in seen:
            continue
        seen.add(u)
        try:
            h, _, final = get(u)
        except Exception as e:
            res["pages"].append({"url": u, "error": type(e).__name__})
            continue
        atts = page_candidates(final, h)
        res["pages"].append({"url": final, "attachments": len(atts), "등록금": h.count("등록금"),
                             "js": h.count("등록금") == 0})
        for a in atts:
            if a["url"] not in [x["url"] for x in res["attachments"]]:
                a["from_page"] = final
                res["attachments"].append(a)
        if not atts:
            frontier += [x for x in sublinks(final, h) if x not in seen][:4]
    res["attachments"].sort(key=lambda x: -x["score"])
    return res


def main():
    kb = load_kb()
    tbd = json.load(open(os.path.join(B, "tuition_by_department.json"), encoding="utf-8"))["schools"]
    pending = [(n, lv) for n, lvs in tbd.items() for lv, e in lvs.items()
               if isinstance(e, dict) and not e.get("rows")]
    print(f"pending (no per-college rows): {len(pending)}")
    if "--limit" in sys.argv:
        pending = pending[:int(sys.argv[sys.argv.index("--limit") + 1])]
    jobs = [({"school": n, "level": lv}, kb.get((n, lv), {})) for n, lv in pending
            if kb.get((n, lv))]
    print(f"with a KB record: {len(jobs)}")
    res = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
        for r in ex.map(lambda a: work(*a), jobs):
            key = f"{r['school']}|{r['level']}"
            res[key] = r
            seednote = f"{len(r['seeds'])} seeds" if r["seeds"] else "NO URL IN KB"
            print(f"  {r['school'][:15]:17}[{r['level']:7}] {seednote:12} pages={len(r['pages'])} "
                  f"atts={len(r['attachments'])}"
                  + (f"  top={r['attachments'][0]['label'][:40]}" if r["attachments"] else ""))
    json.dump(res, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    if "--download" in sys.argv:
        os.makedirs(DL, exist_ok=True)
        got, rej = 0, 0
        for key, r in res.items():
            if not r["attachments"]:
                continue
            d = os.path.join(DL, re.sub(r'[\\/:*?"<>|]', "_", key))
            os.makedirs(d, exist_ok=True)
            for a in r["attachments"][:6]:
                try:
                    raw, disp, _ = get(a["url"], binary=True)
                except Exception:
                    continue
                name = os.path.basename(urllib.parse.urlparse(a["url"]).path) or "file"
                if m := re.search(r'filename="?([^";]+)', disp or ""):
                    name = urllib.parse.unquote(m.group(1))
                if not EXT.search(name):
                    name += ".bin" if not re.search(r"\.(hwpx?|xlsx?|pdf)$", name, re.I) else ""
                blob = name + " " + (a.get("label") or "")
                if (NOISE.search(blob) and not WANT_TABLE.search(blob)) or len(raw) < 20_000:
                    rej += 1
                    continue
                open(os.path.join(d, name[:110]), "wb").write(raw)
                got += 1
                print(f"    saved {len(raw):>9,}B {key.split('|')[0][:14]:16} {name[:60]}")
        print(f"downloaded {got} | rejected {rej}")
    print("WROTE", OUT)


if __name__ == "__main__":
    main()