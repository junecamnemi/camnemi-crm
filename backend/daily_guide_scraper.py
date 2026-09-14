#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""daily_guide_scraper.py — re-scrape school sites daily to CATCH guide-PDF updates.

Rationale (user 2026-09-12): a school may update its 모집요강 even after we
downloaded it. So do not trust the stale copy — re-fetch daily, hash, and if
the file changed, store the new guide + flag for KB re-parse.

Levels: 학부(BA) / 석사(MA, 대학원) / 전문학사(junior) / 어학연수(lang).

Targets come from:
  - _guide_2027_master.json  (BA/MA school->admission-homepage URL)
  - verified_kb guide_url / guide_pdf (전문대·어학·대학원 사이트 URL)

Output / artifacts:
  _guide_fingerprint.json   md5/size/url/mtime per {school}_{level}
  _scrape_changes.jsonl     each change (school, level, old->new hash, saved path)
  <adiga or external _ownsite download dir>/...  saved updated guides
"""
import os, re, json, hashlib, datetime, argparse, glob, urllib.request, ssl

UP = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project"
B = r"C:\Users\USER\camnemi-crm\backend"
FP = os.path.join(B, "_guide_fingerprint.json")
CHANGES = os.path.join(B, "_scrape_changes.jsonl")
OWN_DIR = os.path.join(UP, "_ownsite_daily")

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
           "Accept-Language": "ko-KR,ko;q=0.9"}
CTX = ssl.create_default_context(); CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE
MULTI_LEVEL = re.compile(r"(2027|2026|모집요강|외국인|입학|한국어교육원)")

def norm(s):
    return re.sub(r"\[.*?\]|^\d+_", "", str(s)).strip()

def fetch(url, timeout=25, stream=False):
    req = urllib.request.Request(url, headers=HEADERS)
    r = urllib.request.urlopen(req, timeout=timeout, context=CTX)
    if r.status >= 400:
        raise RuntimeError(f"http {r.status}")
    if stream:
        return r
    b = r.read(6000000)
    return b

def md5(b):
    return hashlib.md5(b).hexdigest()

def find_pdf_links(text, base_url):
    "Extract candidate guide PDF/HWP links from a homepage/HTML text."
    links = set()
    for m in re.finditer(r'href=["\']([^"\']+?\.(?:pdf|hwp|hml|docx?))["\']', text, re.I):
        u = m.group(1)
        if u.startswith("//"):
            u = "https:" + u
        elif u.startswith("/"):
            from urllib.parse import urljoin
            u = urljoin(base_url, u)
        links.add(u)
    return sorted(links)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--level", choices=["ba", "ma", "junior", "lang", "all"], default="all")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--download", action="store_true", default=True)
    args = ap.parse_args()

    today = datetime.date.today().isoformat()
    os.makedirs(OWN_DIR, exist_ok=True)
    fp = json.load(open(FP, encoding="utf-8")) if os.path.exists(FP) else {}

    # ---- build targets ----
    targets = []  # (school, level, url)
    master_path = os.path.join(B, "_guide_2027_master.json")
    if os.path.exists(master_path):
        for rec in json.load(open(master_path, encoding="utf-8")):
            s = rec.get("school", "")
            for tr, lvl in (("ba", "ba"), ("ma", "ma")):
                u = rec.get(f"{tr}_url") or ""
                u = u.split(" ")[0] if u else ""
                if u and "drive.google" not in u:
                    targets.append((s, lvl, u))
    # KB guide_url (junior/lang/ma web links)
    try:
        kb = json.load(open(os.path.join(B, "verified_kb.json"), encoding="utf-8"))
    except Exception:
        kb = {}
    for lbl, sec, lvl in [("전문대", ["junior", "schools"], "junior"),
                          ("어학", ["lang_programs", "schools"], "lang"),
                          ("대학원", ["master", "schools"], "ma")]:
        try:
            d = kb[sec[0]][sec[1]] if sec[1] else kb[sec[0]]
        except Exception:
            continue
        for s, v in d.items():
            u = v.get("guide_url") or ""
            if isinstance(u, str) and u.startswith("http"):
                targets.append((s, lvl, u.split(" ")[0]))
    if args.level != "all":
        targets = [t for t in targets if t[1] == args.level]
    if args.limit:
        targets = targets[:args.limit]
    # dedupe
    targets = list(dict.fromkeys(targets))
    print(f"대상 {len(targets)}개 (level filter={args.level})")

    changed = []
    checked = 0
    for school, lvl, url in targets:
        key = f"{norm(school)}_{lvl}"
        prev = fp.get(key, {})
        prev_url = prev.get("url", "")
        # same URL & unchanged recently -> quick skip? still HEAD for Last-Modified
        try:
            if url.lower().endswith((".pdf", ".hwp", ".hml", ".docx")):
                b = fetch(url)
                h = md5(b); sz = len(b); src_url = url
            else:
                # homepage: fetch page, find a guide PDF link
                html = fetch(url).decode("utf-8", "ignore")
                cands = find_pdf_links(html, url)
                # prefer a link containing guide keywords
                picks = [c for c in cands if MULTI_LEVEL.search(c)]
                if not picks:
                    picks = cands
                if not picks:
                    fp[key] = {"url": url, "status": "no_pdf_link", "last_checked": today, "size": 0}
                    continue
                src_url = picks[0]
                b = fetch(src_url)
                h = md5(b); sz = len(b)
            checked += 1
            if prev.get("md5") == h:
                fp[key] = {**prev, "last_checked": today, "status": "ok", "size": sz, "url": src_url}
            else:
                # save the new guide
                ext = os.path.splitext(src_url.split("?")[0])[1] or ".pdf"
                fname = f"{norm(school)}_{lvl}{ext}"
                path = os.path.join(OWN_DIR, fname)
                open(path, "wb").write(b)
                fp[key] = {"md5": h, "size": sz, "url": src_url, "saved": path,
                           "last_checked": today, "status": "updated",
                           "prev_md5": prev.get("md5"), "changed_on": today}
                with open(CHANGES, "a", encoding="utf-8") as ch:
                    ch.write(json.dumps({"school": school, "level": lvl, "url": src_url,
                                         "prev_md5": prev.get("md5"), "new_md5": h,
                                         "saved": path, "date": today}, ensure_ascii=False) + "\n")
                changed.append((school, lvl, prev.get("md5"), h))
                print(f"  ⚠️ CHANGE: {school} [{lvl}] {str(prev.get('md5'))[:6]}→{h[:6]} → {fname}")
        except Exception as e:
            fp.setdefault(key, {})["last_error"] = str(type(e).__name__)
            fp[key]["last_checked"] = today
            fp[key]["status"] = "error"

    json.dump(fp, open(FP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"완료: {checked} 확인, {len(changed)} 변경")
    print(f"변경: {', '.join(f'{s}[{l}]' for s, l, _, _ in changed) if changed else '없음'}")
    # change count for cron gate
    print(f"_scrape_changes_today={len(changed)}")

if __name__ == "__main__":
    main()