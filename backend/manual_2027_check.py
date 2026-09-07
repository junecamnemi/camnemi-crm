#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Manual 2027 guide check — runs every morning alongside the daily auto-check.

Reads the pending lists (_daily_pending.json for BA/MA/lang + _junior_pending.json)
and probes each school's official page (via requests, fast/scripted) for signs of a
newly published 2027 admission guide:
  - HTTP reachability of the source URL(s)
  - presence of '모집요강' / '2027' / '입학' keywords in the fetched page
  - for Google-Drive links, only records reachability (file content not fetched)

Outputs:
  _manual_check_result.json  per-school probe result
  _manual_check_summary.txt  human-readable summary (delivered in cron report)

Schools still unverifiable by script stay in the pending set for a browser pass.
"""
import json, os, re, datetime, io

BASE = r"C:\Users\USER\camnemi-crm\backend"
PENDING = os.path.join(BASE, "_daily_pending.json")
PENDING_JR = os.path.join(BASE, "_junior_pending.json")
OUT_JSON = os.path.join(BASE, "_manual_check_result.json")
OUT_TXT = os.path.join(BASE, "_manual_check_summary.txt")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8",
}
TIMEOUT = 15
KEYWORDS = ["모집요강", "2027", "입학", "외국인"]


def probe(url):
    """Return dict with reachability + keyword hits for a URL."""
    if not url:
        return {"url": "", "reachable": False, "keywords": [], "status": "no_url"}
    if "drive.google.com" in url:
        # file link — only reachability; content not fetched
        try:
            import requests
            r = requests.get(url, headers=HEADERS, timeout=TIMEOUT, verify=False)
            return {"url": url[:100], "reachable": r.status_code < 400, "keywords": [],
                    "status": f"drive:{r.status_code}"}
        except Exception as e:
            return {"url": url[:100], "reachable": False, "keywords": [], "status": f"error:{type(e).__name__}"}
    try:
        import requests
        requests.packages.urllib3.disable_warnings()
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT, verify=False, allow_redirects=True)
        if r.status_code >= 400:
            return {"url": url[:100], "reachable": False, "keywords": [], "status": f"http:{r.status_code}"}
        # extract keywords from html text (cheap)
        text = re.sub(r"<[^>]+>", " ", r.text[:200000])
        hits = [k for k in KEYWORDS if k in text]
        return {"url": url[:100], "reachable": True, "keywords": hits, "status": f"http:{r.status_code}"}
    except Exception as e:
        return {"url": url[:100], "reachable": False, "keywords": [], "status": f"error:{type(e).__name__}"}


def main():
    today = datetime.date.today().isoformat()
    results = {"date": today, "tracks": {}, "probed": 0, "ok": 0, "unreachable": 0}

    tracks = {}
    if os.path.exists(PENDING):
        with open(PENDING, encoding="utf-8") as f:
            tracks = json.load(f)
    junior = []
    if os.path.exists(PENDING_JR):
        with open(PENDING_JR, encoding="utf-8") as f:
            junior = json.load(f)

    for track, lst in tracks.items():
        track_res = []
        for item in lst:
            school = item.get("school", "?")
            # pick best source URL: track-specific src > generic url
            src = item.get(f"{track.lower()}_src") or item.get("url") or item.get("ba_src") or item.get("ma_src") or item.get("lang_src") or ""
            if isinstance(src, list):
                src = src[0] if src else ""
            r = probe(src)
            r["school"] = school
            r["status_prev"] = item.get("status", "")
            track_res.append(r)
            results["probed"] += 1
            if r["reachable"]:
                results["ok"] += 1
            else:
                results["unreachable"] += 1
        results["tracks"][track] = track_res
        print(f"[{track}] {len(lst)} schools probed")

    # junior colleges
    jr_res = []
    for item in junior:
        school = item.get("school", "?")
        src = item.get("lang_url") or item.get("guide_url") or ""
        r = probe(src)
        r["school"] = school
        r["status_prev"] = item.get("status", "")
        jr_res.append(r)
        results["probed"] += 1
        if r["reachable"]:
            results["ok"] += 1
        else:
            results["unreachable"] += 1
    results["tracks"]["junior"] = jr_res
    print(f"[junior] {len(jr_res)} schools probed")

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=1)

    # summary txt
    buf = io.StringIO()
    buf.write(f"=== Manual 2027 check — {today} ===\n")
    buf.write(f"Probed {results['probed']} pending schools: {results['ok']} reachable, {results['unreachable']} unreachable/error\n\n")
    for track, lst in results["tracks"].items():
        reachable = [x for x in lst if x["reachable"]]
        with2027 = [x for x in reachable if any("2027" in str(k) for k in x.get("keywords", []))]
        buf.write(f"[{track}] {len(lst)} pending | {len(reachable)} reachable | {len(with2027)} mention 2027\n")
        for x in with2027[:10]:
            buf.write(f"   * {x['school']}: {x['status']} kw={x.get('keywords')}\n")
    txt = buf.getvalue()
    with open(OUT_TXT, "w", encoding="utf-8") as f:
        f.write(txt)
    print(txt)
    print(f"Saved: {OUT_JSON}")


if __name__ == "__main__":
    main()
