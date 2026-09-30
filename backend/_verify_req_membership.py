"""Rigorous requirement check: is each published score actually stated in its own guide?

The earlier pass compared against the *minimum* number in the whole document, which is unreliable
(한밭대 states IELTS 6.0 for general units and 5.5 for 국제학부; a stray "TOPIK 1급" flips the min).
This pass asks a sharper question — is the published value one of the numbers attached to that test's
keyword anywhere in the guide?

Verdicts per field:
  confirmed    — published value appears next to the keyword
  contradicted — keyword-adjacent numbers exist, but none equals the published value
  not_stated   — the guide never attaches a number to that keyword
  no_pdf / no_text — guide unavailable (scanned or missing)
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pymupdf
import sync_kb_to_postgres as S

BASE = os.path.dirname(os.path.abspath(__file__))
LIB = r"G:\공유 드라이브\Hermes\Camnemi\02_Crawling_Sheet\University_Project\guides"
TEXT_CACHE = {}


def find_pdf(file_name: str, school: str, level: str):
    stem = os.path.splitext(file_name or "")[0]
    key = re.sub(r"^\d+_", "", stem)
    key = re.sub(r"\[[^\]]*\]", "", key).strip()
    hits = []
    for root in (os.path.join(LIB, level), os.path.join(LIB, "_archive")):
        if not os.path.isdir(root):
            continue
        for dirpath, _d, files in os.walk(root):
            for f in files:
                if not f.lower().endswith(".pdf"):
                    continue
                if key and key[:14] in f:
                    hits.append(os.path.join(dirpath, f))
                elif school and school.replace("국립", "") in f:
                    hits.append(os.path.join(dirpath, f))
    return hits[0] if hits else None


def guide_text(path: str) -> str:
    if path in TEXT_CACHE:
        return TEXT_CACHE[path]
    try:
        doc = pymupdf.open(path)
        text = "\n".join(p.get_text() for p in doc)
    except Exception:
        text = ""
    TEXT_CACHE[path] = text
    return text


def adjacent_numbers(text: str, kind: str) -> list:
    """Every number attached to the test keyword, ignoring 'TOPIK iBT' when looking for TOEFL."""
    t = text
    if kind == "toefl":
        t = re.sub(r"topik\s*\(?\s*ibt\s*\)?", " ", t, flags=re.I)
    if kind == "topik":
        pats = [r"topik[^0-9]{0,8}(\d+(?:\.\d+)?)", r"(\d+(?:\.\d+)?)\s*급"]
    elif kind == "ielts":
        pats = [r"ielts[^0-9]{0,10}(\d+(?:\.\d+)?)"]
    else:
        pats = [r"toefl[^0-9]{0,10}(\d+(?:\.\d+)?)", r"ibt[^0-9]{0,8}(\d+(?:\.\d+)?)",
                r"cbt[^0-9]{0,8}(\d+(?:\.\d+)?)", r"pbt[^0-9]{0,8}(\d+(?:\.\d+)?)"]
    out = []
    for p in pats:
        out += [float(x) for x in re.findall(p, t, flags=re.I)]
    return sorted(set(out))


def classify(published, adjacent):
    if published is None:
        return None
    if not adjacent:
        return "not_stated"
    if any(abs(float(published) - a) < 0.001 for a in adjacent):
        return "confirmed"
    return "contradicted"


def main():
    from pg_conn import connect
    with connect() as conn, conn.cursor() as cur:
        cur.execute("""
            select s.name_kr, p.level, p.topik_req, p.ielts_req, p.toefl_req, p.toefl_scale,
                   coalesce(g.file_name, '')
              from cat.program p
              join cat.school s on s.id = p.school_id
              left join cat.guide_document g on g.id = p.source_doc_id
             where p.is_current and p.status = 'active'
               and (p.topik_req is not null or p.ielts_req is not null or p.toefl_req is not null)
             order by s.name_kr
        """)
        rows = cur.fetchall()

    out, counts = [], {}
    for name, level, topik, ielts, toefl, scale, fname in rows:
        lvl = level if level in ("ba", "ma", "junior", "lang") else "ba"
        path = find_pdf(fname, name, lvl)
        rec = dict(school=name, level=level, file=fname,
                   published=dict(topik=topik, ielts=float(ielts) if ielts is not None else None,
                                  toefl=float(toefl) if toefl is not None else None,
                                  toefl_scale=scale), verdicts={})
        if not path:
            rec["verdicts"] = {"_": "no_pdf"}
            out.append(rec)
            counts["no_pdf"] = counts.get("no_pdf", 0) + 1
            continue
        text = guide_text(path)
        if len(text.strip()) < 200:
            rec["verdicts"] = {"_": "no_text"}
            out.append(rec)
            counts["no_text"] = counts.get("no_text", 0) + 1
            continue
        for kind in ("topik", "ielts", "toefl"):
            pub = rec["published"][kind]
            if pub is None:
                continue
            adj = adjacent_numbers(text, kind)
            v = classify(pub, adj)
            rec["verdicts"][kind] = v
            rec.setdefault("adjacent", {})[kind] = adj[:12]
            counts[v] = counts.get(v, 0) + 1
        out.append(rec)

    json.dump(out, open(os.path.join(BASE, "_verify_req_membership.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("programs checked:", len(out), "| field verdicts:", counts)
    print("\n--- CONTRADICTED (published value not attached to the keyword anywhere) ---")
    n = 0
    for r in out:
        bad = {k: v for k, v in r["verdicts"].items() if v == "contradicted"}
        if not bad:
            continue
        n += 1
        print(f"  {r['school']} [{r['level']}] {r['file'][:42]}")
        for k in bad:
            print(f"      {k}: published {r['published'][k]} | guide numbers {r.get('adjacent', {}).get(k)}")
    print(f"\ncontradicted rows: {n}")
    print("report -> _verify_req_membership.json")


if __name__ == "__main__":
    main()