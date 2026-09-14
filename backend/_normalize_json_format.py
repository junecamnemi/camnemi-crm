import json, io

def rewrite(path, indent):
    obj = json.load(open(path, encoding="utf-8"))
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=indent)
    raw = open(path, "rb").read()
    crlf = b"\r\n" in raw[:200000]
    print(path, "indent=", indent, "CRLF=", crlf, "bytes=", len(raw))

rewrite(r"C:\Users\USER\camnemi-crm\backend\verified_kb.json", 2)
rewrite(r"C:\Users\USER\camnemi-crm\backend\consulting_db.json", 1)
