#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Shared guide-PDF resolver.

Why this exists: guide_section() originally tried only `guides/<level>/<year>/<basename>` for
2026/2027 and gave up, so ~18 of 19 "no local guide" tuition entries were false — the PDFs were
(a) in `guides/_archive/<year>/<level>/`, (b) under the WRONG level folder (a 대학원 guide filed in
ba/2026, a 전문대 guide under junior when the KB row says BA), or (c) stored with a numeric prefix
(`0000203_한양대학교[본교]_2027_외국인.pdf`) that the KB name does not carry.

Resolve order: exact basename anywhere → same name ignoring the `NNNNNN_` prefix → school-stem match
preferring the requested level and the newest year. Personal documents are rejected.
"""
import os, re, json

LIB = r"G:\공유 드라이브\Hermes\Camnemi\02_Crawling_Sheet\University_Project\guides"
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_guide_local_index.json")
YEARS = ["2027", "2026", "2025", "2024", "unknown", ""]
BAD = re.compile(r"조경준|출서류|서류_|계약서|영수증|여권|비자신청서")
INDEX = None


def build_index(force=False):
    global INDEX
    if INDEX is not None and not force:
        return INDEX
    if os.path.exists(CACHE) and not force:
        try:
            INDEX = json.load(open(CACHE, encoding="utf-8"))
            return INDEX
        except Exception:
            pass
    idx = {}
    for dp, dn, fn in os.walk(LIB):
        for f in fn:
            if f.lower().endswith(".pdf"):
                idx[f] = os.path.join(dp, f)
    INDEX = idx
    try:
        json.dump(idx, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False)
    except Exception:
        pass
    return idx


def _key(s):
    """Normalised school key: drop brackets/spaces and the 학교/대학/대학교 suffix."""
    s = re.sub(r"\(.*?\)|\[.*?\]", "", s)
    s = re.sub(r"\s+", "", s)
    return re.sub(r"(대학교|학교|대학)$", "", s).strip()


def _file_school_key(f):
    """The school the FILE claims to be — its leading token ending in 학교/대학/대학교.

    Without this, stem matching picked a DIFFERENT school: 우송정보대학 for 우송대학교,
    한양여자대학교 for 한양대학교, 전남과학대학교 for 전남대학교.
    """
    f2 = re.sub(r"^\d{6,}_", "", f)
    m = re.match(r"^(.{2,20}?(?:대학교|학교|대학))", f2)
    return _key(m.group(1)) if m else None


def _stem(school):
    return _key(school)


def resolve(school, level, hint=""):
    """Return a real path for this school's guide, or None."""
    idx = build_index()
    hint = hint or ""
    base = os.path.basename(hint) if hint else ""
    # 1. exact basename, any folder
    if base and base in idx:
        return idx[base]
    # 2. ignore a NNNNNNN_ prefix
    if base:
        stripped = re.sub(r"^\d{6,}_", "", base)
        for f, p in idx.items():
            if re.sub(r"^\d{6,}_", "", f) == stripped:
                return p
    # 3. school-stem match — prefer the requested level, then the newest year
    lvmap = {"BA": ["ba"], "MA": ["ma"], "전문학사": ["junior", "ba"], "lang": ["lang"]}
    lvs = lvmap.get(level, ["ba", "ma", "junior", "lang"])
    stem = _stem(school)
    if not stem:
        return None
    cands = []
    for f, p in idx.items():
        if BAD.search(f) or stem not in f:
            continue
        fk = _file_school_key(f)
        if fk is not None and fk != stem:
            continue  # a different school with a similar name — never substitute it
        pl = p.replace("/", "\\")
        lvrank = next((i for i, lv in enumerate(lvs) if f"\\{lv}\\" in pl), len(lvs))
        yrank = next((i for i, y in enumerate(YEARS) if f"\\{y}\\" in pl), len(YEARS))
        # prefer guide-ish names over random school PDFs
        nice = 0 if re.search(r"모집요강|요강|외국인|대학원|_ma|_ba|전문학사|한국어교육원", f) else 1
        cands.append((lvrank, yrank, nice, f, p))
    if not cands:
        return None
    cands.sort()
    return cands[0][4]


def read_text(path, max_chars=None):
    try:
        import pymupdf
        doc = pymupdf.open(path)
        t = "".join(doc[i].get_text() for i in range(len(doc)))
        doc.close()
        return t[:max_chars] if max_chars else t
    except Exception:
        return None


OCR_CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_tuition_ocr_text")
_OCR = None


def ocr_text(path, max_pages=14):
    """RapidOCR an image-only guide (local ONNX, 0 tokens). Cached — OCR is slow.

    Guides like 한양대(23p, 0 text chars) / 경민대(0 chars, 4 images) carry no text layer, so
    pymupdf returns '' and the pipeline used to report "no guide". Run this under the venv that
    has rapidocr (C:\\Users\\wisew\\pdf-venv), not the Hermes venv.
    """
    global _OCR
    import hashlib
    key = hashlib.md5((path + f"|{os.path.getmtime(path):.0f}").encode()).hexdigest()[:16]
    os.makedirs(OCR_CACHE, exist_ok=True)
    cf = os.path.join(OCR_CACHE, key + ".txt")
    if os.path.exists(cf):
        return open(cf, encoding="utf-8").read()
    try:
        import io
        import pymupdf, numpy as np
        from PIL import Image
        from rapidocr_onnxruntime import RapidOCR
        if _OCR is None:
            _OCR = RapidOCR()
        doc = pymupdf.open(path)
        texts = []
        for i in range(min(len(doc), max_pages)):
            pix = doc[i].get_pixmap(matrix=pymupdf.Matrix(2.2, 2.2))
            img = np.array(Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB"))
            res, _ = _OCR(img)
            if res:
                texts.append("\n".join(r[1] for r in res))
        doc.close()
        t = "\n".join(texts)
    except Exception as e:
        t = ""
        print(f"   OCR unavailable/failed: {type(e).__name__}: {e}")
    open(cf, "w", encoding="utf-8").write(t)
    return t


if __name__ == "__main__":
    import sys
    if "--reindex" in sys.argv:
        i = build_index(force=True)
        print("indexed", len(i), "pdfs ->", CACHE)
    else:
        for arg in sys.argv[1:]:
            print(arg, "->", resolve(arg, "BA"))