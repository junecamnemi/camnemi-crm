#!/usr/bin/env python3
"""Upload the 2 converted 건양대학교 hwpx->pdf 2027 guides and upsert DB rows."""
import os, json, time, base64, re, urllib.request, urllib.parse

BACKEND_URL = "https://script.google.com/macros/s/AKfycbwJ7QxDviSojjDJrRHJokneMebb46aS19ooqYiIuyYQsXdxzcZmyzPDleJXr-7JCnonAQ/exec"
FOLDER_ID   = "1nGH6jaZmqvQJ9yFKZuh-zsDOoeog3lo7"
MAP_PATH    = r"C:\Users\USER\camnemi-crm\backend\adiga2027_upload_map.json"

h = open(r"C:\Users\USER\camnemi-crm\index.html", encoding="utf-8").read()
m = re.search(r"DEFAULT_SUPABASE_KEY\s*=\s*'([^']+)'", h)
key = m.group(1)
BASE = "https://zjdvzpylxazfbazioxto.supabase.co/rest/v1/university_guides"

def api(method, path, body=None):
    req = urllib.request.Request(BASE + path, data=json.dumps(body).encode("utf-8") if body else None,
                                 headers={"apikey": key, "Authorization": "Bearer " + key, "Content-Type": "application/json", "Prefer": "return=minimal"})
    req.get_method = lambda: method
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.status

def post(payload, retries=4):
    for a in range(retries):
        try:
            req = urllib.request.Request(BACKEND_URL, data=json.dumps(payload).encode("utf-8"),
                                         headers={"Content-Type": "text/plain;charset=utf-8"})
            with urllib.request.urlopen(req, timeout=300) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            if a == retries-1: return {"error": str(e)}
            time.sleep(5)

mapping = json.load(open(MAP_PATH, encoding="utf-8")) if os.path.exists(MAP_PATH) else {}

jobs = [
    (os.path.join(os.environ.get("LOCALAPPDATA", "C:/Users/USER/AppData/Local"), "Temp", "kyw", "kyw_1.pdf"), "건양대학교_2027_외국인.pdf", "건양대학교"),
    (os.path.join(os.environ.get("LOCALAPPDATA", "C:/Users/USER/AppData/Local"), "Temp", "kyw", "kyw_2.pdf"), "건양대학교_제2캠퍼스_2027_외국인.pdf", "건양대학교"),
]
for path, clean_name, sch in jobs:
    data = open(path, "rb").read()
    b64 = base64.b64encode(data).decode("ascii")
    r = post({"action": "upload", "folderId": FOLDER_ID, "filename": clean_name, "contentBase64": b64})
    if r.get("ok"):
        mapping[path] = {"viewLink": r["viewLink"], "fileId": r["fileId"], "name": clean_name, "size": len(data)}
        json.dump(mapping, open(MAP_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        # upsert DB row (delete existing ba row then insert as 2027)
        try:
            try:
                api("DELETE", "?" + urllib.parse.urlencode({"univ_id": "eq." + sch, "track": "eq.ba"}))
            except Exception:
                pass
            api("POST", "", {"univ_id": sch, "track": "ba", "url": r["viewLink"], "year": "2027", "title": ""})
            print("OK + upserted", sch, "->", r["viewLink"][-45:])
        except Exception as e:
            print("uploaded but DB fail", sch, e)
    else:
        print("FAIL", clean_name, r.get("error", "?"))
    time.sleep(1)

print("done")
