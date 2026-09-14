#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Scan ALL local 모집요강 PDFs to detect the application/submission system, by level.

Levels = the adiga folders:
  외국인(학부) / 전문대학 / 대학원 / 어학연수
Output: _apply_systems_pdf.json with per-school detected systems + evidence snippet.
"""
import os, re, json, glob, collections

UP = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project"
FOLDERS = {
    "학부": ["adiga_2026_외국인_모집요강", "adiga_2027_외국인_모집요강"],
    "전문대": ["adiga_2026_전문대학_모집요강"],
    "대학원": ["adiga_2026_대학원_모집요강", "adiga_2027_대학원_모집요강"],
    "어학연수": ["adiga_2026_어학연수_모집요강", "adiga_2027_어학연수_모집요강"],
}
PATS = [
    ("유웨이어플라이", re.compile(r"유웨이|uway|uwayapply", re.I)),
    ("진학어플라이", re.compile(r"진학어플라이|진학사|jinhak", re.I)),
    ("이메일", re.compile(r"이메일|메일\s*접수|E-?mail|@[a-zA-Z0-9._\-]+\.(ac\.kr|com|kr|org|edu)")),
    ("홈페이지", re.compile(r"홈페이지|온라인\s*접수|인터넷\s*접수|입학\s*홈페이지|웹\s*접수|ipsi\.|apply\.|입학원서\s*작성")),
    ("우편", re.compile(r"우편\s*접수|우편\s*제출|등기우편")),
    ("방문", re.compile(r"방문\s*접수|내방\s*접수")),
]

def level_of(path):
    for lvl, dirs in FOLDERS.items():
        if any(d in path for d in dirs):
            return lvl
    return None

def school_of(fn):
    s = re.sub(r"^\d+_", "", fn)
    s = re.sub(r"_?(2026|2027|외국인|전문학사|대학원|한국어교육원|모집요강|입학안내|\(렌더\)|\[본교\]|\[제2캠퍼스\]).*$", "", s)
    return s.strip("_ -") or fn

def main():
    import pymupdf
    out = collections.defaultdict(dict)
    files = []
    for lvl, dirs in FOLDERS.items():
        for d in dirs:
            files += [(lvl, p) for p in glob.glob(os.path.join(UP, d, "**", "*.pdf"), recursive=True)]
    print(f"스캔 대상 PDF: {len(files)}")
    ok = 0
    for lvl, p in files:
        fn = os.path.basename(p)
        try:
            doc = pymupdf.open(p)
            t = "\n".join(doc[i].get_text() for i in range(min(len(doc), 60)))
            doc.close()
        except Exception:
            continue
        if len(t.strip()) < 100:
            continue
        t2 = re.sub(r"[\s\x00-\x1f]+", " ", t)
        hits, ev = [], {}
        for name, pat in PATS:
            m = pat.search(t2)
            if m:
                hits.append(name)
                ev[name] = t2[max(0, m.start()-60):m.start()+90]
        if hits:
            out[lvl][school_of(fn)] = {"file": fn, "systems": hits, "evidence": ev}
            ok += 1
    json.dump(out, open(r"C:\Users\USER\camnemi-crm\backend\_apply_systems_pdf.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"탐지: {ok}개\n")
    for lvl in ["학부", "전문대", "대학원", "어학연수"]:
        d = out.get(lvl, {})
        c = collections.Counter()
        for s, v in d.items():
            for x in v["systems"]:
                c[x] += 1
        print(f"=== {lvl}: {len(d)}개 탐지 ===")
        for k, v in c.most_common():
            print(f"   {k}: {v}")
        print()

if __name__ == "__main__":
    main()
