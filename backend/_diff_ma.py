import json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from pg_conn import connect
kb = json.loads(pathlib.Path("verified_kb.json").read_text(encoding="utf-8"))
kbma = set((kb.get("master") or {}).get("schools") or {})
conn = connect(); cur = conn.cursor()
cur.execute("select name_kr, jsonb_array_length(majors_ma), updated_at::date, left(coalesce(req_note,''),50) from public.universities where majors_ma is not null and jsonb_array_length(majors_ma) > 0 order by name_kr")
db = {r[0]: r[1:] for r in cur.fetchall()}
conn.close()
print("db MA rows:", len(db), "| kb MA schools:", len(kbma))
only_db = sorted(set(db) - kbma); only_kb = sorted(kbma - set(db))
print("\n[only in DB -> ghost rows]", len(only_db))
for n in only_db: print("  ", n, "| majors_ma:", db[n][0], "| updated:", db[n][1], "| req_note:", db[n][2][:40])
print("\n[only in KB -> not published to DB]", len(only_kb))
for n in only_kb[:20]: print("  ", n)
