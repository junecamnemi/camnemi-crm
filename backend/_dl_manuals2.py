#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Download the HiKorea 사증민원 / 체류민원 자격별 안내 매뉴얼 HWP (8-param POST)."""
import os, json, time, ssl, urllib.request, urllib.parse, re

OUT = r"C:\Users\USER\camnemi-crm\backend\hikorea_manuals"
os.makedirs(OUT, exist_ok=True)
URL = "https://www.hikorea.go.kr/fileNewExistsChkAjax.pt"
CTX = ssl.create_default_context(); CTX.check_hostname=False; CTX.verify_mode=ssl.CERT_NONE

FILES = [
 ("260901 사증.체류 민원 자격별 안내 매뉴얼 수정 이력[20260901101443177].hwp",
  "260901 사증.체류 민원 자격별 안내 매뉴얼 수정 이력.hwp", "510"),
 ("260901 사증민원 자격별 안내 매뉴얼[20260901101443182].hwp",
  "260901 사증민원 자격별 안내 매뉴얼.hwp", "511"),
 ("260901 체류민원 자격별 안내 매뉴얼[20260901101443203].hwp",
  "260901 체류민원 자격별 안내 매뉴얼.hwp", "512"),
]

def dl(apnd, ori, seq):
    data = urllib.parse.urlencode({
        "spec":"pt","dir":"ntc","apndFileNm":apnd,"oriFileNm":ori,
        "NTCCTT_SEQ":"1062","BBS_SEQ":"1","BBS_GB_CD":"BS10","APND_SEQ":seq,"BBS_SKIN":"NORMAL"}).encode()
    req = urllib.request.Request(URL, data=data, headers={
        "Referer":"https://www.hikorea.go.kr/board/BoardNtcDetailR.pt?BBS_SEQ=1&BBS_GB_CD=BS10&NTCCTT_SEQ=1062&page=1",
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0",
        "X-Requested-With":"XMLHttpRequest",
        "Content-Type":"application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=180, context=CTX) as r:
        return r.read()

idx=[]
for apnd, ori, seq in FILES:
    safe = re.sub(r'[\\/:*?"<>|]', "_", ori)
    path = os.path.join(OUT, safe)
    try:
        b = dl(apnd, ori, seq)
        ok = b[:4] == b"\xd0\xcf\x11\xe0" or len(b) > 100000
        open(path, "wb").write(b)
        idx.append({"name": ori, "file": path, "size": len(b), "valid_hwp": ok})
        print(f"{'OK ' if ok else '?  '} {ori}  {len(b):,} bytes")
    except Exception as e:
        print("ERR", ori, str(e)[:80])
    time.sleep(0.5)
json.dump(idx, open(os.path.join(OUT,"_index.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
print("\n저장:", OUT)
