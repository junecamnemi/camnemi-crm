#!/usr/bin/env python3
"""Upload Bora's converted photo JPG to her Drive folder, then update her docs."""
import os, json, base64, re, time, urllib.request, urllib.parse

BACKEND_URL = "https://script.google.com/macros/s/AKfycbwJ7QxDviSojjDJrRHJokneMebb46aS19ooqYiIuyYQsXdxzcZmyzPDleJXr-7JCnonAQ/exec"
h = open(r"C:\Users\USER\camnemi-crm\index.html", encoding="utf-8").read()
m = re.search(r"DEFAULT_SUPABASE_KEY\s*=\s*'([^']+)'", h)
key = m.group(1)
BASE = "https://zjdvzpylxazfbazioxto.supabase.co/rest/v1/customers"

# Bora's folder id from earlier scan
FOLDER_ID = "1nkFU2spQC9EIK3b7aDXLSPZrFkqv0Rmu"

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

def api(method, path, body=None):
    req = urllib.request.Request(BASE + path, data=json.dumps(body).encode("utf-8") if body else None,
                                 headers={"apikey": key, "Authorization": "Bearer " + key, "Content-Type": "application/json", "Prefer": "return=representation"})
    req.get_method = lambda: method
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))

# 1. upload JPG to Bora's folder
data = open(r"C:\Users\USER\camnemi-crm\backend\_bora_photo.jpg", "rb").read()
b64 = base64.b64encode(data).decode("ascii")
r = post({"action": "uploadCustomerFile", "folderId": FOLDER_ID, "filename": "Bora_Sreyka_Photo.jpg", "contentBase64": b64})
print("upload:", r.get("ok"), r.get("viewLink") or r.get("error","?"))

# 2. add the JPG to Bora's docs in DB
# find her rows
rows = api("GET", "?" + urllib.parse.urlencode({"name": "eq.BORA SREYKA"}))
for row in rows:
    docs = row.get("docs") or []
    # remove the old PDF photo, add the new JPG
    new_docs = [d for d in docs if not re.search(r'photo|picture|사진', d.get("name",""))]
    new_docs.append({"url": r["viewLink"], "mime": "image/jpeg", "name": "Bora_Sreyka_Photo.jpg", "size": len(data)})
    upd = api("PATCH", "?" + urllib.parse.urlencode({"id": "eq." + row["id"]}), {"docs": new_docs})
    print("updated row", row["id"], "docs now", len(new_docs))
print("done")
