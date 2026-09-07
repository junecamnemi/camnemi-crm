#!/usr/bin/env python3
"""Find all passport files in each of the 57 Korea students' folders."""
import json, urllib.request, time, os

BACKEND = "https://script.google.com/macros/s/AKfycbwJ7QxDviSojjDJrRHJokneMebb46aS19ooqYiIuyYQsXdxzcZmyzPDleJXr-7JCnonAQ/exec"
DIR = os.path.dirname(os.path.abspath(__file__))
KOREA57 = os.path.join(DIR, "_korea57.json")
OUT = os.path.join(DIR, "_passport_files.json")

def main():
    students = json.load(open(KOREA57, encoding="utf-8"))
    results = []
    for i, s in enumerate(students):
        name = s["name"]
        fid = s.get("folder_id")
        if not fid:
            results.append({"name": name, "folder": None, "passports": [], "err": "no folder_id"})
            print(f"  {name}: NO FOLDER", flush=True)
            continue
        body = json.dumps({"action":"listStudentFolderFiles","name":name,"folderId":fid}).encode()
        req = urllib.request.Request(BACKEND, data=body, headers={"Content-Type":"text/plain;charset=utf-8"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=45) as r:
                d = json.loads(r.read())
            files = d.get("files", [])
            # passport files: name contains 'passport' (case-insensitive)
            pps = [f for f in files if "passport" in (f.get("name") or "").lower()]
            results.append({"name": name, "folder": fid, "passports": pps, "err": None})
            print(f"  {name}: {len(pps)} passport(s)", flush=True)
        except Exception as e:
            results.append({"name": name, "folder": fid, "passports": [], "err": str(e)[:80]})
            print(f"  {name}: ERR {e}", flush=True)
        time.sleep(0.35)
        if (i+1) % 15 == 0:
            json.dump(results, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
            print(f"  ...{i+1}/57 saved", flush=True)
    json.dump(results, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"DONE: {len(results)} students, output={OUT}", flush=True)

if __name__ == "__main__":
    main()
