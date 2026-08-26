#!/usr/bin/env python3
"""Upload the 5 newly-converted HWP->PDF 2027 guides, then upsert their DB rows."""
import os, sys, json, time, base64, urllib.request, glob

BACKEND_URL = "https://script.google.com/macros/s/AKfycbwJ7QxDviSojjDJrRHJokneMebb46aS19ooqYiIuyYQsXdxzcZmyzPDleJXr-7JCnonAQ/exec"
FOLDER_ID   = "1nGH6jaZmqvQJ9yFKZuh-zsDOoeog3lo7"
SRC         = r"C:/Users/USER/내 드라이브/02_Crawling_Sheet/University_Project/adiga_2027_외국인_모집요강/외국인"
MAP_PATH    = r"C:\Users\USER\camnemi-crm\backend\adiga2027_upload_map.json"

key = None
h = open(r"C:\Users\USER\camnemi-crm\index.html", encoding="utf-8").read()
import re
m = re.search(r"DEFAULT_SUPABASE_KEY\s*=\s*'([^']+)'", h)
if m: key = m.group(1)
BASE = "https://zjdvzpylxazfbazioxto.supabase.co/rest/v1/university_guides"

def api(method, path, body=None):
    req = urllib.request.Request(BASE + path, data=json.dumps(body).encode("utf-8") if body else None,
                                 headers={"apikey": key, "Authorization": "Bearer " + key, "Content-Type": "application/json", "Prefer": "return=minimal"})
    req.get_method = lambda: method
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.status

def post(payload, retries=3):
    for a in range(retries):
        try:
            req = urllib.request.Request(BACKEND_URL, data=json.dumps(payload).encode("utf-8"),
                                         headers={"Content-Type": "text/plain;charset=utf-8"})
            with urllib.request.urlopen(req, timeout=300) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            if a == retries-1: return {"error": str(e)}
            time.sleep(4)

def school_from_file(name):
    n = re.sub(r"^[0-9]+_", "", name)
    n = re.sub(r"_2027_외국인(\.\w+)?$", "", n)
    n = re.sub(r"\[[^\]]*\]|\([^)]*\)", "", n).strip()
    return n

mapping = json.load(open(MAP_PATH, encoding="utf-8")) if os.path.exists(MAP_PATH) else {}

targets = ["0000027_제주대학교[본교]_2027_외국인.pdf","0000028_국립창원대학교[본교]_2027_외국인.pdf",
           "0000082_단국대학교[본교]_2027_외국인.pdf","0000113_배재대학교[본교]_2027_외국인.pdf",
           "0000239_중원대학교[본교]_2027_외국인.pdf"]
for name in targets:
    path = os.path.join(SRC, name)
    if not os.path.exists(path):
        print("skip (no pdf)", name); continue
    data = open(path, "rb").read()
    b64 = base64.b64encode(data).decode("ascii")
    clean = name.replace("[본교]","").replace("[제2캠퍼스]","").replace("[분교]","")
    r = post({"action":"upload","folderId":FOLDER_ID,"filename":clean,"contentBase64":b64})
    if r.get("ok"):
        mapping[path] = {"viewLink": r["viewLink"], "fileId": r["fileId"], "name": clean, "size": len(data)}
        json.dump(mapping, open(MAP_PATH,"w",encoding="utf-8"), ensure_ascii=False, indent=1)
        sch = school_from_file(name)
        try:
            try: api("DELETE", "?" + urllib.parse.urlencode({"univ_id":"eq."+sch,"track":"eq.ba"}))
            except Exception: pass
            api("POST", "", {"univ_id":sch,"track":"ba","url":r["viewLink"],"year":"2027","title":""})
            print("OK + upserted", sch, r["viewLink"][-40:])
        except Exception as e:
            print("uploaded but DB fail", sch, e)
    else:
        print("FAIL", name, r.get("error","?"))
    time.sleep(0.8)

if __name__ == "__main__":
    import urllib.parse
