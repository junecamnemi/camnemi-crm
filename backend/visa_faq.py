#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""visa_faq.py — search the Korea visa FAQ by keyword.
  python visa_faq.py --list
  python visa_faq.py "아르바이트" / "불법체류" / "가족"
"""
import json, os, re, argparse
B = r"C:\Users\wisew\camnemi-crm\backend"
FAQ = json.load(open(os.path.join(B,"visa_faq_kr.json"), encoding="utf-8"))["faq"]
def search(kw):
    kws = [w for w in re.findall(r"[가-힣A-Za-z0-9\-]+", kw) if len(w)>=2]
    hits=[]
    for f in FAQ:
        txt = f["q"]+f["a"]+" ".join(f.get("src",[]))
        if any(k in txt for k in kws): hits.append(f)
    return hits
ap=argparse.ArgumentParser(); ap.add_argument("kw", nargs="?", default=""); ap.add_argument("--list",action="store_true")
a=ap.parse_args()
if a.list:
    print("■ 한국 비자 FAQ (20문항):")
    for i,f in enumerate(FAQ,1): print(f"  {i}. {f['q']}")
elif a.kw:
    hits = search(a.kw)
    if not hits:
        print(f"'{a.kw}' 관련 FAQ 없음. --list 로 전체 확인")
    for f in hits:
        print(f"\nQ. {f['q']}")
        print(f"A. {f['a']}")
        print(f"   [출처] {', '.join(f['src'])}")
else:
    ap.print_help()
