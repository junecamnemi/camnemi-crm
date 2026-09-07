#!/usr/bin/env python3
"""Scan all Korea students' Drive folders for empty folders. Saves progress incrementally."""
import json, urllib.request, time, os, sys

BACKEND = "https://script.google.com/macros/s/AKfycbwJ7QxDviSojjDJrRHJokneMebb46aS19ooqYiIuyYQsXdxzcZmyzPDleJXr-7JCnonAQ/exec"
DIR = os.path.dirname(os.path.abspath(__file__))
KOREA_FILE = os.path.join(DIR, "_korea_students.json")
PROG_FILE = os.path.join(DIR, "_scan_progress.json")
EMPTY_FILE = os.path.join(DIR, "_empty_folders.json")

def load_progress():
    if os.path.exists(PROG_FILE):
        try: return json.load(open(PROG_FILE, encoding="utf-8"))
        except: pass
    return {"index": 0, "empty": [], "errors": []}

def save_progress(p):
    json.dump(p, open(PROG_FILE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

def main(start_index, end_index):
    korea = json.load(open(KOREA_FILE, encoding="utf-8"))
    prog = load_progress()
    start = max(start_index, prog["index"])
    empty = prog["empty"]
    errors = prog["errors"]

    for i in range(start, min(end_index, len(korea))):
        s = korea[i]
        fid = s.get("folder_id")
        if not fid:
            empty.append({"name": s["name"], "stage": s["stage"], "school": s.get("school",""), "note": "NO_FOLDER_ID"})
            prog["index"] = i + 1
            save_progress(prog)
            continue
        body = json.dumps({"action":"listStudentFolderFiles","name":s["name"],"folderId":fid}).encode()
        req = urllib.request.Request(BACKEND, data=body, headers={"Content-Type":"text/plain;charset=utf-8"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                d = json.loads(r.read())
            n = len(d.get('files',[]))
            if n == 0:
                empty.append({"name": s["name"], "stage": s["stage"], "school": s.get("school",""), "files": 0})
                print(f"EMPTY: {s['name']} ({s['stage']})")
        except Exception as e:
            errors.append({"name": s["name"], "error": str(e)[:100]})
        prog["index"] = i + 1
        prog["empty"] = empty
        prog["errors"] = errors
        save_progress(prog)
        time.sleep(0.35)
        if (i+1) % 15 == 0:
            print(f"...{i+1}/{len(korea)} checked, empty={len(empty)}", flush=True)

    print(f"DONE chunk {start}-{min(end_index,len(korea))}: empty={len(empty)} errors={len(errors)}", flush=True)

if __name__ == "__main__":
    main(int(sys.argv[1]), int(sys.argv[2]) if len(sys.argv)>2 else 100000)
