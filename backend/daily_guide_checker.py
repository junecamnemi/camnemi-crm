#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""daily_guide_checker.py — DAILY (requests-only, FAST) guide change-detector.

Reads scrape_map.json {school:{level:{url,saved}}}; for each known guide URL:
  download -> md5 -> compare with _guide_fingerprint.json
  if changed/new -> save to _ownsite_daily/ and append to _scrape_changes.jsonl
Only uses SCHOOL-OWN URLs (adiga NOT used). No browser -> suitable for the daily cron.

Discover unknown/missing URLs with discover_guides.py (chrome headless).
"""
import os, re, json, hashlib, datetime, argparse, urllib.request, ssl

UP = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project"
B = r"C:\Users\USER\camnemi-crm\backend"
MAP = os.path.join(B, "scrape_map.json")
FP = os.path.join(B, "_guide_fingerprint.json")
CHANGES = os.path.join(B, "_scrape_changes.jsonl")
OWN = os.path.join(UP, "_ownsite_daily")

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0 Safari/537.36",
           "Accept-Language": "ko-KR,ko;q=0.9"}
CTX = ssl.create_default_context(); CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE

def md5(b): return hashlib.md5(b).hexdigest()

def fetch(url, timeout=30):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
        return r.read(8000000)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--level", default="all"); ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    today = datetime.date.today().isoformat()
    os.makedirs(OWN, exist_ok=True)
    smap = json.load(open(MAP, encoding="utf-8")) if os.path.exists(MAP) else {}
    fp = json.load(open(FP, encoding="utf-8")) if os.path.exists(FP) else {}

    tasks = []  # (school, level, url)
    for school, lv in smap.items():
        for lvl, info in lv.items():
            if args.level != "all" and lvl != args.level:
                continue
            u = info.get("url")
            if isinstance(u, str) and u.startswith("http"):
                tasks.append((school, lvl, u))
    if args.limit:
        tasks = tasks[:args.limit]
    print(f"[daily_guide_checker] {today} | mapped tasks: {len(tasks)}")

    changed = 0
    for school, lvl, url in tasks:
        key = f"{school}_{lvl}"
        prev = fp.get(key, {})
        try:
            b = fetch(url)
            h = md5(b); sz = len(b)
            if prev.get("md5") == h:
                fp[key] = {**prev, "url": url, "size": sz, "last_checked": today, "status": "ok"}
            else:
                ext = os.path.splitext(url.split("?")[0])[1] or ".pdf"
                path = os.path.join(OWN, f"{school}_{lvl}{ext}")
                open(path, "wb").write(b)
                fp[key] = {"md5": h, "size": sz, "url": url, "saved": path, "last_checked": today,
                           "status": "updated", "prev_md5": prev.get("md5"), "changed_on": today}
                with open(CHANGES, "a", encoding="utf-8") as c:
                    c.write(json.dumps({"school": school, "level": lvl, "url": url,
                                        "prev_md5": prev.get("md5"), "new_md5": h, "saved": path, "date": today}, ensure_ascii=False) + "\n")
                changed += 1
                print(f"  ⚠️ CHANGE {school}[{lvl}]")
        except Exception as e:
            fp.setdefault(key, {})["url"] = url
            fp[key]["last_checked"] = today
            fp[key]["status"] = f"error:{type(e).__name__}"

    json.dump(fp, open(FP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"완료: {len(tasks)} 확인, {changed} 변경")
    print(f"CHANGE_COUNT={changed}")

if __name__ == "__main__":
    main()