"""List KB (school, level) pairs that the derived stores (consulting_db / data.js) do not carry yet.

coverage_guard reads this file so a recovered-but-unpublished school is reported as PENDING instead
of blocking every publish run. Regenerate after each publish:

  python _pending_publish.py            # report + write backend/_pending_publish.json
"""
from __future__ import annotations

import json
import pathlib

BASE = pathlib.Path(__file__).resolve().parent.parent
KB = BASE / "backend" / "verified_kb.json"
DB = BASE / "backend" / "consulting_db.json"
OUT = BASE / "backend" / "_pending_publish.json"

SECTION = {"BA": "schools", "MA": "master", "전문학사": "junior", "어학연수": "lang_programs"}


def norm(x) -> str:
    import re
    x = re.sub(r"\[.*?\]|\(.*?\)", "", str(x))
    for suf in ["대학원대학교", "대학교", "대학원", "대학", "전문대학", "전문대"]:
        if x.endswith(suf):
            x = x[: -len(suf)]
            break
    if x.endswith("대") and len(x) > 1:
        x = x[:-1]
    return x.replace(" ", "")


def main():
    kb = json.loads(KB.read_text(encoding="utf-8"))
    db = json.loads(DB.read_text(encoding="utf-8"))
    db_index = {}
    for name, sc in db["schools"].items():
        for lvl in (sc.get("programs") or {}):
            db_index[(norm(name), lvl)] = True

    pending = []
    for lvl, sec in SECTION.items():
        node = kb.get(sec) or {}
        schools = node.get("schools", node) if isinstance(node, dict) else {}
        for name, entry in (schools or {}).items():
            if not isinstance(entry, dict):
                continue
            if (norm(name), lvl) not in db_index:
                pending.append(dict(school=name, level=lvl, norm=norm(name),
                                    majors=len(entry.get("majors") or entry.get("majors_sample") or []),
                                    year=entry.get("guide_effective_year") or entry.get("guide_year")))
    OUT.write_text(json.dumps(pending, ensure_ascii=False, indent=1), encoding="utf-8")
    from collections import Counter
    print(f"pending publish: {len(pending)} (school, level) pairs -> {OUT.name}")
    print(" ", dict(Counter(p["level"] for p in pending)))
    for p in pending[:12]:
        print(f"   {p['level']:8s} {p['school']}")


if __name__ == "__main__":
    main()