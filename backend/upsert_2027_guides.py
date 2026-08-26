#!/usr/bin/env python3
"""Upsert 2027 admission-guide rows into university_guides (PK = univ_id+track).

For each (univ, track) with a 2027 guide, REPLACE the row (year->2027, url, title).
Schools without a 2027 guide keep their existing (2026) row.
"""
import json, os, re, urllib.request

key = None
h = open(r"C:\Users\USER\camnemi-crm\index.html", encoding="utf-8").read()
m = re.search(r"DEFAULT_SUPABASE_KEY\s*=\s*'([^']+)'", h)
if m: key = m.group(1)
BASE = "https://zjdvzpylxazfbazioxto.supabase.co/rest/v1/university_guides"

def api(method, path, body=None):
    req = urllib.request.Request(BASE + path, data=json.dumps(body).encode("utf-8") if body else None,
                                 headers={"apikey": key, "Authorization": "Bearer " + key,
                                          "Content-Type": "application/json", "Prefer": "return=minimal"})
    req.get_method = lambda: method
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.status

def school_from_file(name):
    n = re.sub(r"^[0-9]+_", "", name)
    n = re.sub(r"_2027_외국인(\.\w+)?$", "", n)
    n = re.sub(r"\[[^\]]*\]|\([^)]*\)", "", n).strip()
    return n

def main():
    upmap = json.load(open(r"C:\Users\USER\camnemi-crm\backend\adiga2027_upload_map.json", encoding="utf-8"))
    master = json.load(open(r"C:\Users\USER\camnemi-crm\backend\_guide_2027_master.json", encoding="utf-8"))
    master_by_school = {r["school"]: r for r in master}

    adiga_ba = {}
    for path, v in upmap.items():
        sch = school_from_file(os.path.basename(path))
        adiga_ba.setdefault(sch, []).append(v["viewLink"])

    # (univ_id, track, url, year, title)
    upserts = []
    for sch, links in adiga_ba.items():
        url = links[0]
        title = (master_by_school.get(sch) or {}).get("ba_title") or ""
        upserts.append((sch, "ba", url, "2027", title))
    for row in master:
        if row.get("ba_status") in ("2027_own", "2027_guide") and row.get("ba_url") and row["school"] not in adiga_ba:
            upserts.append((row["school"], "ba", row["ba_url"], "2027", row.get("ba_title") or ""))
    for row in master:
        if row.get("ma_status") in ("2027_own", "2027_guide") and row.get("ma_url"):
            upserts.append((row["school"], "ma", row["ma_url"], "2027", row.get("ma_title") or ""))

    # dedupe
    seen = set(); final = []
    for u in upserts:
        k = (u[0], u[1])
        if k not in seen:
            seen.add(k); final.append(u)

    print(f"Upserts: {len(final)} (BA={sum(1 for x in final if x[1]=='ba')} MA={sum(1 for x in final if x[1]=='ma')})")

    # upsert: delete existing row then insert (avoids PK conflict)
    ok = 0; fail = 0
    for (univ, track, url, year, title) in final:
        try:
            try:
                api("DELETE", "?" + urllib.parse.urlencode({"univ_id": "eq." + univ, "track": "eq." + track}))
            except Exception:
                pass
            api("POST", "", {"univ_id": univ, "track": track, "url": url, "year": year, "title": title})
            ok += 1
        except Exception as e:
            fail += 1
            print("  fail", univ, track, e)
    print(f"done ok={ok} fail={fail}")
    json.dump({"upserts": final}, open(r"C:\Users\USER\camnemi-crm\backend\upserted_2027.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

if __name__ == "__main__":
    import urllib.parse
    main()
