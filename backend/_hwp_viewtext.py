#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extract text from the distribution-protected 사증민원 HWP via ViewText streams."""
import olefile, zlib, re, os

OUT = r"C:\Users\USER\camnemi-crm\backend\hikorea_manuals"
src = os.path.join(OUT, "260901 사증민원 자격별 안내 매뉴얼.hwp")
f = olefile.OleFileIO(src)

def get(name):
    raw = f.openstream(name).read()
    try:
        return zlib.decompress(raw, -15)
    except Exception:
        return raw

all_txt = []
for s in [x for x in ["/".join(y) for y in f.listdir()] if x.startswith("ViewText/")]:
    data = get(s)
    txt = data.decode("utf-16-le", "ignore")
    runs = re.findall(r"[\uac00-\ud7a3\u3131-\u318e0-9A-Za-z\(\)\[\]\{\}\.\,\:\;\-\~\/\s%·•○▣□▪→←※]{4,}", txt)
    seg = "\n".join(r.strip() for r in runs if len(r.strip()) >= 4)
    if seg.strip():
        all_txt.append(seg)
    print(f"  {s}: raw {len(data)} → text {len(seg)}")

body = "\n".join(all_txt)
print("\n총 추출:", len(body))
print(body[:600])
if len(body) > 3000:
    open(os.path.join(OUT, "260901 사증민원 자격별 안내 매뉴얼.txt"), "w", encoding="utf-8").write(body)
    print("\n저장 완료")
