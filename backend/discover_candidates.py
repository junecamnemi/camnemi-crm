#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""discover_candidates.py — scan school sites and produce a MANUAL-REVIEW batch of candidate guide URLs.

For each target admission page: chrome-headless render → collect candidate links that
could be the 외국인 모집요강 (PDF/HWP hrefs, download endpoints, guide-keyword anchors),
score by relevance, and write _guide_review_batch.json for human verification.
Verified picks are then moved into scrape_map.json (used by daily_guide_checker.py).
"""
import os, re, json, subprocess, datetime, argparse, tempfile, urllib.parse

B = r"C:\Users\USER\camnemi-crm\backend"
OUT = os.path.join(B, "_guide_review_batch.json")
MAP = os.path.join(B, "scrape_map.json")
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
KEY = re.compile(r"모집요강|외국인|재외국민|입학|2027|2026|국제|어학|한국어|전형|international|foreign|admission|apply|intl", re.I)
LINK = re.compile(r'href=["\']([^"\']+)["\']', re.I)
PDFLIKE = re.compile(r"\.(pdf|hwp|hml|docx?)([?#]|$)", re.I)

def render(url):
    try:
        r = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
                            "--dump-dom", "--virtual-time-budget=9000", url],
                           capture_output=True, timeout=70)
        return (r.stdout or b"").decode("utf-8", "ignore")
    except Exception as e:
        return f"__ERR__ {e}"

def absurl(base, u):
    u = u.strip()
    if not u or u.startswith("javascript") or u.startswith("#"):
        return None
    try:
        return urllib.parse.urljoin(base, u)
    except Exception:
        return None

def score(url, anchor=""):
    s = 0
    t = url + " " + anchor
    if PDFLIKE.search(url): s += 3
    if re.search(r"(\d{4})|(2027|2026)", url): s += 2
    if re.search(r"모집요강|외국인|재외국민", t): s += 3
    if re.search(r"intl|foreign|international|admission|apply|ipsi|입학", t, re.I): s += 2
    if re.search(r"한국어|어학|language|korean", t, re.I): s += 1
    if re.search(r"css|\.js\b|favicon|\.png|\.jpg|banner", url, re.I): s -= 3
    return s

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", required=True, help="[{school, level, url}] target admission pages")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    targets = json.load(open(args.json, encoding="utf-8"))
    if args.limit:
        targets = targets[:args.limit]
    batch = {"generated": datetime.date.today().isoformat(),
             "candidates": [], "not_found": []}
    print(f"스캔 대상: {len(targets)}")

    for t in targets:
        school, level, url = t["school"], t["level"], t["url"]
        dom = render(url)
        if dom.startswith("__ERR__"):
            batch["not_found"].append({"school": school, "level": level, "url": url, "note": dom[:60]})
            print(f"  ✗ {school} err")
            continue
        cands = []
        for m in LINK.finditer(dom):
            au = absurl(url, m.group(1))
            if not au:
                continue
            # anchor text near the href
            seg = dom[max(0, m.start()-60):m.end()+60]
            txt = re.sub(r"<[^>]+>|\\s+", " ", seg)
            sc = score(au, txt)
            if sc >= 3:
                cands.append({"url": au, "anchor": txt.strip()[:40], "score": sc})
        # dedupe by url, keep top
        seen = {}; 
        for c in sorted(cands, key=lambda x: -x["score"]):
            if c["url"] not in seen:
                seen[c["url"]] = c
        top = sorted(seen.values(), key=lambda x: -x["score"])[:6]
        if top:
            batch["candidates"].append({"school": school, "level": level, "src": url,
                                        "picks": top})
            print(f"  🎯 {school}[{level}] 후보 {len(top)}: " + " | ".join(t["url"][:40] for t in top[:3]))
        else:
            batch["not_found"].append({"school": school, "level": level, "url": url, "note": "no candidate link"})
            print(f"  ⊘ {school}[{level}] 후보 없음")

    json.dump(batch, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"\n총 후보 교: {len(batch['candidates'])}, 미발견: {len(batch['not_found'])}")
    print(f"저장: {OUT} — 이 파일을 검토 후 확정분을 scrape_map.json에 옮기면 daily_guide_checker가 매일 감시함")

if __name__ == "__main__":
    main()