#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Guide auto-analyzer (full router) — every COLLECTED guide PDF is analyzed and
merged into the CORRECT verified_kb.json section (BA / MA / junior / lang).

Pipeline:
  1. Scan every guide folder (adiga 외국인, own_site, 2027/2026 대학원, 2026 전문대,
     2027/2026 어학연수) — see FOLDER_MAP.
  2. Skip files already processed (md5 in _processed_guides.json).
  3. Extract: 모집기간/원서접수, IELTS/TOPIK/TOEFL, 전공, 등록금 유무, 장학금.
  4. Route to the correct KB section and apply SECTION-APPROPRIATE fields:
        BA   (kb['schools'])                    : period, lang_req, ielts_req/topik_req, guide_analyzed
        MA   (kb['master']['schools'])          : period, lang_req, topik_req/toefl_req, guide_analyzed
        jun  (kb['junior']['schools'])          : period, lang_req, topik_req/ielts_req, guide_analyzed
        lang (kb['lang_programs']['schools'])   : period, d4_eligible, guide_pdf
  5. YEAR-GATING: a 2027 folder is authoritative (may overwrite); a 2026 folder only
     fills fields that are still missing, so 2027 data is never clobbered by 2026.
  6. Image-only PDFs (0 extractable text) are flagged, not merged.
  7. KB is written ONCE at the end (no per-file churn). Audit trail in
     _guide_analysis_log.json; processed manifest in _processed_guides.json.

