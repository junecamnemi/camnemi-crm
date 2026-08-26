#!/usr/bin/env python3
"""Insert 2027 admission-guide rows into university_guides.

Sources:
  A) adiga2027_upload_map.json  — 58 uploaded PDFs (univ -> viewLink)
  B) _guide_2027_master.json     — 34 schools with 2027_own (direct URL), plus notes

For BA track 2027: use the adiga upload link for schools that were adiga-downloaded,
else the own-site URL when ba_status == 2027_own.
Also inserts 2027 MA guides when the master marks ma 2027 (currently few: 고려대 ma 2027).
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
    # 0002748_가야대학교_2027_외국인.pdf -> 가야대학교 (strip campus tags)
    n = re.sub(r"^[0-9]+_", "", name)
    n = re.sub(r"_2027_외국인(\.\w+)?$", "", n)
    n = re.sub(r"\[[^\]]*\]|\([^)]*\)", "", n).strip()
    return n

def main():
    # A) adiga uploads
    upmap = json.load(open(r"C:\Users\USER\camnemi-crm\backend\adiga2027_upload_map.json", encoding="utf-8"))
    # B) master
    master = json.load(open(r"C:\Users\USER\camnemi-crm\backend\_guide_2027_master.json", encoding="utf-8"))
    master_by_school = {r["school"]: r for r in master}

    # build school -> adiga link (BA)
    adiga_ba = {}   # school -> viewLink
    for path, v in upmap.items():
        sch = school_from_file(os.path.basename(path))
        adiga_ba.setdefault(sch, []).append(v["viewLink"])

    inserts = []  # (univ_id, track, url, year, title)
    for sch, links in adiga_ba.items():
        # prefer the first/main campus link
        url = links[0]
        title = ""
        md = master_by_school.get(sch)
        if md: title = md.get("ba_title") or ""
        inserts.append((sch, "ba", url, "2027", title))

    # own-site 2027 guides (BA)
    for row in master:
        if row.get("ba_status") in ("2027_own", "2027_guide") and row.get("ba_url"):
            sch = row["school"]
            if sch not in adiga_ba:  # don't override an uploaded adiga link
                inserts.append((sch, "ba", row["ba_url"], "2027", row.get("ba_title") or ""))

    # MA 2027 (from master where ma_status == 2027_own / 2027_guide)
    for row in master:
        if row.get("ma_status") in ("2027_own", "2027_guide") and row.get("ma_url"):
            inserts.append((row["school"], "ma", row["ma_url"], "2027", row.get("ma_title") or ""))

    # dedupe
    seen = set(); final = []
    for ins in inserts:
        k = (ins[0], ins[1], ins[2], ins[3])
        if k not in seen:
            seen.add(k); final.append(ins)

    print(f"Total 2027 inserts: {len(final)}")
    print(f"  BA: {sum(1 for x in final if x[1]=='ba')}  MA: {sum(1 for x in final if x[1]=='ma')}  lang: {sum(1 for x in final if x[1]=='lang')}")

    # delete any existing 2027 rows (idempotent rerun), then insert
    # (no id col; delete by year=2027)
    try:
        api("DELETE", "?year=eq.2027")
        print("cleared existing 2027 rows")
    except Exception as e:
        print("clear note:", e)

    # batch insert (Supabase POST supports array for bulk insert)
    rows = [{"univ_id": a, "track": b, "url": c, "year": d, "title": e} for a,b,c,d,e in final]
    try:
        st = api("POST", "", rows)
        print("insert status:", st)
    except Exception as e:
        print("batch insert failed:", e)
        # fallback: one by one
        for r in rows:
            try: api("POST", "", r)
            except Exception as e2: print("  fail", r["univ_id"], e2)
    json.dump({"inserts": final}, open(r"C:\Users\USER\camnemi-crm\backend\inserted_2027.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
    print("saved inserted_2027.json")

if __name__ == "__main__":
    main()
