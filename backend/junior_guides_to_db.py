#!/usr/bin/env python3
"""junior_guides_to_db.py — insert junior-college 2026 guides into university_guides
(track='junior'), using the Drive upload map from upload_junior2026.py."""
import os, re, json, urllib.request, urllib.parse

BASE = os.path.dirname(os.path.abspath(__file__))
MAP = os.path.join(BASE, "junior2026_upload_map.json")
H = open(r"C:\Users\USER\camnemi-crm\index.html", encoding="utf-8").read()
KEY = re.search(r"DEFAULT_SUPABASE_KEY\s*=\s*'([^']+)'", H).group(1)
URL = "https://zjdvzpylxazfbazioxto.supabase.co"
REST = URL + "/rest/v1/university_guides"

def api(method, path, body=None, prefer=None):
    hdr = {"apikey": KEY, "Authorization": "Bearer " + KEY, "Content-Type": "application/json",
           "Accept": "application/json"}
    if prefer: hdr["Prefer"] = prefer
    req = urllib.request.Request(URL + "/rest/v1/" + path, data=(json.dumps(body).encode() if body else None),
                                 method=method, headers=hdr)
    with urllib.request.urlopen(req, timeout=30) as r:
        t = r.read().decode()
        return json.loads(t) if t.strip() else None

# known junior ids
univs = api("GET", "universities?select=id,type&type=eq.junior&limit=300")
jids = [u["id"] for u in univs]
print("junior ids:", len(jids))

def norm(name):
    n = name
    for suf in ["_전문학사_외국인모집요강","_전문학사_모집요강","_전문학사학위심화_모집요강",
                "_전문학사_입학안내(렌더)","_전문학사_입학안내","_전문학사_모집요강.pdf",
                "_모집요강","_입학안내(렌더)"]:
        n = n.replace(suf, "")
    n = n.replace(".pdf","").strip()
    return n

OVER = {
    "_chsu_guide.pdf": "충북보건과학대학교",
    "_du_ENG.pdf": "동서울대학교",
    "_du_KOR.pdf": "동서울대학교",
}
# English-version junior guides (detected by content scan)
EN_FILES = {"_du_ENG.pdf", "거제대학교_전문학사_모집요강.pdf",
            "배화여자대학교_전문학사_모집요강.pdf", "서울예술대_전문학사_모집요강.pdf"}

def match(name):
    if name in OVER: return OVER[name]
    n = norm(name)
    # exact first
    for j in jids:
        if j == n: return j
    # starts/contains
    for j in jids:
        if j.startswith(n) or n.startswith(j.replace("대학교","").replace("대학","")):
            return j
    return None

mapping = json.load(open(MAP, encoding="utf-8"))
rows = []
unmatched = []
for path, info in mapping.items():
    if not info.get("viewLink"): continue
    base = os.path.basename(path)
    jid = match(base)
    if not jid:
        unmatched.append(base); continue
    rows.append({"univ_id": jid, "track": "junior", "url": info["viewLink"],
                 "year": "2026", "title": "2026 전문학사 모집요강",
                 "en": base in EN_FILES})
print("rows to upsert:", len(rows), "| unmatched:", len(unmatched))
for u in unmatched[:20]: print("   unmatched:", u)
json.dump(rows, open(os.path.join(BASE,"_junior_guide_rows.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
print("saved _junior_guide_rows.json")
