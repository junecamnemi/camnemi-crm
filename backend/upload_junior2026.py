#!/usr/bin/env python3
"""Upload 2026 JUNIOR-college admission guides to the Camnemi guide Drive folder.
Maps each file -> {viewLink, fileId}. Resumable (skips already-mapped)."""
import os, glob, json, base64, time, urllib.request

BACKEND_URL = "https://script.google.com/macros/s/AKfycbwJ7QxDviSojjDJrRHJokneMebb46aS19ooqYiIuyYQsXdxzcZmyzPDleJXr-7JCnonAQ/exec"
FOLDER_ID   = "1nGH6jaZmqvQJ9yFKZuh-zsDOoeog3lo7"
SRC         = r"C:/Users/USER/내 드라이브/02_Crawling_Sheet/University_Project/adiga_2026_전문대학_모집요강"
MAP_PATH    = r"C:\Users\USER\camnemi-crm\backend\junior2026_upload_map.json"
MAX_B64     = 60_000_000

def post(payload, retries=3):
    for a in range(retries):
        try:
            req = urllib.request.Request(BACKEND_URL, data=json.dumps(payload).encode("utf-8"),
                                         headers={"Content-Type": "text/plain;charset=utf-8"})
            with urllib.request.urlopen(req, timeout=300) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            if a == retries - 1: return {"error": str(e)}
            time.sleep(3 + 5*a)
    return {"error": "failed"}

def main():
    pdfs = sorted(f for f in glob.glob(os.path.join(SRC, "*")) if f.lower().endswith(".pdf"))
    print(f"PDFs: {len(pdfs)}")
    mapping = json.load(open(MAP_PATH, encoding="utf-8")) if os.path.exists(MAP_PATH) else {}
    ok=fail=skip=0
    for i, path in enumerate(pdfs, 1):
        if path in mapping and mapping[path].get("viewLink"):
            ok += 1; continue
        data = open(path, "rb").read()
        b64 = base64.b64encode(data).decode("ascii")
        if len(b64) > MAX_B64:
            print(f"  [{i}] TOO BIG ({len(data)/1e6:.1f}MB) skip: {os.path.basename(path)}")
            fail += 1; continue
        name = os.path.basename(path).replace("[본교]","").replace("[제2캠퍼스]","")
        r = post({"action":"upload","folderId":FOLDER_ID,"filename":name,"contentBase64":b64})
        if r.get("ok") and (r.get("viewLink") or r.get("fileId")):
            mapping[path] = {"viewLink": r.get("viewLink"), "fileId": r.get("fileId"), "name": name}
            ok += 1
            if ok % 10 == 0:
                json.dump(mapping, open(MAP_PATH,"w",encoding="utf-8"), ensure_ascii=False, indent=1)
                print(f"  ...{ok} uploaded")
        else:
            print(f"  [{i}] FAIL {os.path.basename(path)}: {str(r)[:120]}")
            fail += 1
        time.sleep(0.4)
    json.dump(mapping, open(MAP_PATH,"w",encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"DONE ok={ok} fail={fail} | map={MAP_PATH}")

if __name__ == "__main__":
    main()
