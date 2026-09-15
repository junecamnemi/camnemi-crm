#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""discover_lang2.py — domain-based lang discovery.

From each uncovered school's known admission-URL domains, derive the MAIN homepage
(https://{root_domain}, also try www.), render it, and follow a 한국어교육원/어학
(or 국제) menu link to the program page. Records it in scrape_map (level=lang).
Falls back to a web-search-triggered domain guess if no admission URL is known.
"""
import os, re, json, subprocess, datetime, argparse, urllib.parse

B = r"C:\Users\USER\camnemi-crm\backend"
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
LANG_KEY = re.compile(r"한국어교육원|어학당|어학원|한국어|어학|international|korean.?language|klc|korean", re.I)

def norm(s): return re.sub(r"\[.*?\]", "", str(s)).replace("대학교","대학").replace("대학","").strip()

def render(url):
    try:
        r = subprocess.run([CHROME,"--headless=new","--disable-gpu","--no-sandbox",
                            "--dump-dom","--virtual-time-budget=9000", url],
                           capture_output=True, timeout=70)
        return (r.stdout or b"").decode("utf-8","ignore")
    except Exception as e:
        return f"__ERR__ {e}"

def root_domain(url):
    try:
        host = urllib.parse.urlparse(url).netloc
        parts = host.split(".")
        # country-code TLD (kr, jp, cn, tw) -> registrable is last 3 (e.g. gachon.ac.kr, ipsi.kaya.ac.kr -> kaya.ac.kr)
        if len(parts) >= 3 and len(parts[-1]) == 2:
            return ".".join(parts[-3:])
        if len(parts) >= 2:
            return ".".join(parts[-2:])
        return host
    except Exception:
        return None

def first_lang_href(dom, base):
    for m in re.finditer(r'href=["\']([^"\']+)["\']', dom):
        u = m.group(1)
        if LANG_KEY.search(u) or LANG_KEY.search(re.sub(r"<[^>]+>|\s+"," ", dom[max(0,m.start()-40):m.end()+40])):
            u2 = urllib.parse.urljoin(base, u.strip())
            if not u2.startswith("javascript"):
                return u2
    return None

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--limit", type=int, default=0); ap.add_argument("--start", type=int, default=0)
    a = ap.parse_args()
    kb = json.load(open(os.path.join(B,"verified_kb.json"),encoding="utf-8"))
    lp = kb["lang_programs"]["schools"]
    sm = json.load(open(os.path.join(B,"scrape_map.json"),encoding="utf-8"))
    dt = json.load(open(os.path.join(B,"_discover_targets.json"),encoding="utf-8"))
    import school_keys as SK
    # domain keyed by adiga canonical key
    dom = {}
    for t in dt:
        r = root_domain(t["url"])
        k = SK.resolve(t["school"])
        if r and k:
            dom.setdefault(k, []).append(f"https://{r}")
    def find_domains(s):
        k = SK.resolve(s)
        return dom.get(k, []) if k else []
    def candidates(s):
        out = []
        for u0 in find_domains(s):
            out += [u0, f"{u0}/", u0.replace("https://", "https://www.")]
        return out
    targets=[s for s in lp if not sm.get(s,{}).get("lang")]
    print(f"uncovered lang: {len(targets)} | domain-known: {sum(1 for s in targets if find_domains(s))}")
    found=0
    for s in targets[a.start:a.start+(a.limit or len(targets))]:
        got=None
        for u0 in candidates(s):
            d=render(u0)
            if d.startswith("__ERR__") or "<html" not in d.lower():
                continue
            langurl=first_lang_href(d, u0)
            if langurl:
                got=langurl; break
        if got:
            sm.setdefault(s,{})["lang"]={"url":got,"tier":"C","method":"domain",
                                         "discovered":datetime.date.today().isoformat()}
            found+=1
            print(f"  ✅ {s} → {got[:60]}")
        else:
            print(f"  ⊘ {s} (domains: {candidates(s)[:2]})")
    json.dump(sm,open(os.path.join(B,"scrape_map.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)
    print(f"\n발견 {found} | lang 총 {sum(1 for s,d in sm.items() if s!='_meta' and 'lang' in d)}")

if __name__=="__main__":
    main()