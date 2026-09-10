#!/usr/bin/env python3
"""Download 2026 foreigner admission guides (외국인 모집요강) for 7 junior colleges
from adiga.kr, saving into the adiga_2026_전문대학_모집요강 project folder as
{학교}_전문학사_외국인모집요강.pdf.

Methodology mirrors scrape_adiga_2027.py:
  1. univGroupAjax.do (searchSyr=2026) -> universities (unvCd + name)
  2. univFileAjax.do (searchSyr=2026, unvCd) -> doc list w/ fileId+fileSn
  3. fileDown.do -> download the 외국인 모집요강 PDF
"""
import requests, re, time, os, sys, json
from urllib.parse import unquote

requests.packages.urllib3.disable_warnings()

BASE = "https://www.adiga.kr"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8",
}
REFERER_LIST = f"{BASE}/ucp/uvt/uni/univView.do?menuId=PCUVTINF2000"
REFERER_DETAIL = f"{BASE}/ucp/uvt/uni/univDetail.do?menuId=PCUVTINF2000&searchSyr=2026"

YEAR = 2026
OUT_DIR = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project\adiga_2026_전문대학_모집요강"
os.makedirs(OUT_DIR, exist_ok=True)

TARGETS = [
    "계원예술대학교", "농협대학교", "대구과학대학교", "부산여자대학교",
    "영남외국어대학", "영남이공대학교", "충남도립대학교",
]

def get(url, **kw):
    kw.setdefault("headers", HEADERS); kw.setdefault("timeout", 60); kw.setdefault("verify", False)
    return requests.get(url, **kw)

def post(url, data, referer=None, **kw):
    h = dict(HEADERS)
    if referer: h["Referer"] = referer
    kw.setdefault("headers", h); kw.setdefault("timeout", 60); kw.setdefault("verify", False)
    return requests.post(url, data=data, **kw)

def fetch_universities():
    r = post(f"{BASE}/ucp/uvt/uni/univGroupAjax.do", {"searchSyr": YEAR}, referer=REFERER_LIST)
    items = re.findall(r'<li>(.*?)</li>', r.text, re.S)
    univs = {}
    for it in items:
        cd = re.search(r'name="searchUnvCode"[^>]*value="(\d+)"', it)
        name_m = re.search(r'<label[^>]*>\s*([^<]+?)\s*<strong>', it, re.S)
        if cd:
            name = re.sub(r"\s+", " ", name_m.group(1).strip()) if name_m else ""
            univs[cd.group(1)] = {"unvCd": cd.group(1), "name": name}
    return univs

def fetch_file_list(unvCd):
    r = post(f"{BASE}/ucp/uvt/uni/univFileAjax.do",
             {"searchSyr": YEAR, "unvCd": unvCd, "syr": YEAR},
             referer=REFERER_DETAIL + f"&unvCd={unvCd}")
    from html import unescape
    lis = re.findall(r'<li([^>]*)>(.*?)</li>', unescape(r.text), re.S)
    entries = []
    for attrs, inner in lis:
        disabled = "disabled" in attrs
        m = re.search(r"fnUnvFileDownOne\('([^']+)',\s*'([^']+)'", inner)
        fileId = m.group(1) if m else ""
        fileSn = m.group(2) if m else ""
        span = re.search(r"<span>(.*?)</span>", inner, re.S)
        label = ""
        if span:
            label = re.sub(r"<[^>]+>", "", span.group(1)).strip()
            label = re.sub(r"\s+", " ", label)
        entries.append({"label": label, "disabled": disabled, "fileId": fileId, "fileSn": fileSn})
    return entries

def download(unvCd, fileId, fileSn):
    url = (f"{BASE}/cmm/com/file/fileDown.do?fileId={fileId}&fileSn={fileSn}"
           f"&menuId=PCUVTINF2000&downLogYn=Y&unvCd={unvCd}&searchSyr={YEAR}")
    r = get(url, headers={**HEADERS, "Referer": REFERER_DETAIL + f"&unvCd={unvCd}",
                          "X-Requested-With": "XMLHttpRequest"})
    if r.status_code != 200:
        return None, r.status_code, ""
    content = r.content
    ctype = r.headers.get("Content-Type", "")
    if content[:1] == b"{" or ctype.startswith("application/json") or \
       content.lstrip()[:5].lower() in (b"<html", b"<!doc"):
        return None, r.status_code, ctype
    disp = r.headers.get("Content-Disposition", "")
    fn_m = re.search(r"filename\*=(?:UTF-8'')?([^;]+)", disp)
    if fn_m:
        orig = unquote(fn_m.group(1))
    else:
        fn_m2 = re.search(r'filename="?([^";]+)', disp)
        orig = fn_m2.group(1) if fn_m2 else "file"
    return content, r.status_code, orig

def main():
    univs = fetch_universities()
    print(f"[1] Universities for {YEAR}: {len(univs)}")
    found = {t: [] for t in TARGETS}
    # match by exact name or normalized containment
    def norm(s): return re.sub(r"\s+", "", s)
    for cd, u in univs.items():
        un = norm(u["name"])
        for t in TARGETS:
            if un == norm(t):
                found[t].append(u)
    print("[2] Matches:")
    results = {}
    for t in TARGETS:
        if not found[t]:
            print(f"    NO MATCH: {t}")
            results[t] = {"status": "no-match"}
            continue
        u = found[t][0]
        unvCd, uname = u["unvCd"], u["name"]
        try:
            entries = fetch_file_list(unvCd)
        except Exception as e:
            print(f"    {t} FILE-LIST ERROR: {e}")
            results[t] = {"status": "file-list-error", "error": str(e)}
            continue
        target_ent = None
        for ent in entries:
            lab = re.sub(r"\s+", "", ent["label"])
            if "외국인모집요강" in lab or "외국인" in lab:
                if not ent["disabled"] and ent["fileId"]:
                    target_ent = ent
                    break
        if not target_ent:
            labels = [e["label"] for e in entries]
            print(f"    {t} no foreigner file. labels={labels}")
            results[t] = {"status": "no-foreigner-file", "labels": labels}
            continue
        content, status, orig = download(unvCd, target_ent["fileId"], target_ent["fileSn"])
        if content is None:
            print(f"    {t} DOWNLOAD FAIL status={status} orig={orig}")
            results[t] = {"status": "download-fail", "status_code": status}
            continue
        ext = os.path.splitext(orig)[1] or ".pdf"
        fname = f"{t}_전문학사_외국인모집요강{ext}"
        fpath = os.path.join(OUT_DIR, fname)
        with open(fpath, "wb") as f:
            f.write(content)
        print(f"    OK {t} -> {fname} ({len(content)} bytes, src={orig})")
        results[t] = {"status": "ok", "saved_as": fname, "bytes": len(content),
                      "unvCd": unvCd, "fileId": target_ent["fileId"], "orig": orig}
        time.sleep(0.3)
    json.dump(results, open(os.path.join(OUT_DIR, "_jr_foreign_batch0_result.json"), "w",
                            encoding="utf-8"), ensure_ascii=False, indent=1)
    print("[3] Done.")

if __name__ == "__main__":
    main()
