#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Daily 2027 HOMEPAGE checker for foreign-student BA/MA (외국인 학사/대학원).

Purpose (user directive 2026-09-11):
  For every university whose BA (외국인 학부) or MA (외국인 대학원) 2027 모집요강 is
  NOT yet secured, EVERY DAY:
    1. Fetch the school's OFFICIAL admission page (ba_url / ma_url) and detect a
       newly-published 2027 guide (keywords: 2027 + 모집요강/외국인/신입학).
    2. Check whether the 2027 guide has appeared on adiga.kr (외국인 manifest for BA;
       the graduate-guide folder for MA).
    3. MAP the finding back into _guide_2027_master.json (status + url + note + date).

Why: adiga lags the school homepage by ~1-2 weeks (Sejong: own-site 2026-08-26,
adiga 2026-09-11). So we must watch the OWN SITE daily, not wait for adiga.

Outputs (backend/):
  _homepage_2027_check.json    per-school probe result (BA/MA)
  _homepage_2027_new.json      schools newly confirmed 2027 THIS run (the diff)
  _homepage_2027_summary.txt   human-readable summary
  _guide_2027_master.json      updated statuses for newly-2027 schools

Usage:
  python daily_homepage_2027_check.py            # probe all pending, update master
  python daily_homepage_2027_check.py --track ba # only BA
  python daily_homepage_2027_check.py --limit 20 # limit (testing)
