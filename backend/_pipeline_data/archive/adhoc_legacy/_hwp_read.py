import olefile, zlib, re, os, sys

p = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.environ["LOCALAPPDATA"], "Temp", "kw_fee_JF00000085103")
try:
    ole = olefile.OleFileIO(p)
    streams = ole.listdir()
    print("streams:", ["/".join(s) for s in streams][:20])
    if ole.exists("PrvText"):
        txt = ole.openstream("PrvText").read().decode("utf-16", errors="ignore")
        print("\n=== PrvText(미리보기) ===")
        print(re.sub(r"\s+", " ", txt)[:1500])
    # BodyText/Section0 (often zlib raw deflate)
    for s in streams:
        name = "/".join(s)
        if "BodyText" in name:
            data = ole.openstream(s).read()
            for wbits in (15, -15):
                try:
                    out = zlib.decompress(data, wbits)
                    t = out.decode("utf-16-le", errors="ignore")
                    t = re.sub(r"[\x00-\x1f]+", " ", t)
                    if re.search(r"[가-힣]{2,}", t):
                        print(f"\n=== {name} (wbits={wbits}, {len(out)}B) ===")
                        print(t[:2500])
                        break
                except Exception:
                    continue
    ole.close()
except Exception as e:
    print("ERR:", e)
