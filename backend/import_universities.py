"""Regenerate backend/import_universities.sql from data.js."""
import json, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
text = (ROOT / "data.js").read_text(encoding="utf-8")

def extract_after(prefix, opener, closer):
    idx = text.find(prefix)
    start = text.find(opener, idx)
    depth = 0
    in_str = False
    esc = False
    quote = ""
    i = start
    while i < len(text):
        ch = text[i]
        if in_str:
            if esc: esc = False
            elif ch == "\\": esc = True
            elif ch == quote: in_str = False
        else:
            if ch in "\"'":
                in_str = True; quote = ch
            elif ch == opener: depth += 1
            elif ch == closer:
                depth -= 1
                if depth == 0:
                    return json.loads(text[start:i+1])
        i += 1
    raise SystemExit("unclosed "+prefix)

univs = extract_after("window.UNIV_KNOWLEDGE", "[", "]")
guides = extract_after("window.UNIV_GUIDES", "{", "}")

def lit(obj):
    return "'" + json.dumps(obj, ensure_ascii=False).replace("'", "''") + "'::jsonb"

def esc(s):
    if s is None: return "NULL"
    return "'" + str(s).replace("'", "''") + "'"

def num(v):
    if v is None or v == "": return "NULL"
    try: return str(int(v))
    except Exception: return "NULL"

lines = ["-- Generated from data.js. Run AFTER supabase_full.sql", "begin;"]
for u in univs:
    uid = u.get("n") or u.get("ek") or u.get("en")
    extra = {k: u.get(k) for k in ("t","i","eng","majors","req_note") if k in u}
    lines.append(
        "insert into universities (id,name_kr,name_en,short_en,loc,type,logo,students,rank,tuition,req,cert,majors_ba,majors_ma,extra) values ("
        + ",".join([
            esc(uid), esc(u.get("n") or ""), esc(u.get("en") or ""), esc(u.get("es") or ""),
            esc(u.get("loc") or ""), esc(u.get("type") or "univ"), esc(u.get("logo") or ""),
            num(u.get("stu")), num(u.get("rk")),
            lit(u.get("tuition") or {}), lit(u.get("req") or {}), lit(u.get("cert") or {}),
            lit(u.get("majors_ba") or []), lit(u.get("majors_ma") or []), lit(extra),
        ])
        + ") on conflict (id) do update set name_kr=excluded.name_kr, name_en=excluded.name_en, short_en=excluded.short_en, loc=excluded.loc, type=excluded.type, logo=excluded.logo, students=excluded.students, rank=excluded.rank, tuition=excluded.tuition, req=excluded.req, cert=excluded.cert, majors_ba=excluded.majors_ba, majors_ma=excluded.majors_ma, extra=excluded.extra, updated_at=now();"
    )
ids = {u.get("n") for u in univs}
for name, tracks in guides.items():
    if not isinstance(tracks, dict) or name not in ids: continue
    for track, url in tracks.items():
        if not url: continue
        lines.append(
            "insert into university_guides (univ_id, track, url) values ("
            + esc(name) + "," + esc(track) + "," + esc(url)
            + ") on conflict (univ_id, track) do update set url=excluded.url;"
        )
lines.append("commit;")
out = ROOT / "backend" / "import_universities.sql"
out.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("wrote", out, "univs", len(univs))
