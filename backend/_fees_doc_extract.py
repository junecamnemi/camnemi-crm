#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extract 계열/학과 tuition rows from the downloaded 등록금 documents — deterministic first, vision last.

Why coordinates: these PDFs are printed tables, and `get_text()` returns amounts in scrambled order
(한동대's 계열구분표 yielded "3,857,000 / 0 / 0 / 0 / , / 7 / 5"). `get_text("words")` keeps each
word's x/y, so words are clustered into visual rows (same y band) and ordered by x — that reconstructs
the table without a model.

Guards:
  · LEVEL MATCH — a 학부(학과) table must not fill an MA entry; doc title decides, and a mismatch is
    skipped with a reason rather than merged (한동대's PDF is 2026학년도 대학(학부) 계열구분표).
  · VERBATIM — krw_raw must occur in that page's own text.
  · 입학금/전형료 columns dropped; unit taken from the page's words, never converted if unknown.
Image-only pages (no text layer) are queued to `_fees_doc_vision_todo.json` instead of being guessed.
  python _fees_doc_extract.py
Writes _fees_doc_rows.jsonl
"""
import os, re, json, glob, sys

B = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(B, "_fees_docs.json")
OUT = os.path.join(B, "_fees_doc_rows.jsonl")
VTODO = os.path.join(B, "_fees_doc_vision_todo.json")

AMOUNT = re.compile(r"^\d{1,3}(?:,\d{3}){2,}$|^\d{7,}$")
FEE_HINT = re.compile(r"등록금|수업료|학비")
COLLEGE = re.compile(r"인문|사회|자연|공학|예체능|예능|체능|간호|보건|사범|의학|약학|한의|수산|해양|"
                     r"농림|상경|경상|경영|음악|미술|체육|디자인|계열|학부|학과|전공|대학원|과정")
METRIC = re.compile(r"1인당|인당|장학금|교육비|충원율|경쟁률|취업률|비율|순위|평균|합계|총계|소계|"
                    r"증감|전년|대비|환산|지수|임차료|수수료|이자|감가|비품|소모품|인쇄비|여비|"
                    r"교육과정|특별과정|연수|출장|회의|홍보|전산|시설")
# a row we can trust as a 모집단위 — not merely a word that happens to contain 미술/공학
UNIT_NAME = re.compile(r"계열$|학과$|학부$|전공$|대학원|대학$|과$|과정$|계열\s|학과\s|전공\s|전공심화")
# 등록금이 아닌 문서 유형: 예산서·결산서·교비회계·고지서(개인별)
DOC_TYPE_BAD = re.compile(r"예산|결산|교비|자금계산서|회계|고지서|bill|budget|settlement", re.I)
DROP = re.compile(r"입학금|전형료|기숙|식비|실습비")
LVL = {"BA": (r"학부|학과|신입학|학사", r"대학원|석사|박사"),
       "MA": (r"대학원|석사|박사", r"학부\(|신입학|학사과정"),
       "전문학사": (r"전문학사|전문대|전공심화|학과", r"대학원|석사")}


def rows_by_coords(page):
    """Reconstruct printed table rows: cluster words by y band, order cells by x."""
    words = page.get_text("words")           # x0,y0,x1,y1,word,block,line,word_no
    if not words:
        return []
    words.sort(key=lambda w: (round(w[1] / 6), w[0]))
    lines, cur, cury = [], [], None
    for w in words:
        y = round(w[1] / 6)
        if cury is None or abs(y - cury) <= 1:
            cur.append(w)
            cury = y if cury is None else cury
        else:
            lines.append(sorted(cur, key=lambda z: z[0]))
            cur, cury = [w], y
    if cur:
        lines.append(sorted(cur, key=lambda z: z[0]))
    out = []
    for ln in lines:
        cells, buf, prev_x1 = [], [], None
        for w in ln:
            if prev_x1 is not None and w[0] - prev_x1 > 12:
                cells.append(" ".join(buf))
                buf = []
            buf.append(w[4])
            prev_x1 = w[2]
        if buf:
            cells.append(" ".join(buf))
        out.append(cells)
    return out


def parse_page(page, text, school, level, url, path):
    rows = []
    unit = ("semester" if re.search(r"학기\s*(당|기준|분)", text) else
            "year" if re.search(r"연간|년간|연액|1년", text) else "unknown")
    ym = re.search(r"(20\d\d)\s*학년도", text)
    year = ym.group(1) if ym else None
    for cells in rows_by_coords(page):
        if len(cells) < 2:
            continue
        label = cells[0].strip()
        if not label or not COLLEGE.search(label) or METRIC.search(label):
            continue
        if not UNIT_NAME.search(label):
            continue                 # "미술작품 임차료" matched 미술 — require a 모집단위 shape
        amt_cells = [(i, c) for i, c in enumerate(cells[1:], 1)
                     if AMOUNT.match(c.replace(" ", "")) and not DROP.search(label)]
        if not amt_cells:
            continue
        idx, raw = amt_cells[0]
        krw = int(raw.replace(",", "").replace(" ", ""))
        if not (500_000 <= krw <= 20_000_000):
            continue
        if raw.replace(" ", "") not in text.replace(" ", ""):
            continue                                    # verbatim guard
        rows.append({"school": school, "level": level, "college": label[:60], "krw": krw,
                     "krw_raw": raw, "unit": unit, "page_year": year, "source_url": url,
                     "source_file": os.path.basename(path),
                     "detail_level": "college" if re.search(r"계열|학부|대학$", label) else "department",
                     "basis": "요강/공식 등록금 계열구분표 PDF(좌표 기반 표 재구성)",
                     "verbatim": f"{label} … {raw}"[:160]})
    return rows


def level_ok(title, text_head, level):
    good, bad = LVL.get(level, (None, None))
    if not good:
        return True, ""
    head = (title or "") + " " + text_head[:400]
    if bad and re.search(bad, head) and not re.search(good, head):
        return False, f"레벨 불일치: 문서가 '{re.search(bad, head).group(0)}' 표"
    return True, ""


def main():
    import pymupdf, hashlib
    docs = json.load(open(DOCS, encoding="utf-8"))
    # GUARD 1 — content identity. The first pass handed the SAME bytes
    # (20260129132506V8CW29.PDF, md5 c782be63…) to 숙명여대/한동대/청주대/칼빈대/극동대: a file that
    # is not one school's own table cannot be merged into any of them.
    hashes = {}
    for key, rec in docs.items():
        for d in rec.get("docs", []):
            p = d.get("path")
            if p and os.path.exists(p):
                h = hashlib.md5(open(p, "rb").read()).hexdigest()
                hashes.setdefault(h, []).append(key)
    shared = {h for h, keys in hashes.items() if len({k.split("|")[0] for k in keys}) > 1}
    print(f"shared files across schools: {len(shared)} (will be refused)")
    vision_todo, n_rows, n_files, skipped, refused_shared, refused_name = [], 0, 0, 0, 0, 0
    with open(OUT, "w", encoding="utf-8") as fh:
        for key, rec in docs.items():
            school, level = rec["school"], rec["level"]
            tok = re.sub(r"(대학교|대학|학교)$", "", school).strip()
            for d in rec.get("docs", []):
                path = d.get("path")
                if not path or not os.path.exists(path):
                    continue
                h = hashlib.md5(open(path, "rb").read()).hexdigest()
                if h in shared:
                    refused_shared += 1
                    continue
                if not re.search(r"\.pdf$", path, re.I):
                    vision_todo.append({"school": school, "level": level, "path": path,
                                        "url": d["url"], "why": "image file"})
                    continue
                n_files += 1
                try:
                    doc = pymupdf.open(path)
                except Exception:
                    continue
                text_all = "".join(p.get_text() for p in doc)
                if len(text_all.strip()) < 200:
                    vision_todo.append({"school": school, "level": level, "path": path,
                                        "url": d["url"], "why": "no text layer",
                                        "pages": len(doc)})
                    continue
                # GUARD 2 — the document must name the school it is being merged into.
                if tok and tok not in text_all and tok not in (d.get("page_title") or ""):
                    refused_name += 1
                    doc.close()
                    continue
                title = d.get("page_title") or ""
                if DOC_TYPE_BAD.search(os.path.basename(path) + " " + title) and not re.search(
                        r"등록금\s*계열|계열구분표|일람표", title + text_all[:600]):
                    skipped += 1
                    doc.close()
                    continue
                ok, why = level_ok(title, text_all, level)
                if not ok:
                    skipped += 1
                    continue
                got = []
                for p in doc:
                    t = p.get_text()
                    if not FEE_HINT.search(t) and not FEE_HINT.search(text_all[:200]):
                        continue
                    # YEAR GUARD — a 2015 교비 예산서 must not become 2027 학비.
                    yrs = [int(y) for y in re.findall(r"(20\d\d)\s*학년도", t)] + \
                          [int(y) for y in re.findall(r"(20\d\d)", os.path.basename(path))]
                    if not yrs or max(yrs) < 2025:
                        skipped += 1
                        break
                    got += parse_page(p, t, school, level, d["url"], path)
                if got:
                    rec_out = {"school": school, "level": level, "rows": got,
                               "source_file": os.path.basename(path), "source_url": d["url"]}
                    fh.write(json.dumps(rec_out, ensure_ascii=False) + "\n")
                    n_rows += len(got)
                    print(f"  ✔ {school[:15]:17}[{level:7}] {os.path.basename(path)[:38]:40} rows={len(got)}")
                doc.close()
    json.dump(vision_todo, open(VTODO, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"pdf files scanned={n_files} rows={n_rows} level-mismatch skipped={skipped} "
          f"refused_shared={refused_shared} refused_wrong_school={refused_name} "
          f"vision queue={len(vision_todo)}")
    print("WROTE", OUT)


if __name__ == "__main__":
    main()