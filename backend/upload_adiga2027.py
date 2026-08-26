#!/usr/bin/env python3
"""Upload the 65 adiga 2027 foreign-admission PDFs to the Camnemi guide Drive folder.

Maps each uploaded file -> {viewLink, fileId, name}. Skips .hwp/.hwpx (need conversion)
and files already in the map. Saves backend/adiga2027_upload_map.json.
"""
import os, sys, json, time, base64, urllib.request, urllib.error, glob

BACKEND_URL = "https://script.google.com/macros/s/AKfycbwJ7QxDviSojjDJrRHJokneMebb46aS19ooqYiIuyYQsXdxzcZmyzPDleJXr-7JCnonAQ/exec"
FOLDER_ID   = "1nGH6jaZmqvQJ9yFKZuh-zsDOoeog3lo7"  # Camnemi guide folder (same as existing guides)
SRC         = r"C:/Users/USER/내 드라이브/02_Crawling_Sheet/University_Project/adiga_2027_외국인_모집요강/외국인"
MAP_PATH    = r"C:\Users\USER\camnemi-crm\backend\adiga2027_upload_map.json"
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
            time.sleep(3 + 5 * a)
    return {"error": "failed"}

def main():
    files = sorted(glob.glob(os.path.join(SRC, "*")))
    pdfs = [f for f in files if f.lower().endswith(".pdf")]
    others = [f for f in files if not f.lower().endswith(".pdf")]
    print(f"PDFs: {len(pdfs)} | non-PDF (skip): {len(others)}")
    for o in others: print("  skip:", os.path.basename(o))

    mapping = {}
    if os.path.exists(MAP_PATH):
        mapping = json.load(open(MAP_PATH, encoding="utf-8"))

    ok = 0; fail = 0
    for i, path in enumerate(pdfs, 1):
        if path in mapping and mapping[path].get("viewLink"):
            ok += 1; continue
        data = open(path, "rb").read()
        b64 = base64.b64encode(data).decode("ascii")
        if len(b64) > MAX_B64:
            print(f"  [{i}] TOO BIG ({len(data)/1e6:.1f}MB) skip: {os.path.basename(path)}")
            fail += 1; continue
        name = os.path.basename(path).replace("[본교]", "").replace("[제2캠퍼스]", "").replace("[제3캠퍼스]", "").replace("[제4캠퍼스]", "").replace("[분교]", "")
        r = post({"action": "upload", "folderId": FOLDER_ID, "filename": name, "contentBase64": b64})
        if r.get("ok"):
            mapping[path] = {"viewLink": r["viewLink"], "fileId": r["fileId"], "name": name, "size": len(data)}
            json.dump(mapping, open(MAP_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            ok += 1
            print(f"  [{i}] OK ({len(data)/1e6:.1f}MB): {name}")
        else:
            fail += 1
            print(f"  [{i}] FAIL: {r.get('error','?')} :: {os.path.basename(path)}")
        time.sleep(0.8)
    print(f"\nDONE ok={ok} fail={fail} total_mapped={len(mapping)}")
    json.dump(mapping, open(MAP_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

if __name__ == "__main__":
    main()
