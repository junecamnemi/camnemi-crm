#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""adiga_detail_ingest.py — adiga 모바일 상세에서 홈페이지·입시홈페이지·주소·전화 수집."""
import requests, re, json, time, os

requests.packages.urllib3.disable_warnings()
B = os.path.dirname(os.path.abspath(__file__))
BASE = "https://m.adiga.kr"
HEADERS = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/537.36",
           "Accept-Language": "ko-KR,ko;q=0.9"}

def fetch_detail(unvCd, is_junior):
    ep = "collDetail.do" if is_junior else "univDetail.do"
    menu = "MOUVTINF2001" if is_junior else "MOUVTINF1001"
    sub = "col" if is_junior else "uni"
    for attempt in range(3):
        try:
            r = requests.get(f"{BASE}/mob/ucp/uvt/{sub}/{ep}",
                            params={"menuId": menu, "unvCd": unvCd, "searchSyr": "2027"},
                            headers=HEADERS, verify=False, timeout=30)
            return r.text
        except Exception:
            time.sleep(1.5)
    return ""

def clean(u):
    u = u.replace("\\/", "/")
    u = u.replace("&quot;", "")
    u = u.replace("&#39;", "")
    return u.strip()

def extract(h):
    h2 = h.replace("&quot;", '"').replace("&#39;", "'").replace("\\/", "/")
    urls = re.findall(r"fnOpenNewUrl\(\s*[\"']([^\"']+)[\"']\s*\)", h2)
    home = None
    ipsi = None
    for u in urls:
        u = clean(u)
        if not u or "adiga" in u or "academyinfo" in u or "static" in u or "kcce" in u or "javascript" in u or u == "http:":
            continue
        if not u.startswith("http"):
            u = "http://" + u.lower()
        if "ipsi." in u or "admission" in u or "ipsi" in u:
            if not ipsi:
                ipsi = u
        else:
            if not home:
                home = u
    txt = re.sub(r"<[^>]+>", " ", h)
    txt = re.sub(r"\s+", " ", txt)
    addr = None
    m = re.search(r"([가-힣]{2,3}(?:특별시|광역시|도|시|군)\s+[가-힣0-9\s\-]{4,40})", txt)
    if m:
        addr = m.group(1).strip()
    tel = None
    m2 = re.search(r"(\d{2,3}-\d{3,4}-\d{4})", txt)
    if m2:
        tel = m2.group(1)
    return {"homepage": home, "ipsi_homepage": ipsi, "addr": addr, "tel": tel}

def main():
    univ = json.load(open(os.path.join(B, "_adiga_univ_list.json"), encoding="utf-8"))
    jr = json.load(open(os.path.join(B, "_adiga_junior_list.json"), encoding="utf-8"))
    out = {}
    for cd, nm in univ.items():
        if "[본교]" not in nm:
            continue
        h = fetch_detail(cd, is_junior=False)
        meta = extract(h)
        meta["name"] = nm
        out[cd] = meta
        time.sleep(0.25)
    for cd, nm in jr.items():
        h = fetch_detail(cd, is_junior=True)
        meta = extract(h)
        meta["name"] = nm
        out[cd] = meta
        time.sleep(0.25)
    with open(os.path.join(B, "_adiga_school_meta.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    n4 = sum(1 for cd in out if cd in univ)
    print(f"저장: {len(out)}개 (4년제 {n4} + 전문대 {len(out)-n4})")
    for cd in list(out)[:3]:
        print(" ", cd, out[cd])

if __name__ == "__main__":
    main()