"""
import json, os, re, sys, datetime, time, argparse

try:
    import requests
    requests.packages.urllib3.disable_warnings()
except Exception:
    requests = None

BASE = r"C:\Users\USER\camnemi-crm\backend"
MASTER = os.path.join(BASE, "_guide_2027_master.json")
OUT_JSON = os.path.join(BASE, "_homepage_2027_check.json")
OUT_NEW = os.path.join(BASE, "_homepage_2027_new.json")
OUT_TXT = os.path.join(BASE, "_homepage_2027_summary.txt")

ADIGA_BASE = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project\adiga_2027_외국인_모집요강"
ADIGA_MANIFEST = os.path.join(ADIGA_BASE, "download_manifest.csv")
ADIGA_FOREIGN_DIR = os.path.join(ADIGA_BASE, "외국인")
ADIGA_GRAD_DIR = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project\adiga_2027_대학원_모집요강"
ADIGA_GRAD_DIR_2026 = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project\adiga_2026_대학원_모집요강"

OK_2027 = {"2027_own", "2027_adiga", "2027_guide"}
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8",
}
TIMEOUT = 20

def norm(s):
    return re.sub(r"\[.*?\]", "", str(s)).replace("대학교", "").replace("대학", "").strip()

def probe(url):
    """Fetch a URL and return (reachable, has_2027, keywords, status).
    has_2027 is STRONG: page must show 2027 in a guide/admission context
    (i.e. '2027학년도' + 모집요강/외국인, or '2027' adjacent to 모집요강)."""
    if not url or "drive.google" in str(url):
        return False, False, [], "no_url/drive"
    if requests is None:
        return False, False, [], "no_requests"
    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT, verify=False, allow_redirects=True)
        if r.status_code >= 400:
            return False, False, [], f"http:{r.status_code}"
        import html as _html
        raw = _html.unescape(re.sub(r"<[^>]+>", " ", r.text[:300000]))
        text = re.sub(r"\s+", " ", raw)
        kws = [k for k in ["모집요강", "2027", "외국인", "재외국민", "신입학", "전형"] if k in text]
        # STRONG signal: a FOREIGNER-guide PHRASE near 2027. Require an explicit
        # 외국인 guide phrase (not the bare nav label '재외국민/외국인'), and 2027 within 60 chars.
        # ⚠️ 재외국민-only (overseas Korean) is a DIFFERENT track → reject.
        KR = r"(?:재외국민과\s*외국인|외국인\s*(?:특별전형|신입학|모집요강|전형))"
        EN = r"(?:International|Foreign)\s+Student[s]?"
        foreign2027 = (
            bool(re.search(rf"2027[^0-9]{{0,60}}{KR}", text))
            or bool(re.search(rf"{KR}[^0-9]{{0,60}}2027", text))
            or bool(re.search(rf"2027[^0-9]{{0,60}}{EN}", text, re.I))
            or bool(re.search(rf"{EN}[^0-9]{{0,60}}2027", text, re.I))
        )
        has27 = ("2027" in text) and foreign2027
        return True, has27, kws, f"http:{r.status_code}"
    except Exception as e:
        return False, False, [], f"error:{type(e).__name__}"

def adiga_has_foreign(school):
    """Check the adiga 2027 외국인 manifest for an available 외국인 guide for this school."""
    if not os.path.exists(ADIGA_MANIFEST):
        return None
    import csv
    key_n = norm(school)
    with open(ADIGA_MANIFEST, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            if norm(row.get("university", "")) == key_n and row.get("doc_type") == "외국인":
                return str(row.get("available", "")).lower() == "true"
    return None

def adiga_has_grad(school):
    """Check whether an adiga **2027** graduate guide file exists for this school.
    Only the 2027 folder counts — never fall back to 2026 (false positive)."""
    key = norm(school)
    if not os.path.isdir(ADIGA_GRAD_DIR):
        return False
    for f in os.listdir(ADIGA_GRAD_DIR):
        if key and key in norm(f):
            return True
    return False

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--track", choices=["ba", "ma", "all"], default="all")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    today = datetime.date.today().isoformat()
    master = json.load(open(MASTER, encoding="utf-8"))
    results = {"date": today, "ba": [], "ma": [], "new_ba": [], "new_ma": []}
    probed = ok = 0
    new_ba, new_ma = [], []

    for rec in master:
        school = rec["school"]
        for track in (["ba", "ma"] if args.track == "all" else [args.track]):
            status = rec.get(f"{track}_status", "")
            if status in OK_2027:
                continue
            url = rec.get(f"{track}_url") or ""
            url = url.split(" ")[0] if url else ""
            # skip drive-only sources
            if "drive.google" in url:
                url = rec.get(f"{track}_src", "")
            reachable, has27, kws, pstatus = probe(url)
            # adiga cross-check
            adiga = adiga_has_foreign(school) if track == "ba" else adiga_has_grad(school)
            entry = {"school": school, "status_prev": status, "url": url[:90],
                     "reachable": reachable, "has_2027": has27, "keywords": kws,
                     "probe": pstatus, "adiga_2027": adiga}
            results[track].append(entry)
            probed += 1
            if reachable:
                ok += 1
            # MAP: newly confirmed 2027 on own site -> update master
            if has27 and status not in OK_2027:
                rec[f"{track}_status"] = "2027_own"
                rec[f"{track}_url"] = url
                rec[f"{track}_note"] = f"HOMEPAGE 2027 detected {today} (auto). kw={kws}"
                new_ba.append(school) if track == "ba" else new_ma.append(school)
            elif adiga is True and status not in OK_2027:
                rec[f"{track}_status"] = "2027_adiga"
                rec[f"{track}_note"] = f"adiga 2027 guide available {today} (auto)"
                new_ba.append(school) if track == "ba" else new_ma.append(school)
            if args.limit and probed >= args.limit:
                break
        if args.limit and probed >= args.limit:
            break

    results["new_ba"] = new_ba
    results["new_ma"] = new_ma

    # save
    json.dump(results, open(OUT_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump({"date": today, "new_ba": new_ba, "new_ma": new_ma},
              open(OUT_NEW, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(master, open(MASTER, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    # summary
    lines = [f"=== Daily homepage 2027 check — {today} ===",
             f"probed {probed} pending targets, {ok} reachable",
             f"NEW 2027 confirmed: BA {len(new_ba)} | MA {len(new_ma)}"]
    if new_ba:
        lines.append("  BA: " + ", ".join(new_ba[:20]))
    if new_ma:
        lines.append("  MA: " + ", ".join(new_ma[:20]))
    # list reachable docs mentioning 2027 but not fully confirmed
    for track in ("ba", "ma"):
        m27 = [x for x in results[track] if x["reachable"] and "2027" in str(x["keywords"]) and not x["has_2027"]]
        if m27:
            lines.append(f"  [{track.upper()}] mention 2027 (manual review): " +
                         ", ".join(x["school"] for x in m27[:15]))
    txt = "\n".join(lines)
    open(OUT_TXT, "w", encoding="utf-8").write(txt)
    print(txt)
    print(f"\nSaved: {OUT_JSON}" if False else f"\nSaved: {os.path.basename(OUT_JSON)}, {os.path.basename(OUT_NEW)}")

if __name__ == "__main__":
    main()
