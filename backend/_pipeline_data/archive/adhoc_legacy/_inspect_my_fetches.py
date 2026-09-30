# -*- coding: utf-8 -*-
"""Identify the 4 files my guide_fetch attempts created (all suspect)."""
import re, os, fitz
G = r"G:/공유 드라이브/Hermes/Camnemi/02_Crawling_Sheet/University_Project/guides"
suspects = {
    "ba/2027/선문대학교_외국인모집요강_2027.pdf": "url graduate.sunmoon.ac.kr",
    "ba/2027/한세대학교_외국인모집요강_2027.pdf": "url admission2026_2_kr.pdf",
    "lang/2027/연세대학교_외국인모집요강_2027.pdf": "url graduate.yonsei.ac.kr s_f_guide_2027-1_k.pdf",
    "ma/2027/연세대학교_외국인모집요강_2027.pdf": "url graduate.yonsei.ac.kr s_f_guide_2027-1_k.pdf",
}
for rel, why in suspects.items():
    p = os.path.join(G, rel.replace("/", os.sep))
    if not os.path.exists(p):
        print(f"MISSING {rel}")
        continue
    d = fitz.open(p)
    t = re.sub(r"\s+", " ", "".join(d[i].get_text() for i in range(min(2, d.page_count)))).strip()
    yrs = sorted(set(re.findall(r"20(?:2[4-9])", t)))[:6]
    grad = "대학원" in t[:400] or "Graduate" in t[:400]
    print(f"{rel}")
    print(f"   {os.path.getsize(p):,}B  {d.page_count}p  years={yrs}  mentions_대학원={grad}")
    print(f"   src: {why}")
    print(f"   head: {t[:170]}")
    d.close()