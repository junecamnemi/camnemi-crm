#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extract text from the HiKorea manuals (HWP) via pyhwp."""
import os, sys, io, contextlib

OUT = r"C:\Users\USER\camnemi-crm\backend\hikorea_manuals"
files = ["260901 사증민원 자격별 안내 매뉴얼.hwp", "260901 체류민원 자격별 안내 매뉴얼.hwp"]

for fn in files:
    src = os.path.join(OUT, fn)
    print("="*70); print(fn, os.path.getsize(src), "bytes")
    try:
        from hwp5.xmlmodel import Hwp5File
        f = Hwp5File(src)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            from hwp5.hwp5txt import TextTransform
            buf2 = io.StringIO()
            tt = TextTransform()
            import hwp5.hwp5txt as T
            # stream text
            tt.transform_hwp5_to_text(f, buf2)
        txt = buf2.getvalue()
    except Exception as e:
        print("  xmlmodel 실패:", str(e)[:120])
        try:
            from hwp5.hwp5txt import hwp5txt_main
            out = os.path.join(OUT, fn.replace(".hwp",".txt"))
            sys.argv = ["hwp5txt", src, "--output", out]
            import hwp5.hwp5txt
            # use CLI-like: read via pytxt
            from hwp5.dataio import ParseError
            txt = ""
        except Exception as e2:
            print("  CLI 실패:", str(e2)[:120]); txt=""
    print("  추출 길이:", len(txt))
    if txt:
        open(os.path.join(OUT, fn.replace(".hwp",".txt")), "w", encoding="utf-8").write(txt)
        print("  미리보기:", txt[:300].replace("\n"," "))
