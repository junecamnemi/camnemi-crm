#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Download HiKorea 민원서식 HWP forms (recipe: POST /fileNewExistsChkAjax.pt with Referer)."""
import re, os, json, time, urllib.request, urllib.parse

DOM = r"C:\Users\wisew\camnemi-crm\backend\_hikorea_dom.html"
OUT = r"C:\Users\wisew\camnemi-crm\backend\hikorea_forms"
os.makedirs(OUT, exist_ok=True)
html = open(DOM, encoding="utf-8").read()

# extract (apnd, ori) pairs for hwp files
entries = re.findall(r"fnNewFileDownLoad\('pt','info','([^']+)','([^']+)'\)", html)
hwp = [(a, o) for a, o in entries if a.lower().endswith(".hwp")]
seen = set(); uniq = []
for a, o in hwp:
    if a in seen: continue
    seen.add(a); uniq.append((a, o))
print(f"총 다운로드 항목 {len(entries)} | HWP {len(uniq)}")

URL = "https://www.hikorea.go.kr/fileNewExistsChkAjax.pt"
def dl(apnd, ori):
    data = urllib.parse.urlencode({"spec": "pt", "dir": "info", "apndFileNm": apnd, "oriFileNm": ori,
                                   "BBS_GB_CD": "", "BBS_SEQ": "", "NTCCTT_SEQ": "", "APND_SEQ": "", "BBS_SKIN": ""}).encode()
    req = urllib.request.Request(URL, data=data, headers={
        "Referer": "https://www.hikorea.go.kr/board/BoardApplicationListR.pt",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0",
        "X-Requested-With": "XMLHttpRequest", "Content-Type": "application/x-www-form-urlencoded"})
    import ssl
    ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
    with urllib.request.urlopen(req, timeout=60, context=ctx) as r:
        return r.read()

ok = 0; fail = 0; index = []
for apnd, ori in uniq:
    safe = re.sub(r'[\\/:*?"<>|]', "_", ori)
    path = os.path.join(OUT, safe if safe.lower().endswith(".hwp") else safe + ".hwp")
    if os.path.exists(path) and os.path.getsize(path) > 5000:
        ok += 1; index.append({"apnd": apnd, "name": ori, "file": path, "size": os.path.getsize(path)}); continue
    try:
        b = dl(apnd, ori)
        if b[:4] == b"\xd0\xcf\x11\xe0" or b[:5] == b"%PDF" or len(b) > 5000:  # HWP(ole) or valid
            open(path, "wb").write(b)
            ok += 1; index.append({"apnd": apnd, "name": ori, "file": path, "size": len(b)})
        else:
            fail += 1
    except Exception as e:
        fail += 1
    time.sleep(0.3)
json.dump(index, open(os.path.join(OUT, "_index.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"다운로드 완료: 성공 {ok} / 실패 {fail} → {OUT}")
