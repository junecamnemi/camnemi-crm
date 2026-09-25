#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Daily junior-college foreigner-guide collection — DIRECT from each school's URL.
Replaces adiga.kr as the collection point. For each junior college:
  1. fetch its guide_url (from verified_kb)
  2. find the 2027 외국인 모집요강 PDF link
  3. download it into guides/junior/2027/ (or 2026/)
Outputs:
  _junior_direct_collected.json   per-school status + saved path
"""
import os, re, json, datetime, hashlib, urllib.request, ssl

BASE = r"C:\Users\wisew\camnemi-crm\backend"
UP = r"C:\Users\wisew\내 드라이브\02_Crawling_Sheet\University_Project"
GUIDES = os.path.join(UP, "guides", "junior")
OUT = os.path.join(BASE, "_junior_direct_collected.json")

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
           "Accept-Language": "ko-KR,ko;q=0.9"}
CTX = ssl.create_default_context(); CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE

def fetch(url, timeout=30):
    req = urllib.request.Request(url, headers=HEADERS)
    r = urllib.request.urlopen(req, timeout=timeout, context=CTX)
    if r.status >= 400:
        raise RuntimeError(f"http {r.status}")
    return r.read()

def find_pdf_links(text, base_url):
    links = set()
    for m in re.finditer(r'href=["\']([^"\']+?\.(?:pdf|hwp|hml|docx?))["\']', text, re.I):
        u = m.group(1)
        if u.startswith("//"): u = "https:" + u
        elif u.startswith("/"):
            from urllib.parse import urljoin
            u = urljoin(base_url, u)
        links.add(u)
    return sorted(links)

def is_2027_foreigner(url, text=""):
    """Heuristic: is this link a 2027 foreigner guide?"""
    s = url + " " + text
    if "2027" not in s and "2026" not in s:
        return None  # unknown year
    if "2027" in s:
        return "2027"
    return "2026"

def main():
    kb = json.load(open(os.path.join(BASE, "verified_kb.json"), encoding="utf-8"))
    juniors = kb.get("junior", {}).get("schools", {})
    today = datetime.date.today().isoformat()
    result = {}
    downloaded = 0

    for name, info in juniors.items():
        url = info.get("guide_url", "")
        if not url or not url.startswith("http"):
            result[name] = {"status": "no_url", "checked": today}
            continue
        try:
            html = fetch(url).decode("utf-8", "ignore")
            cands = find_pdf_links(html, url)
            # prefer 2027 foreigner guide
            picks = [c for c in cands if "외국인" in c or "foreign" in c.lower() or "2027" in c]
            if not picks:
                picks = cands
            if not picks:
                result[name] = {"status": "no_pdf_link", "url": url, "checked": today}
                continue
            src = picks[0]
            year = is_2027_foreigner(src)
            ydir = "2027" if year == "2027" else "2026"
            d = os.path.join(GUIDES, ydir)
            os.makedirs(d, exist_ok=True)
            fname = f"{name}_외국인모집요강_{year or 'unknown'}.pdf"
            path = os.path.join(d, fname)
            b = fetch(src)
            if not os.path.exists(path):
                open(path, "wb").write(b)
                downloaded += 1
            result[name] = {"status": "downloaded", "year": year, "saved": path,
                            "url": src, "checked": today}
        except Exception as e:
            result[name] = {"status": f"error:{type(e).__name__}", "url": url, "checked": today}

    json.dump(result, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    from collections import Counter
    st = Counter(v["status"] for v in result.values())
    print(f"전문대 {len(juniors)}개 처리 | 다운로드 {downloaded} | 상태: {dict(st)}")
    print(f"저장: {OUT}")

if __name__ == "__main__":
    main()
