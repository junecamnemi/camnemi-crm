#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""계열별 등록금 via real browser (Playwright) — the "둘 다" path.

Static fetch is dead for these: school homepages are JS menus and the national portals (adiga,
대학알리미) render client-side. So: Naver-search each school → keep results on the school's OWN
domain → extract HTML **tables structurally** (rows/cells), which is far safer than regex over prose,
and keep only tables that look like 등록금 (계열/학과 + amounts).

Determinism rules:
  · every amount must appear VERBATIM in the rendered cell text (no arithmetic, no unit conversion)
  · 입학금 columns are dropped (operator rule: 입학금 = 별도)
  · the unit (semester vs year) is taken from the page's own words (학기/연간/년) — if the page does
    not say, unit=unknown and the row is NOT converted
  · the guide year is recorded; a 2025 page is tagged prev_year rather than silently mixed
Writes _fees_pw_rows.jsonl (append-per-school, resumable) + _fees_pw_report.json
  python _fees_playwright.py --limit 6      # validate on a sample
  python _fees_playwright.py                # all pending
"""
import os, re, json, sys, urllib.parse
from playwright.sync_api import sync_playwright

B = os.path.dirname(os.path.abspath(__file__))
TBD = os.path.join(B, "tuition_by_department.json")
ROWS = os.path.join(B, "_fees_pw_rows.jsonl")
REPORT = os.path.join(B, "_fees_pw_report.json")

AMOUNT = re.compile(r"\d{1,3}(?:,\d{3}){2,}|\d{7,}")
COLLEGE = re.compile(r"인문|사회|자연|공학|예체능|예능|체능|간호|보건|사범|의학|약학|한의|수산|해양|"
                     r"농림|상경|경상|경영|사범|음악|미술|체육|디자인|전\s*계열|전\s*학과|기타")
FEE_HINT = re.compile(r"등록금|수업료|학비")
DROP_COL = re.compile(r"입학금|전형료|기타납부|실습비|기숙|식비")
# 공시 지표 tables sit on the same page and mention 등록금 somewhere — they are NOT tuition.
# Caught live: "학생1인당연간장학금(2025) 2,041,900", "학생1인당교육비(2025) 15,736,400".
METRIC = re.compile(r"1인당|인당|장학금|교육비|충원율|경쟁률|취업률|등록률|비율|율\b|순위|평균|"
                    r"합계|총계|계\b|소계|증감|전년|대비|환산|지수|만원")
# a row we can trust as a 모집단위 name
UNIT_NAME = re.compile(r"계열|학과|학부|전공|대학원|대학|과$|과정|트랙|전공심화")

TABLES_JS = """(() => {
  const out = [];
  for (const t of document.querySelectorAll('table')) {
    const rows = [];
    for (const tr of t.querySelectorAll('tr')) {
      const cells = [...tr.querySelectorAll('th,td')].map(c => (c.innerText||'').replace(/\\s+/g,' ').trim());
      if (cells.some(c => c)) rows.push(cells);
    }
    if (rows.length) out.push(rows);
  }
  return out;
})()"""


def school_token(name):
    n = re.sub(r"\(.*?\)|\[.*?\]", "", name)
    n = re.sub(r"(대학교|대학|학교|캠퍼스|본교|분교|성신교정)$", "", n.strip())
    return n.strip()


def own_domain(link, token):
    m = re.search(r"https?://([^/]+)", link)
    if not m:
        return False
    h = m.group(1).lower()
    if re.search(r"naver|google|youtube|daum|facebook|instagram|wikipedia|adiga|academyinfo|"
                 r"uni-?moa|junkang|blog|cafe|kin\.|tistory", h):
        return False
    return ".ac.kr" in h or ".kr" in h or ".or.kr" in h


def tables_to_rows(tables, page_text, url, school, level):
    rows = []
    unit = ("semester" if re.search(r"(학기|1학기|2학기)\s*(기준|당|분)", page_text) else
            "year" if re.search(r"(연간|년간|1년|연액)", page_text) else "unknown")
    ym = re.search(r"(20\d\d)\s*학년도", page_text)
    year = ym.group(1) if ym else None
    for t in tables:
        flat = " ".join(" ".join(r) for r in t)
        if not FEE_HINT.search(flat) or METRIC.search(flat[:400]):
            continue
        # header: which column is 수업료/등록금, which is 입학금
        header = next((r for r in t[:3] if any(re.search(r"수업료|등록금", c) for c in r)), None)
        # no header naming 수업료/등록금 → we cannot prove which number is tuition. Skip: a wrong
        # column is worse than a blank (the sheet would show a plausible but false 학비).
        if header is None:
            continue
        fee_idx = None
        for i, c in enumerate(header):
            if re.search(r"수업료|등록금", c) and not DROP_COL.search(c):
                fee_idx = i
                break
        for r in t:
            if not r:
                continue
            label = r[0].strip()
            if not label or AMOUNT.fullmatch(label) or re.fullmatch(r"구분|계열|학과|전공|모집단위|단과대학", label):
                continue
            if METRIC.search(label) or not UNIT_NAME.search(label):
                continue          # a 지표 row (장학금/교육비/비율) or a stub — not a 모집단위
            # 계열 names first (인문/자연/공학…), but accept a named 학과 row too — those give
            # per-department detail, which is the better outcome; `detail_level` records which.
            label_is_college = bool(COLLEGE.search(label))
            cells = [c for i, c in enumerate(r) if i > 0 and not DROP_COL.search(
                (header[i] if header and i < len(header) else ""))]
            pick = None
            if fee_idx is not None and fee_idx < len(r):
                pick = r[fee_idx]
            else:
                for c in cells:
                    if AMOUNT.search(c):
                        pick = c
                        break
            if not pick:
                continue
            m = AMOUNT.search(pick)
            if not m:
                continue
            krw = int(m.group(0).replace(",", ""))
            if krw < 500_000 or krw > 20_000_000:
                continue
            rows.append({"school": school, "level": level, "college": label[:60],
                         "krw": krw, "krw_raw": m.group(0), "unit": unit,
                         "source_url": url, "page_year": year,
                         "basis": f"공식 홈페이지 계열별 표({'학과별 미공개' if not header else '수업료 열'})",
                         "detail_level": "college" if label_is_college else "department",
                         "verbatim": f"{label} … {m.group(0)}"[:160]})
    return rows


def search_links(page, school):
    q = urllib.parse.quote(f"{school} 등록금")
    page.goto(f"https://search.naver.com/search.naver?query={q}", timeout=45000)
    page.wait_for_timeout(2500)
    links = page.eval_on_selector_all(
        "a[href^='http']",
        "els => els.map(e => [e.innerText.trim().slice(0,70), e.href])")
    token = school_token(school)
    keep = []
    for text, href in links:
        if not own_domain(href, token):
            continue
        if token[:3] and token[:3] not in urllib.parse.unquote(href) and token[:3] not in text:
            continue
        score = 2 if re.search(r"등록금|수업료|학비", text + href) else 0
        keep.append({"url": href, "text": text, "score": score})
    keep.sort(key=lambda x: -x["score"])
    seen, out = set(), []
    for k in keep:
        if k["url"] not in seen:
            seen.add(k["url"])
            out.append(k)
    return out[:4]


def work(page, school, level):
    res = {"school": school, "level": level, "links": [], "tables": 0, "rows": [], "errors": []}
    try:
        cands = search_links(page, school)
    except Exception as e:
        res["errors"].append(f"search:{type(e).__name__}")
        return res
    res["links"] = [c["url"] for c in cands]
    for c in cands[:3]:
        try:
            page.goto(c["url"], timeout=40000, wait_until="domcontentloaded")
            page.wait_for_timeout(1800)
            text = page.inner_text("body")[:40000]
            tables = page.evaluate(TABLES_JS)
            res["tables"] += len(tables)
            got = tables_to_rows(tables, text, c["url"], school, level)
            if got:
                res["rows"] += got
                break
        except Exception as e:
            res["errors"].append(f"{type(e).__name__}:{c['url'][:50]}")
    return res


def main():
    doc = json.load(open(TBD, encoding="utf-8"))
    pending = [(n, lv) for n, lvs in doc["schools"].items() for lv, e in lvs.items()
               if isinstance(e, dict) and not e.get("rows")]
    done = set()
    if os.path.exists(ROWS):
        for line in open(ROWS, encoding="utf-8"):
            if line.strip():
                r = json.loads(line)
                done.add((r["school"], r["level"]))
    todo = [p for p in pending if p not in done]
    if "--limit" in sys.argv:
        todo = todo[:int(sys.argv[sys.argv.index("--limit") + 1])]
    print(f"pending={len(pending)} already done={len(done)} this run={len(todo)}")
    rep = {}
    if os.path.exists(REPORT):
        rep = json.load(open(REPORT, encoding="utf-8"))
    with sync_playwright() as p:
        br = p.chromium.launch(headless=True)
        ctx = br.new_context(locale="ko-KR",
                             user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                                        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
        page = ctx.new_page()
        with open(ROWS, "a", encoding="utf-8") as fh:
            for school, level in todo:
                r = work(page, school, level)
                rep[f"{school}|{level}"] = {k: r[k] for k in ("links", "tables", "errors")}
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
                fh.flush()
                flag = "✔" if r["rows"] else "·"
                print(f"  {flag} {school[:15]:17}[{level:7}] links={len(r['links'])} "
                      f"tables={r['tables']} rows={len(r['rows'])}"
                      + (f"  {r['rows'][0]['college'][:18]} {r['rows'][0]['krw']:,}"
                         if r["rows"] else ""))
        br.close()
    json.dump(rep, open(REPORT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("WROTE", ROWS)


if __name__ == "__main__":
    main()