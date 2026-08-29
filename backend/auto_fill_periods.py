#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto-fill application deadlines (period) into verified_kb.json from the local
adiga 2027 foreigner PDFs. Run daily after the adiga scrape so newly published
2027 guides get their deadlines extracted automatically.

Flow:
  1. Scan the adiga 2027 foreigner PDF folder for schedule sections
     (전형일정/원서접수/모집기간) using pymupdf.
  2. Extract a compact application-window string (best-effort, from the date
     context around schedule keywords).
  3. Map scan school name -> verified_kb school name (alias table for mismatches).
  4. Update verified_kb.json: schools[].period / master[].period / period_notes
     only when we have a confident window and the current value is vague/missing.
  5. Write _daily_period_new.json with the diff (school -> new period) so the
     cron can report "new deadlines today".

Run:  python backend/auto_fill_periods.py
"""
import json
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
KB_PATH = os.path.join(BASE, "verified_kb.json")
SCAN_PATH = os.path.join(BASE, "_period_scan.json")
PDF_DIR = r"C:/Users/USER/내 드라이브/02_Crawling_Sheet/University_Project/adiga_2027_외국인_모집요강/외국인"
OUT_NEW = os.path.join(BASE, "_daily_period_new.json")

import pymupdf  # fitz

# --- schedule section keywords + date regex (mirrors _scan_periods.py) -------
SCHED_KW = ["전형일정", "모집일정", "원서접수", "접수기간", "모집기간", "지원일정", "원서 접수", "입학원서 제출"]

DATE_RE = re.compile(
    r"(?:20\d{2}\s*[.\-년]\s*)?\d{1,2}\s*[.\-월]\s*\d{1,2}"
    r"(?:\s*[\(（]\s*[월화수목금토일]\s*[\)）])?"
    r"(?:\s*[~∼\-–]\s*(?:20\d{2}\s*[.\-년]\s*)?\d{1,2}\s*[.\-월]\s*\d{1,2}"
    r"(?:\s*[\(（]\s*[월화수목금토일]\s*[\)）])?)?"
)

# scan filename -> verified_kb school name (when they differ)
NAME_ALIAS = {
    "연세대학교(미래)": "연세대학교",
    "한양대학교": "한양대학교(ERICA)",  # adiga PDF may just say 한양대학교
    "대전가톨릭대학교": "대전가톨릭대학교",
    "한서대학교": "한서대학교",
}


def extract_text(path):
    try:
        doc = pymupdf.open(path)
        txt = ""
        for p in doc:
            txt += p.get_text()
        doc.close()
        return txt
    except Exception as e:
        return f"__ERR__ {e}"


def normalize_date(d):
    """'2026. 7. 6' / '2026.09.01(월)' / '2026. 9.  1' -> '2026.7.6'"""
    # strip weekday parentheses like (월) (금)
    d = re.sub(r"[\(（][월화수목금토일][\)）]", "", d)
    d = re.sub(r"\s+", "", d)
    d = d.replace("년", ".").replace("월", ".").replace("-", ".")
    parts = [p for p in re.split(r"[.\s]+", d) if p]
    if len(parts) >= 3:
        try:
            return f"{parts[0]}.{int(parts[1])}.{int(parts[2])}"
        except ValueError:
            return d
    return d


def complete_end(start, end_raw):
    """Complete a year-less end date (e.g. '10. 23') using the start's year.
    Returns '2026.10.23' or None if unparseable."""
    end_raw = re.sub(r"[\(（][월화수목금토일][\)）]", "", end_raw)
    end_raw = re.sub(r"\s+", "", end_raw)
    end_raw = end_raw.replace("년", ".").replace("월", ".").replace("-", ".")
    parts = [p for p in re.split(r"[.\s]+", end_raw) if p]
    if len(parts) >= 2:
        try:
            return f"{start[:4]}.{int(parts[0])}.{int(parts[1])}"
        except ValueError:
            return None
    return None


def valid_range(period):
    """Reject obviously wrong ranges (day 0, day>31, month>12, end before start)."""
    m = re.match(r"^(\d{4})\.(\d{1,2})\.(\d{1,2})~(\d{4})\.(\d{1,2})\.(\d{1,2})$", period)
    if not m:
        return False
    sy, sm, sd, ey, em, ed = (int(x) for x in m.groups())
    if not (1 <= sm <= 12 and 1 <= sd <= 31 and 1 <= em <= 12 and 1 <= ed <= 31):
        return False
    if (sy, sm, sd) > (ey, em, ed):
        return False
    return True


def extract_period_from_pdf(path):
    """Return (period_str, confidence) or (None, 0)."""
    txt = extract_text(path)
    if txt.startswith("__ERR__"):
        return None, 0
    lines = txt.split("\n")
    for i, line in enumerate(lines):
        if any(k in line for k in SCHED_KW):
            ctx = " ".join(x.strip() for x in lines[max(0, i - 1):i + 8])
            dates = DATE_RE.findall(ctx)
            if not dates:
                continue
            # first date containing a full year = start; the following date = end
            starts, ends = [], []
            for d in dates:
                clean = re.sub(r"\s+", " ", d).strip()
                m = re.match(
                    r"^((?:20\d{2}\s*[.\-]\s*)?\d{1,2}\s*[.\-]\s*\d{1,2})"
                    r"(?:\s*[~∼\-–]\s*((?:20\d{2}\s*[.\-]\s*)?\d{1,2}\s*[.\-]\s*\d{1,2}))?$",
                    clean,
                )
                if not m:
                    continue
                if re.search(r"20\d{2}", m.group(1)):
                    starts.append(m.group(1))
                    if m.group(2):
                        ends.append(m.group(2))
                elif m.group(2) and re.search(r"20\d{2}", m.group(2)):
                    ends.append(m.group(2))
                elif not starts:
                    pass  # year-less standalone date before any start -> ignore
            # pair: take first full-year start; end = first following date in context
            if not starts:
                continue
            start = normalize_date(starts[0])
            end = None
            if ends:
                end_raw = ends[0]
                if re.match(r"20\d{2}", end_raw):
                    end = normalize_date(end_raw)
                else:
                    end = complete_end(start, end_raw)
            else:
                # fall back to the next year-less date token after the start in the raw list
                for d in dates:
                    if re.search(r"20\d{2}", re.sub(r"\s+", "", d)):
                        continue
                    m2 = re.match(r"^(\d{1,2}\s*[.\-]\s*\d{1,2})", re.sub(r"\s+", " ", d).strip())
                    if m2:
                        end = complete_end(start, m2.group(1))
                        break
            if end:
                return f"{start}~{end}", 0.9
            return f"{start}~", 0.6
    return None, 0


def main():
    if not os.path.isdir(PDF_DIR):
        print(f"[auto-fill] PDF dir not found: {PDF_DIR}")
        return

    kb = json.load(open(KB_PATH, encoding="utf-8"))

    results = {}
    for fn in sorted(os.listdir(PDF_DIR)):
        if not fn.lower().endswith(".pdf"):
            continue
        path = os.path.join(PDF_DIR, fn)
        m = re.match(r"^\d+_(.+?)(?:\[.*?\])?_20\d+_외국인\.pdf$", fn)
        school = m.group(1) if m else fn
        period, conf = extract_period_from_pdf(path)
        if period and valid_range(period):
            results[school] = {"period": period, "conf": conf, "file": fn}
        elif period:
            print(f"[auto-fill] rejected invalid range for {school}: {period}")

    print(f"[auto-fill] scanned {len(results)} PDFs with extractable periods")

    new_periods = {}
    for scan_name, info in results.items():
        kb_name = NAME_ALIAS.get(scan_name, scan_name)
        period = info["period"]

        def better(cur):
            # replace if current is missing/vague/dangling, or new has a full range
            if not cur:
                return True
            if cur in ("2027", "2027-1", "2026-2 순수외국인"):
                return True
            if cur.endswith("~") and "~" in period and not period.endswith("~"):
                return True
            return False

        # try BA schools section
        d = kb["schools"].get(kb_name)
        if d is not None:
            cur = d.get("period")
            if better(cur):
                d["period"] = period
                new_periods[kb_name] = period
            continue
        # try master section
        d = kb.get("master", {}).get("schools", {}).get(kb_name)
        if d is not None:
            cur = d.get("period")
            if better(cur):
                d["period"] = period
                new_periods.setdefault(kb_name, period)
            continue
        # fallback: period_notes
        cur = kb.get("period_notes", {}).get(kb_name)
        if better(cur):
            kb.setdefault("period_notes", {})[kb_name] = period
            new_periods.setdefault(kb_name, period)

    json.dump(kb, open(KB_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(new_periods, open(OUT_NEW, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    print(f"[auto-fill] updated {len(new_periods)} schools with deadlines:")
    for name, p in sorted(new_periods.items()):
        print(f"   {name}: {p}")


if __name__ == "__main__":
    main()
