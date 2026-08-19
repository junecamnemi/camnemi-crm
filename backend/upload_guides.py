#!/usr/bin/env python3
"""
Camnemi — Upload admission guide PDFs to Google Drive folder via Apps Script backend.
Usage: python upload_guides.py
Reads the current customer-pipeline.html to find every admission guide PDF path,
base64-encodes each, and POSTs it to the Apps Script web app (BACKEND_URL) which
saves it into the target Drive folder and returns a shareable link.
Saves a mapping JSON (local path -> {link, viewLink, fileId}) for the next step.
"""
import re, os, sys, json, time, base64, urllib.request, urllib.error

BACKEND_URL = "https://script.google.com/macros/s/AKfycbwJ7QxDviSojjDJrRHJokneMebb46aS19ooqYiIuyYQsXdxzcZmyzPDleJXr-7JCnonAQ/exec"
FOLDER_ID   = "1nGH6jaZmqvQJ9yFKZuh-zsDOoeog3lo7"
HTML_PATH   = r"C:\Users\wisew\customer-pipeline.html"
MAP_PATH    = r"C:\Users\wisew\guide_upload_map.json"
BATCH_DELAY = 0.6   # seconds between uploads (avoid Apps Script throttling)
MAX_B64     = 60_000_000  # ~45MB base64 -> stays under Apps Script 50MB limit

def main():
    h = open(HTML_PATH, encoding="utf-8").read()
    refs = sorted(set(re.findall(r'C:/Users/wisew/OneDrive/University AI/adiga_외국인모집요강/[^"\'`\\\s)]+\.pdf', h)))
    print(f"Found {len(refs)} guide PDFs to upload.\n")

    mapping = {}
    if os.path.exists(MAP_PATH):
        mapping = json.load(open(MAP_PATH, encoding="utf-8"))

    done = 0
    for i, path in enumerate(refs, 1):
        if not os.path.exists(path):
            print(f"  [{i}] MISSING (skip): {path}")
            continue
        if path in mapping and mapping[path].get("link"):
            done += 1
            continue  # already uploaded

        data = open(path, "rb").read()
        b64 = base64.b64encode(data).decode("ascii")
        if len(b64) > MAX_B64:
            print(f"  [{i}] TOO BIG ({len(data)/1e6:.1f}MB) skip: {path}")
            continue

        filename = os.path.basename(path)
        payload = json.dumps({"action":"upload","folderId":FOLDER_ID,
                              "filename":filename,"contentBase64":b64})
        req = urllib.request.Request(BACKEND_URL, data=payload.encode("utf-8"),
                                     headers={"Content-Type":"text/plain;charset=utf-8"})
        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                result = json.loads(resp.read().decode("utf-8"))
            if result.get("ok"):
                mapping[path] = {"link": result["viewLink"], "viewLink": result["viewLink"],
                                 "fileId": result["fileId"], "name": result["name"]}
                json.dump(mapping, open(MAP_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
                done += 1
                print(f"  [{i}] OK ({len(data)/1e6:.1f}MB): {filename}")
            else:
                print(f"  [{i}] ERROR: {result.get('error','?')} :: {filename}")
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "ignore")
            print(f"  [{i}] HTTP {e.code}: {body[:150]} :: {filename}")
        except Exception as e:
            print(f"  [{i}] FAIL: {e} :: {filename}")
        time.sleep(BATCH_DELAY)

    print(f"\nDone. Uploaded {done} of {len(refs)}.")
    print("Mapping saved to:", MAP_PATH)

if __name__ == "__main__":
    main()
