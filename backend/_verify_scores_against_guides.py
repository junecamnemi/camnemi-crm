"""Verify every published requirement that `req_verified=false` against its own guide PDF.

Deterministic: the same keyword-adjacent parsers that produced the values are re-run on the guide's
full text (all pages), so the comparison is text evidence vs published number — no model involved.

Output: _verify_scores_report.json  (agree / text_says_other / not_stated / no_pdf per row)
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


def find_pdf(file_name: str, school: str, level: str):
    """Locate a guide PDF by its recorded file name, then by school token."""
    if not file_name:
        file_name = ""
    stem = os.path.splitext(file_name)[0]
    key = re.sub(r"^\d+_", "", stem)
    key = re.sub(r"\[[^\]]*\]", "", key).strip()
    cands = []
    for root in (os.path.join(LIB, level), os.path.join(LIB, "_archive")):
        if not os.path.isdir(root):
            continue
        for dirpath, _dirs, files in os.walk(root):
            for f in files:
                if not f.lower().endswith(".pdf"):
                    continue
                if key and key[:14] in f:
                    cands.append(os.path.join(dirpath, f))
                elif school and school.replace("국립", "") in f:
                    cands.append(os.path.join(dirpath, f))
    return cands[0] if cands else None


def guide_text(path: str) -> str:
    try:
        doc = pymupdf.open(path)
    except Exception as exc:                                    # unreadable / broken file
        return f"__ERR__{exc}"
    parts = []
    for page in doc:
        try:
            parts.append(page.get_text())
        except Exception:
            pass
    return "\n".join(parts)


def main():
    import psycopg
    from pg_conn import connect
    rows = []
    with connect() as conn, conn.cursor() as cur:
        cur.execute("""
            select s.name_kr, p.level, p.topik_req, p.ielts_req, p.toefl_req, p.toefl_scale,
                   coalesce(g.file_name, ''), p.id::text
              from cat.program p
              join cat.school s on s.id = p.school_id
              left join cat.guide_document g on g.id = p.source_doc_id
             where p.req_verified is false and p.is_current and p.status = 'active'
             order by s.name_kr
        """)
        rows = cur.fetchall()

    out = []
    for name, level, topik, ielts, toefl, scale, fname, pid in rows:
        lvl = {"ba": "ba", "ma": "ma", "junior": "junior", "lang": "lang"}.get(level, "ba")
        path = find_pdf(fname, name, lvl)
        rec = dict(school=name, level=level, file=fname, pdf=path, published=dict(
            topik=topik, ielts=float(ielts) if ielts is not None else None,
            toefl=float(toefl) if toefl is not None else None, toefl_scale=scale))
        if not path:
            rec["verdict"] = "no_pdf"
            out.append(rec)
            continue
        text = guide_text(path)
        if text.startswith("__ERR__") or len(text.strip()) < 200:
            rec["verdict"] = "no_text"
            rec["note"] = text[:120] if text.startswith("__ERR__") else f"text={len(text.strip())}"
            out.append(rec)
            continue
        from_text = dict(
            topik=S.score_lower_bound(text, "topik"),
            ielts=S.score_lower_bound(text, "ielts"),
            toefl=S.toefl_from_text(text)[0],
            toefl_scale=S.toefl_from_text(text)[1])
        rec["from_guide_text"] = from_text
        diffs = []
        for k in ("topik", "ielts", "toefl"):
            pub, txt = rec["published"][k], from_text[k]
            if pub is None:
                continue
            if txt is None:
                diffs.append(f"{k}: published {pub} but guide text states none")
            elif abs(float(pub) - float(txt)) > 0.001:
                diffs.append(f"{k}: published {pub} vs text {txt}")
        rec["verdict"] = "agree" if not diffs else "text_says_other"
        rec["diffs"] = diffs
        out.append(rec)

    summary = {}
    for r in out:
        summary[r["verdict"]] = summary.get(r["verdict"], 0) + 1
    json.dump(out, open(os.path.join(BASE, "_verify_scores_report.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("rows:", len(out), "| verdicts:", summary)
    for r in out:
        if r["verdict"] in ("text_says_other",):
            print(f"  MISMATCH {r['school']} [{r['level']}] {r['diffs']}  ({r['file']})")
    for r in out:
        if r["verdict"] == "agree":
            print(f"  agree    {r['school']} [{r['level']}] {r['published']['topik']}/"
                  f"{r['published']['ielts']}/{r['published']['toefl']}")
    print("report -> _verify_scores_report.json")


if __name__ == "__main__":
    main()