Called by the daily cron after the guide checks.
"""
import os, re, json, hashlib, datetime

BASE = r"C:\Users\USER\camnemi-crm\backend"
KB_PATH = os.path.join(BASE, "verified_kb.json")
PROC_PATH = os.path.join(BASE, "_processed_guides.json")
LOG_PATH = os.path.join(BASE, "_guide_analysis_log.json")

UP = r"C:/Users/USER/내 드라이브/02_Crawling_Sheet/University_Project"

ADIGA_FOREIGN = f"{UP}/adiga_2027_외국인_모집요강/외국인"

# folder -> (section, authoritative_year)  section ∈ {BA, MA, jun, lang}
FOLDER_MAP = {
    ADIGA_FOREIGN:                                       ("BA",   2027),
    f"{UP}/adiga_2027_외국인_모집요강/own_site":         ("BA",   2027),
    f"{UP}/adiga_2027_대학원_모집요강":                  ("MA",   2027),
    f"{UP}/adiga_2026_대학원_모집요강":                  ("MA",   2026),
    f"{UP}/adiga_2026_전문대학_모집요강":                ("jun",  2026),
    f"{UP}/adiga_2027_전문대학_모집요강":                ("jun",  2027),
    f"{UP}/adiga_2027_어학연수_모집요강":                ("lang", 2027),
    f"{UP}/adiga_2026_어학연수_모집요강":                ("lang", 2026),
}

SECTION_CONTAINER = {
    "BA":   lambda kb: kb["schools"],
    "MA":   lambda kb: kb["master"]["schools"],
    "jun":  lambda kb: kb["junior"]["schools"],
    "lang": lambda kb: kb["lang_programs"]["schools"],
}


# ---------- extraction helpers ----------
def extract_period(text):
    pats = [
        r"(?:원서접수|접수기간|모집기간)[^\n]{0,40}?((?:202[5-7])[.\-년]\s*\d{1,2}[.\-월]\s*\d{1,2}[.\-일]?\s*[~～\-]\s*(?:202[5-7])?[.\-년]?\s*\d{1,2}[.\-월]\s*\d{1,2}[.\-일]?)",
        r"((?:202[5-7])[.\-년]\s*\d{1,2}[.\-월]\s*\d{1,2}[.\-일]?\s*[~～\-]\s*(?:202[5-7])?[.\-년]?\s*\d{1,2}[.\-월]\s*\d{1,2}[.\-일]?)",
    ]
    for p in pats:
        m = re.search(p, text)
        if m:
            return re.sub(r"\s+", "", m.group(1))
    return None

def extract_ielts(text):
    m = re.search(r"IELTS\s*(\d+\.?\d*)", text); return m.group(1) if m else None

def extract_topik(text):
    m = re.search(r"TOPIK[^\d]{0,6}(\d)\s*급", text); return m.group(1) if m else None

def extract_toefl(text):
    m = re.search(r"TOEFL\s*(?:iBT)?\s*(\d{2,3})", text); return m.group(1) if m else None

def extract_majors(text):
    hits = []
    for m in re.finditer(r"([가-힣A-Za-z·&()]{2,30}(?:학과|학부|전공))", text):
        s = m.group(1)
        if s not in hits and len(s) >= 4:
            hits.append(s)
        if len(hits) >= 12:
            break
    return hits

def extract_scholarship(text):
    kws = []
    for m in re.finditer(r"([가-힣A-Za-z]{2,20}장학금?)", text):
        if m.group(1) not in kws:
            kws.append(m.group(1))
        if len(kws) >= 6:
            break
    return kws

def analyze_pdf(path):
    import pymupdf
    doc = pymupdf.open(path)
    full = "\n".join(doc[i].get_text() for i in range(len(doc)))
    doc.close()
    return {
        "period": extract_period(full),
        "ielts": extract_ielts(full),
        "topik": extract_topik(full),
        "toefl": extract_toefl(full),
        "majors": extract_majors(full),
        "scholarships": extract_scholarship(full),
        "has_tuition": bool(re.search(r"(등록금|수업료|tuition)", full, re.I)),
        "text_len": len(full.strip()),
    }


def school_name_from_filename(fn):
    """Extract school name across all folder namings."""
    name = fn[:-4] if fn.lower().endswith(".pdf") else fn
    name = re.sub(r"^\d+[_\-]", "", name)             # strip 0000138_
    parts = name.split("_")
    # own-site / MA naming: {School}_{BA|MA}_{year}
    first = parts[0]
    first = re.sub(r"\[.*?\]", "", first).strip()      # strip [본교]
    return first


def norm(s):
    return re.sub(r"\[.*?\]", "", str(s)).replace("대학교", "").replace("대학", "").replace(" ", "").strip()


def find_key(container, school):
    """Fuzzy-match a school name to a KB key in the given section container."""
    if school in container:
        return school
    ns = norm(school)
    if not ns:
        return None
    for k in container:
        nk = norm(k)
        if nk == ns or (len(ns) >= 3 and (ns in nk or nk in ns)):
            return k
    return None


def apply_update(entry_obj, section, facts, year, today):
    """Write section-appropriate fields. Returns True if changed."""
    changed = False
    authoritative = (year >= 2027)

    if section == "lang":
        if facts["period"] and (authoritative or not entry_obj.get("period")):
            entry_obj["period"] = facts["period"]; changed = True
        if entry_obj.get("d4_eligible") is None:
            entry_obj["d4_eligible"] = True; changed = True
        return changed

    if section == "BA":
        if facts["period"] and (authoritative or not entry_obj.get("period")):
            entry_obj["period"] = facts["period"]; changed = True
        if facts["ielts"] and (authoritative or entry_obj.get("ielts_req") in (None, "", "null")):
            entry_obj["ielts_req"] = float(facts["ielts"]) if re.match(r"^\d", str(facts["ielts"])) else facts["ielts"]
            changed = True
        if facts["topik"] and (authoritative or not entry_obj.get("topik_req")):
            entry_obj["topik_req"] = int(facts["topik"]); changed = True
        lr = str(entry_obj.get("lang_req") or "")
        if facts["ielts"] and f"IELTS {facts['ielts']}" not in lr and authoritative:
            entry_obj["lang_req"] = (f"IELTS {facts['ielts']} / " + lr) if lr else f"IELTS {facts['ielts']}"
            changed = True
        if authoritative:
            entry_obj["guide_analyzed"] = today; changed = True
        return changed

    if section == "MA":
        if facts["period"] and (authoritative or not entry_obj.get("period")):
            entry_obj["period"] = facts["period"]; changed = True
        if facts["topik"] and (authoritative or not entry_obj.get("topik_req")):
            entry_obj["topik_req"] = int(facts["topik"]); changed = True
        if facts["toefl"] and (authoritative or not entry_obj.get("toefl_req")):
            entry_obj["toefl_req"] = facts["toefl"]; changed = True
        lr = str(entry_obj.get("lang_req") or "")
        if facts["ielts"] and f"IELTS {facts['ielts']}" not in lr and authoritative:
            entry_obj["lang_req"] = (f"IELTS {facts['ielts']} / " + lr) if lr else f"IELTS {facts['ielts']}"
            changed = True
        if authoritative:
            entry_obj["guide_analyzed"] = today; changed = True
        return changed

    if section == "jun":
        if facts["period"] and (authoritative or not entry_obj.get("period")):
            entry_obj["period"] = facts["period"]; changed = True
        if facts["topik"] and (authoritative or not entry_obj.get("topik_req")):
            entry_obj["topik_req"] = int(facts["topik"]); changed = True
        if facts["ielts"] and (authoritative or not entry_obj.get("ielts_req")):
            entry_obj["ielts_req"] = facts["ielts"]; changed = True
        if authoritative:
            entry_obj["guide_analyzed"] = today; changed = True
        return changed
    return changed


def main():
    today = datetime.date.today().isoformat()
    proc = {}
    if os.path.exists(PROC_PATH):
        try: proc = json.load(open(PROC_PATH, encoding="utf-8"))
        except Exception: proc = {}
    log = []
    if os.path.exists(LOG_PATH):
        try: log = json.load(open(LOG_PATH, encoding="utf-8"))
        except Exception: log = []

    kb = json.load(open(KB_PATH, encoding="utf-8")) if os.path.exists(KB_PATH) else {}

    new_entries, image_only, no_match = [], [], []
    kb_changed = False

    for folder, (section, year) in FOLDER_MAP.items():
        if not os.path.isdir(folder):
            continue
        container = SECTION_CONTAINER[section](kb)
        for fn in sorted(os.listdir(folder)):
            if not fn.lower().endswith(".pdf"):
                continue
            path = os.path.join(folder, fn)
            try:
                h = hashlib.md5(open(path, "rb").read()).hexdigest()
            except Exception:
                continue
            proc_key = fn if folder == ADIGA_FOREIGN else f"{os.path.basename(folder)}/{fn}"
            if proc.get(proc_key) == h:
                continue
            school = school_name_from_filename(fn)
            try:
                facts = analyze_pdf(path)
            except Exception as e:
                print(f"[guide-analyze] FAIL {fn}: {e}")
                continue
            proc[proc_key] = h

            if facts["text_len"] < 30:
                image_only.append(f"{section}:{fn}")
                log.append({"date": today, "file": fn, "school": school, "section": section,
                            "year": year, "image_only": True})
                print(f"[guide-analyze] IMAGE-ONLY {school} ({section}) — flagged, not merged")
                continue

            key = find_key(container, school)
            if not key:
                no_match.append(f"{section}:{school}")
                log.append({"date": today, "file": fn, "school": school, "section": section,
                            "year": year, "matched": False})
                print(f"[guide-analyze] NO-MATCH {school} ({section}) — not in KB section")
                continue

            entry = {"date": today, "file": fn, "school": school, "section": section,
                     "year": year, "kb_key": key,
                     "period": facts["period"], "ielts": facts["ielts"],
                     "topik": facts["topik"], "toefl": facts["toefl"],
                     "majors_sample": facts["majors"][:6],
                     "scholarships": facts["scholarships"], "has_tuition": facts["has_tuition"]}
            if apply_update(container[key], section, facts, year, today):
                kb_changed = True
            log.append(entry)
            new_entries.append(entry)
            print(f"[guide-analyze] NEW {school} [{section} {year}]: period={facts['period']} "
                  f"IELTS={facts['ielts']} TOPIK={facts['topik']} majors={len(facts['majors'])}")

    if kb_changed:
        json.dump(kb, open(KB_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print(f"[guide-analyze] KB written ({sum(1 for e in new_entries)} guides applied)")

    json.dump(proc, open(PROC_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(log, open(LOG_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    print(f"[guide-analyze] done: {len(new_entries)} new guide(s) merged; "
          f"{len(image_only)} image-only; {len(no_match)} unmatched; total processed {len(proc)}")
    for e in new_entries:
        print(f"  ★ [{e['section']}] {e['school']}: period={e['period']} IELTS={e['ielts']} TOPIK={e['topik']}")


if __name__ == "__main__":
    main()
