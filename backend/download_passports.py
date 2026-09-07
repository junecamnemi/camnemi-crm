#!/usr/bin/env python3
"""Download all passport files for 57 Korea students, rename uniformly, _1/_2 for multiples."""
import json, urllib.request, os, re, sys, time

BACKEND = "https://script.google.com/macros/s/AKfycbwJ7QxDviSojjDJrRHJokneMebb46aS19ooqYiIuyYQsXdxzcZmyzPDleJXr-7JCnonAQ/exec"
DIR = os.path.dirname(os.path.abspath(__file__))
PASSPORTS = os.path.join(DIR, "_passport_files.json")
OUT_DIR = os.path.join(os.environ.get("USERPROFILE", "C:/Users/USER"), "Desktop", "Passports_57")
os.makedirs(OUT_DIR, exist_ok=True)

def file_id_from_url(url):
    m = re.search(r'/file/d/([^/]+)/', url or '')
    return m.group(1) if m else None

def download_file(file_id, dest):
    # try drive.usercontent download (most reliable for CORS-free CLI)
    urls = [
        f"https://drive.usercontent.google.com/download?id={file_id}&export=download",
        f"https://drive.google.com/uc?export=download&id={file_id}",
    ]
    for u in urls:
        try:
            req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
            with urllib.request.urlopen(req, timeout=90) as r:
                data = r.read()
                if len(data) > 1000:
                    with open(dest, "wb") as f:
                        f.write(data)
                    return True, len(data)
        except Exception as e:
            last_err = str(e)
    # If all failed, try confirming the download (Google shows a virus-scan confirmation page)
    try:
        req = urllib.request.Request(urls[1] + "&confirm=t", headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=90) as r:
            data = r.read()
            if len(data) > 1000:
                with open(dest, "wb") as f:
                    f.write(data)
                return True, len(data)
    except Exception as e:
        last_err = str(e)
    return False, last_err

def main():
    data = json.load(open(PASSPORTS, encoding="utf-8"))
    report = []
    downloaded = 0
    failed = []
    for d in data:
        name = d["name"]
        pps = d["passports"]
        if not pps:
            report.append({"name": name, "count": 0, "files": [], "status": "NO_PASSPORT"})
            print(f"  {name}: NO passport file", flush=True)
            continue
        files_done = []
        for idx, p in enumerate(pps):
            fid = file_id_from_url(p.get("url")) or p.get("fileId")
            if not fid:
                files_done.append({"orig": p.get("name"), "file": None, "err": "no file id"})
                continue
            # uniform name: NAME_PASSPORT[_N].ext  (uppercase name, uppercase ext)
            name_clean = re.sub(r'[^A-Z0-9]', '_', name.upper())
            ext = os.path.splitext(p.get("name") or "")[1].upper() or ".PDF"
            if len(pps) == 1:
                fname = f"{name_clean}_PASSPORT{ext}"
            else:
                fname = f"{name_clean}_PASSPORT_{idx+1}{ext}"
            dest = os.path.join(OUT_DIR, fname)
            ok, info = download_file(fid, dest)
            if ok:
                downloaded += 1
                files_done.append({"orig": p.get("name"), "file": fname, "size": info})
                print(f"  ✓ {name}: {fname} ({info} bytes)", flush=True)
            else:
                failed.append({"name": name, "orig": p.get("name"), "err": info})
                files_done.append({"orig": p.get("name"), "file": None, "err": str(info)[:80]})
                print(f"  ✗ {name}: {p.get('name')} FAILED {info}", flush=True)
            time.sleep(0.2)
        report.append({"name": name, "count": len(files_done), "files": files_done, "status": "ok" if files_done else "NO_PASSPORT"})
    json.dump(report, open(os.path.join(DIR, "_passport_download_report.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"\nDONE: {downloaded} files downloaded, {len(failed)} failed, output={OUT_DIR}", flush=True)

if __name__ == "__main__":
    main()
