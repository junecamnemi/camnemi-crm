#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Guide auto-analyzer — NEW 2027 guide PDFs are analyzed the moment they appear.

How it works:
  1. Scans the adiga 2027 외국인 PDF folder for *.pdf files.
  2. Compares against a processed-manifest (_processed_guides.json: filename -> hash).
  3. For each NEW/CHANGED file, extracts from the PDF text:
       - 모집기간/원서접수 (application period)
       - IELTS/TOPIK/TOEFL language requirements
       - major/department names (모집단위)
       - tuition (등록금) when present
       - scholarship keywords
     using pymupdf text extraction + regex.
  4. Updates verified_kb.json (period/lang_req/majors for the matched school)
     and appends an entry to _guide_analysis_log.json (audit trail).
  5. Prints a compact diff so the cron report can list "newly analyzed today".

Designed to be called by the daily cron (after daily_2027_check.py / manual_2027_check.py)
so any guide downloaded since yesterday gets analyzed immediately.
"""
import os, re, json, hashlib, datetime

ADIGA_DIR = r"C:/Users/USER/내 드라이브/02_Crawling_Sheet/University_Project/adiga_2027_외국인_모집요강/외국인"
BASE = r"C:\Users\USER\camnemi-crm\backend"
KB_PATH = os.path.join(BASE, "verified_kb.json")
PROC_PATH = os.path.join(BASE, "_processed_guides.json")
LOG_PATH = os.path.join(BASE, "_guide_analysis_log.json")

# --- extraction helpers ---
def extract_period(text):
    """Find 모집기간/원서접수 dates like 2026.09.01~2026.10.07 or 2026.9.1~10.7."""
    pats = [
        r"(?:원서접수|접수기간|모집기간)[^\n]{0,40}?((?:202[56]|202[67])[.\-년]\s*\d{1,2}[.\-월]\s*\d{1,2}[.\-일]?\s*[~～\-]\s*(?:202[67])?[.\-년]?\s*\d{1,2}[.\-월]\s*\d{1,2}[.\-일]?)",
        r"((?:202[56]|202[67])[.\-년]\s*\d{1,2}[.\-월]\s*\d{1,2}[.\-일]?\s*[~～\-]\s*(?:202[67])?[.\-년]?\s*\d{1,2}[.\-월]\s*\d{1,2}[.\-일]?)",
    ]
    for p in pats:
        m = re.search(p, text)
        if m:
            return re.sub(r"\s+", "", m.group(1) if m.lastindex else m.group(1))
    return None

def extract_ielts(text):
    m = re.search(r"IELTS\s*(\d+\.?\d*)", text)
    return m.group(1) if m else None

def extract_topik(text):
    m = re.search(r"TOPIK\s*(\d+)\s*급", text)
    return m.group(1) if m else None

def extract_toefl(text):
    m = re.search(r"TOEFL\s*(?:iBT)?\s*(\d{2,3})", text)
    return m.group(1) if m else None

def extract_majors(text):
    """Best-effort: lines containing 학과/학부/전공 in the 모집단위 area."""
    hits = []
    for m in re.finditer(r"([가-힣A-Za-z·&()]{2,30}(?:학과|학부|전공))", text):
        s = m.group(1)
        if s not in hits and len(s) >= 4:
            hits.append(s)
        if len(hits) >= 8:
            break
    return hits

def extract_scholarship(text):
    kws = []
    for m in re.finditer(r"([가-힣A-Za-z]{2,20}장학금)", text):
        if m.group(1) not in kws:
            kws.append(m.group(1))
        if len(kws) >= 5:
            break
    return kws


def analyze_pdf(path):
    """Extract key facts from a guide PDF -> dict."""
    import pymupdf
    doc = pymupdf.open(path)
    full = "\n".join(p.get_text() for p in doc)
    doc.close()
    return {
        "period": extract_period(full),
        "ielts": extract_ielts(full),
        "topik": extract_topik(full),
        "toefl": extract_toefl(full),
        "majors": extract_majors(full),
        "scholarships": extract_scholarship(full),
        "has_tuition": bool(re.search(r"(등록금|수업료)", full)),
        "pages": len(full),
    }


def school_name_from_filename(fn):
    parts = fn.split("_")
    name = parts[1] if len(parts) > 2 else fn
    return re.sub(r"\[.*?\]", "", name).strip()


def main():
    today = datetime.date.today().isoformat()
    proc = {}
    if os.path.exists(PROC_PATH):
        try:
            with open(PROC_PATH, encoding="utf-8") as f:
                proc = json.load(f)
        except Exception:
            proc = {}
    log = []
    if os.path.exists(LOG_PATH):
        try:
            with open(LOG_PATH, encoding="utf-8") as f:
                log = json.load(f)
        except Exception:
            log = []

    if not os.path.isdir(ADIGA_DIR):
        print("[guide-analyze] adiga dir missing:", ADIGA_DIR)
        return

    new_entries = []
    for fn in sorted(os.listdir(ADIGA_DIR)):
        if not fn.endswith(".pdf"):
            continue
        path = os.path.join(ADIGA_DIR, fn)
        try:
            h = hashlib.md5(open(path, "rb").read()).hexdigest()
        except Exception:
            continue
        if proc.get(fn) == h:
            continue  # already processed
        school = school_name_from_filename(fn)
        try:
            facts = analyze_pdf(path)
        except Exception as e:
            print(f"[guide-analyze] FAIL {fn}: {e}")
            continue
        entry = {
            "date": today, "file": fn, "school": school,
            "period": facts["period"], "ielts": facts["ielts"],
            "topik": facts["topik"], "toefl": facts["toefl"],
            "majors_sample": facts["majors"][:6],
            "scholarships": facts["scholarships"],
            "has_tuition": facts["has_tuition"],
        }
        log.append(entry)
        new_entries.append(entry)
        proc[fn] = h
        print(f"[guide-analyze] NEW {school}: period={facts['period']} IELTS={facts['ielts']} TOPIK={facts['topik']} majors={len(facts['majors'])}")

        # --- update verified_kb.json if the school matches ---
        if os.path.exists(KB_PATH):
            with open(KB_PATH, encoding="utf-8") as f:
                kb = json.load(f)
            changed = False
            for sec in ["schools"]:
                for name, s in kb.get(sec, {}).items():
                    base = name.replace("(ERICA)", "").strip()
                    if school == base or (school in base and len(school) >= 4) or (base in school and len(base) >= 4):
                        if facts["period"]:
                            s["period"] = facts["period"]
                        if facts["ielts"] and "IELTS" not in str(s.get("lang_req", "")):
                            s["lang_req"] = f"IELTS {facts['ielts']} / " + str(s.get("lang_req", "TOPIK 기반"))
                        s["guide_analyzed"] = today
                        changed = True
                        break
            if changed:
                with open(KB_PATH, "w", encoding="utf-8") as f:
                    json.dump(kb, f, ensure_ascii=False, indent=2)
                print(f"[guide-analyze] → KB updated for {school}")

    with open(PROC_PATH, "w", encoding="utf-8") as f:
        json.dump(proc, f, ensure_ascii=False, indent=1)
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=1)

    print(f"[guide-analyze] done: {len(new_entries)} new guide(s) analyzed today; total processed {len(proc)}")
    for e in new_entries:
        print(f"  ★ {e['school']}: period={e['period']} IELTS={e['ielts']} TOPIK={e['topik']} majors={e['majors_sample'][:3]}")


if __name__ == "__main__":
    main()
