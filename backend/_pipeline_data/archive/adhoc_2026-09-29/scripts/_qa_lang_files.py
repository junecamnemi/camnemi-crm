# -*- coding: utf-8 -*-
"""QA scan of every lang guide file: real text? placeholder/CMS junk? Prints a table."""
import os, re, collections
import pymupdf

G = r"G:/공유 드라이브/Hermes/Camnemi/02_Crawling_Sheet/University_Project/guides"
JUNK = re.compile(r"(웹표준|Lazy binding|CMS의 장점|센터 소개\s*$|준비\s*중|페이지를 찾을 수 없|접근이 차단|로그인이 필요|비정상적인 접근|삭제된 게시물|존재하지 않는)", re.I)
GUIDEISH = re.compile(r"(한국어|어학|연수|유학생|모집요강|입학|등록금|수강료|학사일정|Korean|Language)", re.I)
rows = []
for root, dirs, files in os.walk(os.path.join(G, "lang")) + os.walk(os.path.join(G, "_archive", "lang")):
    pass
for base in (os.path.join(G, "lang"), os.path.join(G, "_archive", "lang")):
    for root, dirs, files in os.walk(base):
        for f in files:
            if not f.lower().endswith(".pdf"):
                continue
            p = os.path.join(root, f)
            if open(p, "rb").read(4) != b"%PDF":
                rows.append((f, 0, 0, "NOT-PDF", "")); continue
            try:
                d = pymupdf.open(p)
                t = "".join(d[i].get_text() for i in range(min(8, d.page_count)))
                pages = d.page_count
                d.close()
            except Exception as e:
                rows.append((f, 0, 0, f"ERR:{type(e).__name__}", "")); continue
            t = t.strip()
            verdict = "ok"
            if len(t) < 250:
                verdict = "THIN"
            elif JUNK.search(t) and not GUIDEISH.search(t[:600]):
                verdict = "JUNK"
            rows.append((f, pages, len(t), verdict, t[:70].replace("\n", " ")))
rows.sort(key=lambda r: (r[3] != "ok", r[0]))
c = collections.Counter(r[3] for r in rows)
print("lang files:", len(rows), dict(c))
print()
for f, pages, chars, verdict, head in rows:
    if verdict != "ok":
        print("%-58s %-6s p=%-3d c=%-5d %s" % (f[:58], verdict, pages, chars, head[:60]))
print()
print("--- sample of ok files:")
for f, pages, chars, verdict, head in rows[:8]:
    print("%-58s p=%-3d c=%-5d %s" % (f[:58], pages, chars, head[:56]))