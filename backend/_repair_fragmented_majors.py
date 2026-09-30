"""Repair character-split major lists by re-reading the guide with word coordinates.

Some guides lose every table cell boundary in plain text extraction, so a major list comes back as
individual characters ('솔','브','릿','지'...). Grouping words by their y coordinate rebuilds the rows:
  솔브릿지경영학부 / AI·빅데이터학과 / 글로벌철도학과 / 글로벌미디어AI영상학과 ...

Usage:  python _repair_fragmented_majors.py [--write] [--school 우송대학교]
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pymupdf

BASE = os.path.dirname(os.path.abspath(__file__))
KB = os.path.join(BASE, "verified_kb.json")
LIB = r"G:\공유 드라이브\Hermes\Camnemi\02_Crawling_Sheet\University_Project\guides"
SEP = {" ", "/", "·", ",", "-", "–", "(", ")", "&"}
NAME_RE = re.compile(r"^[◉●○※*\-–\s]*(.+?(?:학부|학과|전공|대학))\s*(?:\(.*\))?\s*$")


def fragmented(lst) -> bool:
    if not lst or len(lst) < 5:
        return False
    frag = sum(1 for x in lst if isinstance(x, str) and len(x.strip()) <= 2 and x.strip() not in SEP)
    return frag / len(lst) >= 0.15


def rows_from_pdf(path: str) -> list:
    """Department-like strings rebuilt from y-grouped words, in page order."""
    out = []
    try:
        doc = pymupdf.open(path)
    except Exception:
        return out
    for page in doc:
        words = page.get_text("words")
        if not words:
            continue
        lines = {}
        for x0, y0, _x1, _y1, w, *_ in words:
            lines.setdefault(round(y0 / 3), []).append((x0, w))
        for key in sorted(lines):
            text = " ".join(w for _x, w in sorted(lines[key]))
            text = re.sub(r"\s+", " ", text).strip()
            # Cut at the first digit (enrolment counts / '*' markers follow the department name).
            left = re.split(r"\d", text)[0]
            left = left.replace("◉", "").replace("●", "").replace("○", "").strip(" ·-–")
            left = re.sub(r"^([A-Z])\s+([A-Z])\s+", r"\1\2", left)     # 'A I 빅데이터학과'
            if not re.search(r"(학부|학과|전공)$", left):
                continue
            if "대학" in left[:-2]:                     # '국제경영대학◉솔브릿지경영학부'
                tail = left.split("대학")[-1].strip()
                if tail and re.search(r"(학부|학과|전공)$", tail):
                    left = tail
            name = re.sub(r"\s+", " ", left).strip().lstrip("★☆•·-– ")
            if re.search(r"면접|해당|참고|비고|안내|모집|전형", name):
                continue
            if len(name) >= 3 and not re.fullmatch(r"[\d\s%*·]+", name):
                out.append(name)
    # order-preserving dedupe
    seen, uniq = set(), []
    for n in out:
        if n not in seen:
            seen.add(n)
            uniq.append(n)
    return uniq


def find_pdf(school: str, level: str):
    """Prefer a guide that actually has a text layer.

    Several schools keep a scanned copy next to the text PDF (우송대: a 52-page 0-text scan sits
    beside the 13-page text guide), so the first name match is not usable.
    """
    cands = []
    for root in (os.path.join(LIB, level), os.path.join(LIB, "_archive")):
        if not os.path.isdir(root):
            continue
        for dirpath, _d, files in os.walk(root):
            for f in files:
                if f.lower().endswith(".pdf") and school.replace("국립", "") in f:
                    cands.append(os.path.join(dirpath, f))
    best = None
    for c in cands:
        try:
            doc = pymupdf.open(c)
            n = sum(len(p.get_text()) for p in doc)
        except Exception:
            continue
        if n > 500 and (best is None or n > best[1]):
            best = (c, n)
    return best[0] if best else (cands[0] if cands else None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--school")
    args = ap.parse_args()

    kb = json.load(open(KB, encoding="utf-8"))
    targets = []
    for sec, key, fld, lvl in (("ba", "schools", "majors", "ba"), ("ma", "master", "majors", "ma"),
                               ("junior", "junior", "majors_sample", "junior")):
        node = kb[key]["schools"] if key != "schools" else kb["schools"]
        for name, entry in node.items():
            if not isinstance(entry, dict):
                continue
            lst = entry.get(fld) or []
            if fragmented(lst) and (not args.school or args.school == name):
                targets.append((name, sec, fld, lvl, entry))

    print(f"fragmented lists: {len(targets)}")
    for name, sec, fld, lvl, entry in targets:
        path = find_pdf(name, lvl)
        old = entry.get(fld) or []
        if not path:
            print(f"  {name} [{sec}]: PDF 없음 — 건너뜀")
            continue
        new = rows_from_pdf(path)
        print(f"\n  {name} [{sec}] {os.path.basename(path)}")
        print(f"    old {len(old)} fragments -> new {len(new)} names")
        for n in new:
            print("      -", n)
        if not new or len(new) < 3:
            print("    결과가 부족해 적용하지 않음")
            continue
        if args.write:
            entry[fld] = new
            entry.setdefault("_corrections", []).append(dict(
                date=__import__("datetime").date.today().isoformat(), field=fld,
                why=f"글자 단위로 쪼개진 목록을 요강 word 좌표 기준 행 재구성으로 교체 "
                    f"({len(old)} 조각 → {len(new)} 학과)"))
    if args.write:
        json.dump(kb, open(KB, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("\n저장 완료:", KB)
    else:
        print("\nDRY RUN — re-run with --write to apply")


if __name__ == "__main__":
    main()