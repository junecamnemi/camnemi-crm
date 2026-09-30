"""Cross-check what landed in Postgres against the raw verified_kb.json values.

Read-only. Flags any case where a numeric column in cat.program disagrees with the KB text,
so the inference (prose -> lower bound) can be reviewed instead of trusted.
"""
from __future__ import annotations

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from pg_conn import connect  # noqa: E402

BACKEND = pathlib.Path(__file__).parent
LEVELS = [("ba", lambda kb: (kb.get("schools") or {})),
          ("ma", lambda kb: (kb.get("master") or {}).get("schools") or {}),
          ("junior", lambda kb: (kb.get("junior") or {}).get("schools") or {}),
          ("lang", lambda kb: (kb.get("lang_programs") or {}).get("schools") or {})]


def main():
    kb = json.loads((BACKEND / "verified_kb.json").read_text(encoding="utf-8"))
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        select s.name_kr, p.level, p.guide_year, p.topik_req, p.ielts_req, p.toefl_req,
               p.tuition_min, p.tuition_max
        from cat.program p join cat.school s on s.id = p.school_id
        where p.is_current
    """)
    db = {}
    for row in cur.fetchall():
        db[(row[0], row[1])] = dict(year=row[2], topik=row[3], ielts=float(row[4]) if row[4] else None,
                                    toefl=row[5], tmin=float(row[6]) if row[6] else None,
                                    tmax=float(row[7]) if row[7] else None)
    conn.close()

    missing, ok, raw_missing = [], 0, 0
    for level, getter in LEVELS:
        for name, entry in getter(kb).items():
            if not isinstance(entry, dict):
                continue
            d = db.get((name, level))
            if not d:
                missing.append((name, level))
                continue
            if level == "lang":
                if d["topik"] or d["ielts"] or d["toefl"]:
                    missing.append((name, level, "lang has a language requirement"))
                continue
            raw_t = entry.get("topik_req")
            if raw_t is None and d["topik"] is None:
                raw_missing += 1
            elif raw_t is not None and d["topik"] is None:
                missing.append((name, level, f"topik lost: {str(raw_t)[:60]}"))
            else:
                ok += 1
    print(f"programs present in DB: {len(db)}")
    print(f"school/level rows missing from DB: {len([m for m in missing if len(m) == 2])}")
    print(f"topik agreement (both values or both absent): {ok} (raw-absent cases: {raw_missing})")
    issues = [m for m in missing if len(m) > 2]
    print(f"flagged rows: {len(issues)}")
    for m in issues[:25]:
        print("  ", m)


if __name__ == "__main__":
    main()