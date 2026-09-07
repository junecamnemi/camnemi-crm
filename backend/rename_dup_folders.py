#!/usr/bin/env python3
"""Rename the 7 filled student folders to DB-standard names via Apps Script backend."""
import json, urllib.request, time, os

BACKEND = "https://script.google.com/macros/s/AKfycbwJ7QxDviSojjDJrRHJokneMebb46aS19ooqYiIuyYQsXdxzcZmyzPDleJXr-7JCnonAQ/exec"
DIR = os.path.dirname(os.path.abspath(__file__))
PROG = os.path.join(DIR, "_rename_progress.json")

renames = [
    ("noeun souleang", "NOEUN SULEANG"),
    ("phornprak somphas", "PHORN PRAKSOMPHORS"),
    ("thuon vannchoeurng", "THUON VANNCHHOEURNG"),
    ("phoeuk pheanit", "PHOEUK PHEANITH"),
    ("sorm chanchumpou", "SORM CHANCHUM POU"),
    ("soun pichrita", "SOUN PICHIRITA"),
    ("phorn sreyly", "PHON SREYLY"),
]

def load_prog():
    if os.path.exists(PROG):
        try: return json.load(open(PROG, encoding="utf-8"))
        except: pass
    return {"results": []}

def save_prog(p):
    json.dump(p, open(PROG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

def main():
    prog = load_prog()
    done_old = {r["old"] for r in prog["results"]}
    for old, new in renames:
        if old in done_old: continue
        body = json.dumps({"action":"renameStudentFolder","oldName":old,"newName":new}).encode()
        req = urllib.request.Request(BACKEND, data=body, headers={"Content-Type":"text/plain;charset=utf-8"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                d = json.loads(r.read())
            if d.get("ok") and d.get("renamed"):
                print(f"RENAMED: {old} -> {new} (folderId={d.get('folderId')})", flush=True)
                prog["results"].append({"old": old, "new": new, "ok": True, "folderId": d.get("folderId")})
            else:
                print(f"WARN: {old} -> {new}: {d.get('error','?')}", flush=True)
                prog["results"].append({"old": old, "new": new, "ok": False, "error": d.get("error")})
        except Exception as e:
            print(f"ERR: {old}: {e}", flush=True)
            prog["results"].append({"old": old, "new": new, "ok": False, "error": str(e)})
        save_prog(prog)
        time.sleep(1)
    print("DONE", flush=True)

if __name__ == "__main__":
    main()
