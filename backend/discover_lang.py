#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""discover_lang.py — find each uncovered school's 한국어교육원/어학원 program page.

Starts from the university admission/homepage URL (from _discover_targets or the
school guide_pdf), renders with Chrome headless, follows a 한국어교육원/어학 link,
records the resulting program page into scrape_map (level=lang).
"""
import os, re, json, subprocess, datetime, argparse, tempfile

B = r"C:\Users\wisew\camnemi-crm\backend"
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
LANG_KEY = re.compile(r"한국어교육원|어학당|어학원|한국어|국제|어학|인터내셔널|international|korean.?language|klc|ellt", re.I)

def norm(s): return re.sub(r"\[.*?\]", "", str(s)).replace("대학교", "대학").replace("대학", "").strip()

def render(url):
    try:
        r = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
                            "--dump-dom", "--virtual-time-budget=8000", url],
                           capture_output=True, timeout=65)
        return (r.stdout or b"").decode("utf-8", "ignore")
    except Exception as e:
        return f"__ERR__ {e}"

def absurl(base, u):
    from urllib.parse import urljoin
    if not u or u.startswith("javascript") or u.startswith("#"): return None
    return urljoin(base, u.strip())

def first_lang_href(dom, base):
    for m in re.finditer(r'href=["\']([^"\']+)["\']', dom):
        u = m.group(1)
        if LANG_KEY.search(u):
            a = re.sub(r"<[^>]+>|\s+", " ", dom[max(0, m.start()-50):m.end()+60])
            if LANG_KEY.search(a) or re.search(r"한국어|어학", u):
                return absurl(base, u)
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--start", type=int, default=0)
    a = ap.parse_args()

    # uncovered lang schools
    kb = json.load(open(os.path.join(B, "verified_kb.json"), encoding="utf-8"))
    lp = kb["lang_programs"]["schools"]
    sm = json.load(open(os.path.join(B, "scrape_map.json"), encoding="utf-8"))
    dt = json.load(open(os.path.join(B, "_discover_targets.json"), encoding="utf-8"))
    # match lang school to a university homepage (prefix-tolerant)
    dt_list = [(norm(t["school"]), t["url"]) for t in dt]
    def find_home(s):
        n = norm(s)
        # exact
        for nn, u in dt_list:
            if nn == n: return u
        # prefix either way
        for nn, u in dt_list:
            if n and (nn.startswith(n) or n.startswith(nn)) and len(n) >= 2 and len(nn) >= 2:
                return u
        return None
    def has_lang(s): return bool(sm.get(s, {}).get("lang"))
    targets = [s for s in lp if not has_lang(s)]
    print(f"uncovered lang: {len(targets)}")

    found = 0
    for s in targets[a.start:a.start + (a.limit or len(targets))]:
        seed = find_home(s)
        if not seed:
            print(f"  ⊘ {s}: no homepage URL")
            continue
        try:
            dom = render(seed)
            if dom.startswith("__ERR__"):
                print(f"  ✗ {s}: render err")
                continue
            langurl = first_lang_href(dom, seed)
            if langurl:
                sm.setdefault(s, {})["lang"] = {"url": langurl, "tier": "C",
                                                "discovered": datetime.date.today().isoformat(), "src": seed}
                found += 1
                print(f"  ✅ {s} → {langurl[:60]}")
            else:
                print(f"  ⊘ {s}: 어학 링크 없음 on {seed[:50]}")
        except Exception as e:
            print(f"  ✗ {s}: {e}")
    json.dump(sm, open(os.path.join(B, "scrape_map.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"\n발견 {found} | scrape_map lang {sum(1 for s,d in sm.items() if s!='_meta' and 'lang' in d)}")

if __name__ == "__main__":
    main()