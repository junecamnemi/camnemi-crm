#!/usr/bin/env python3
"""Scan In Process + Korea students: check for name collisions and empty/wrong folders."""
import json, urllib.request, time, os

BACKEND = "https://script.google.com/macros/s/AKfycbwJ7QxDviSojjDJrRHJokneMebb46aS19ooqYiIuyYQsXdxzcZmyzPDleJXr-7JCnonAQ/exec"
DIR = os.path.dirname(os.path.abspath(__file__))

def get_index(force=True):
    body = json.dumps({"action":"getFolderIndex","force":force}).encode()
    req = urllib.request.Request(BACKEND, data=body, headers={"Content-Type":"text/plain;charset=utf-8"}, method="POST")
    with urllib.request.urlopen(req, timeout=120) as r:
        d = json.loads(r.read())
    return d.get("index", {})

def list_files(name, folder_id):
    body = json.dumps({"action":"listStudentFolderFiles","name":name,"folderId":folder_id}).encode()
    req = urllib.request.Request(BACKEND, data=body, headers={"Content-Type":"text/plain;charset=utf-8"}, method="POST")
    with urllib.request.urlopen(req, timeout=45) as r:
        d = json.loads(r.read())
    return d

def main():
    idx = get_index()
    print(f"index: {len(idx)}", flush=True)

    all_students = []
    for f in ["_scan_inprocess.json", "_scan_korea.json"]:
        all_students.extend(json.load(open(os.path.join(DIR, f), encoding="utf-8")))

    # dedupe by id
    seen = set()
    students = []
    for s in all_students:
        if s["id"] not in seen:
            seen.add(s["id"])
            students.append(s)
    print(f"students to check: {len(students)}", flush=True)

    results = []
    for i, s in enumerate(students):
        name = s["name"]
        db_fid = s.get("folder_id")
        # what does the index resolve this name to?
        label = name.lower().replace("/","").strip()
        idx_fid = idx.get(label)
        if not idx_fid:
            # fuzzy: tokens
            tokens = label.split()
            for k in idx:
                if all(t in k for t in tokens):
                    idx_fid = idx[k]; break
        status = "ok"
        files = -1
        db_files = -1
        if idx_fid:
            try:
                d = list_files(name, idx_fid)
                files = len(d.get("files", []))
                if d.get("found") is False:
                    status = "not_found"
                elif files == 0:
                    status = "EMPTY_FOLDER" if db_fid and db_fid != idx_fid else "empty_but_db_matches"
            except Exception as e:
                status = "err:" + str(e)[:50]
        else:
            status = "no_folder_in_index"

        # check DB folder vs index folder mismatch
        db_mismatch = ""
        if db_fid and idx_fid and db_fid != idx_fid:
            db_mismatch = f"DB({db_fid}) != INDEX({idx_fid})"
            status = "MISMATCH" if status in ("ok","EMPTY_FOLDER","empty_but_db_matches") else status

        results.append({
            "name": name, "pipe": s.get("pipe"), "stage": s.get("stage"),
            "db_fid": db_fid, "idx_fid": idx_fid,
            "files": files, "status": status, "mismatch": db_mismatch
        })
        if status != "ok":
            print(f"[{status}] {name} (pipe={s.get('pipe')} stage={s.get('stage')}) idx_files={files} {db_mismatch}", flush=True)
        time.sleep(0.2)
        if (i+1) % 20 == 0:
            json.dump(results, open(os.path.join(DIR, "_scan_results.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
            print(f"...{i+1}/{len(students)}", flush=True)

    json.dump(results, open(os.path.join(DIR, "_scan_results.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"DONE: {len(results)} students", flush=True)

if __name__ == "__main__":
    main()
