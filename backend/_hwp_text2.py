#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extract text from HWP via PrvText + BodyText/Section0 record parsing."""
import olefile, zlib, struct, re, os

OUT = r"C:\Users\USER\camnemi-crm\backend\hikorea_manuals"
src = os.path.join(OUT, "260901 사증민원 자격별 안내 매뉴얼.hwp")

f = olefile.OleFileIO(src)
# 1) PrvText (plain preview, utf-16le)
try:
    prv = f.openstream("PrvText").read()
    t = prv.decode("utf-16-le", "ignore")
    print("=== PrvText 길이:", len(t))
    print(t[:400])
except Exception as e:
    print("PrvText 실패:", e)

# 2) BodyText/Section0 raw -> extract UTF-16 runs from the decompressed stream
try:
    raw = f.openstream("BodyText/Section0").read()
    try:
        data = zlib.decompress(raw, -15)
    except Exception:
        data = raw
    print("\n=== Section0 raw:", len(raw), "→ decompressed:", len(data))
    # HWP text records contain UTF-16LE strings; extract printable korean runs
    strs = re.findall((b"(?:[\x00-\xff][\xac-\xd7]|[\x00-\xff][\x00-\x02]){4,}").decode("latin1"), b"") if False else None
    # simpler: decode whole as utf-16le and keep korean/hangul runs
    txt = data.decode("utf-16-le", "ignore")
    runs = re.findall(r"[\uac00-\ud7a3\u3131-\u318e0-9A-Za-z\(\)\[\]\.\,\:\;\-\~\/\s%·•○▣□▪→←]{6,}", txt)
    body = "\n".join(r.strip() for r in runs if len(r.strip()) >= 6)
    print("=== 추출 런:", len(runs), "| 길이:", len(body))
    print(body[:500])
    if len(body) > 2000:
        open(os.path.join(OUT, "260901 사증민원 자격별 안내 매뉴얼.txt"), "w", encoding="utf-8").write(body)
        print("\n저장 완료")
except Exception as e:
    print("Section0 실패:", str(e)[:120])
