#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""discover_guides.py — find each school's CURRENT 모집요강 PDF URL via Chrome headless.

Renders the school admission page (JS too), extracts candidate PDF/HWP links,
prefers guide-keyword links, writes them into scrape_map.json for daily_guide_checker.
Uses SCHOOL-OWN pages only (no adiga).
"""
import os, re, json, subprocess, datetime, argparse, tempfile

B = r"C:\Users\wisew\camnemi-crm\backend"
MAP = os.path.join(B, "scrape_map.json")
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
KEY = re.compile(r"모집요강|외국인|입학|2027|2026|한국어|어학|전형|admission|apply|intl", re.I)
LINK = re.compile(r'href=["\']([^"\']+?\.(?:pdf|hwp|hml|docx?)(?:[?#][^"\']*)?)["\']', re.I)

def render(url, timeout=60):
    out = tempfile.mktemp(suffix=".html")
    try:
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
                        "--dump-dom", "--virtual-time-budget=8000", url],
                       capture_output=True, timeout=timeout)
        # chrome --dump-dom prints DOM to stdout when redirected; use capture
        r = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
                            "--dump-dom", "--virtual-time-budget=8000", url],
                           capture_output=True, timeout=timeout)
        return (r.stdout or b"").decode("utf-8", "ignore")
    except Exception as e:
        return f"__ERR__{e}"

def absurl(base, u):
    from urllib.parse import urljoin
    if u.startswith("//"):
        return "https:" + u
    if u.startswith("/") or not u.startswith("http"):
        return urljoin(base, u)
    return u

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--urls", nargs="*", help="pairs school,level,url ...")
    ap.add_argument("--json", help="file of [{school,level,url}]")
    args = ap.parse_args()

    smap = json.load(open(MAP, encoding="utf-8")) if os.path.exists(MAP) else {}
    targets = []
    if args.json:
        for r in json.load(open(args.json, encoding="utf-8")):
            targets.append((r["school"], r["level"], r["url"]))
    elif args.urls:
        it = iter(args.urls)
        for s, l, u in zip(it, it, it):
            targets.append((s, l, u))
    print(f"발견할 대상: {len(targets)}")

    for school, level, url in targets:
        if school in smap and level in smap[school]:
            continue  # already mapped
        try:
            dom = render(url)
            if dom.startswith("__ERR__"):
                print(f"  ✗ {school} render err: {dom[:40]}")
                continue
            links = []
            for m in LINK.finditer(dom):
                u2 = absurl(url, m.group(1))
                if u2 not in links:
                    links.append(u2)
            picks = [u for u in links if KEY.search(u)]
            best = picks[0] if picks else (links[0] if links else None)
            if best:
                smap.setdefault(school, {})[level] = {"url": best, "discovered": datetime.date.today().isoformat(),
                                                      "src_page": url, "n_candidates": len(links)}
                print(f"  ✅ {school} [{level}] → {best[:80]}")
            else:
                print(f"  ⊘ {school} [{level}] no guide link on {url[:60]}")
        except Exception as e:
            print(f"  ✗ {school} {e}")
    json.dump(smap, open(MAP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"scrape_map 업데이트: 총 {sum(len(v) for v in smap.values())}개 매핑")

if __name__ == "__main__":
    main()