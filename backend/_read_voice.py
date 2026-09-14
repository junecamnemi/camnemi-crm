p = r"C:\Users\USER\AppData\Local\hermes\profiles\univ\cache\documents\doc_1ddee2b7761d_음성 260911_141623_original.txt"
raw = open(p, "rb").read()
for enc in ("utf-16", "utf-16-be", "utf-16-le"):
    try:
        t = raw.decode(enc)
        if t.count("\ufffd") < 5 and len(t) > 50:
            print(f"=== decoded as {enc} ({len(t)} chars) ===")
            print(t[:4000])
            break
    except Exception as e:
        print(enc, "fail", e)
