# -*- coding: utf-8 -*-
"""Apply parsed 어학연수(lang) guides that arrived 2026-09-29 and have NO KB row.

The LLM merger is fill-only: a record whose school is not already in the KB is
dropped as "unmatched", so newly collected lang guides never land anywhere.
This script creates the missing rows from the parse stores — additive only, every
field source-tagged, values only as written in the guide (no invention) — and
registers image-only PDFs that cannot be read.

  python _apply_new_lang_guides.py            # dry run (prints the draft)
  python _apply_new_lang_guides.py --write    # backup + write KB
"""
import json, os, re, sys, shutil, datetime, collections

BASE = os.path.dirname(os.path.abspath(__file__))
KB = os.path.join(BASE, "verified_kb.json")
DATA_JS = os.path.join(os.path.dirname(BASE), "data.js")
LIB = r"G:/공유 드라이브/Hermes/Camnemi/02_Crawling_Sheet/University_Project/guides"
STAMP = datetime.datetime.now().strftime("%Y%m%d_%H%M")

STORES = [("lib", "_parse_library.jsonl"),
          ("vision", "_parse_library_vl.jsonl"),
          ("main", "_pipeline_data/parsed/guides_llm_parsed.jsonl"),
          ("libstore", "_pipeline_data/parsed/guides_llm_parsed_library.jsonl"),
          ("ocr", "_pipeline_data/parsed/guides_llm_parsed_ocr.jsonl"),
          ("real", "_pipeline_data/parsed/guides_llm_parsed_real.jsonl")]
TRUST_ORDER = ["lib", "libstore", "main", "real", "ocr", "vision"]   # text layer before vision
JUNK = {"", "none", "null", "unknown", "미상", "정보 없음", "미기재", "없음",
        "등록금 정보 없음", "등록금 관련 정보 없음", "등록금안내 메뉴만 제공됨",
        "등록금 금액 미기재", "확인 불가"}
# a value may only enter the lang row when it is about the Korean course itself
LANG_HINT = re.compile(r"한국어|어학|D-?4|수강료|한국어연수|국제어학|어학연수")
# junior/adult-learner admissions data must never be attributed to a language course
FOREIGN_TRACK = re.compile(r"성인학습자|수시1차|수시2차|정시\s*모집|자율모집|전문학사|학위과정")


def is_lang_record(r):
    """True when the parse record itself speaks about the Korean-language course."""
    prog = str(r.get("program") or r.get("_level") or "").lower()
    if prog in ("lang", "language"):
        return True
    txt = " ".join(str(r.get(k) or "") for k in ("period", "tuition_note", "scholarship_note", "level_note"))
    return bool(LANG_HINT.search(txt))


def usable_tuition(c):
    """Tuition text only: never a visa/financial-proof amount, never a junior/adult track."""
    if not c or not has_amount(c):
        return False
    if FOREIGN_TRACK.search(c):
        return False
    return not re.search(r"비자|예치금|재정증명|잔고|체류", c)


def nkey(s):
    s = re.sub(r"[^가-힣A-Za-z0-9]", "", str(s or ""))
    for suf in ("대학원대학교", "대학교", "대학원", "대학", "전문대"):
        if s.endswith(suf):
            return s[: -len(suf)]
    return s


def clean(v):
    if v is None:
        return None
    s = str(v).strip()
    low = s.lower()
    if low in JUNK or any(j in s for j in ("정보 없음", "미기재", "메뉴만 제공", "미상")):
        return None
    return s


def has_amount(s):
    return bool(s and re.search(r"\d{1,3}(,\d{3})+|\d+\s*만\s*원|\d{6,}", s))


def load_recs():
    out = []
    for name, rel in STORES:
        p = os.path.join(BASE, rel)
        if not os.path.exists(p):
            continue
        for line in open(p, encoding="utf-8", errors="replace"):
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except Exception:
                continue
            if not any(r.get(k) for k in ("period", "majors", "tuition_note", "scholarship_note", "topik", "ielts")):
                continue
            r["_store"] = name
            out.append(r)
    return out


def store_rank(name):
    return TRUST_ORDER.index(name) if name in TRUST_ORDER else 99


def region_map():
    reg = {}
    if os.path.exists(DATA_JS):
        txt = open(DATA_JS, encoding="utf-8").read()
        s = txt.find("[")
        depth = 0
        e = len(txt)
        for i in range(s, len(txt)):
            if txt[i] == "[":
                depth += 1
            elif txt[i] == "]":
                depth -= 1
                if depth == 0:
                    e = i
                    break
        for row in json.loads(txt[s:e + 1]):
            if row.get("loc"):
                reg[nkey(row.get("n"))] = row["loc"]
    return reg


def main():
    write = "--write" in sys.argv
    kb = json.load(open(KB, encoding="utf-8"))
    lang = kb["lang_programs"]["schools"]
    # rows this script created stay refreshable (idempotent re-runs); hand-curated
    # rows are never touched
    own = {x for x, v in lang.items() if isinstance(v, dict) and v.get("_added_by") == "_apply_new_lang_guides.py"}
    have = {nkey(x) for x in lang if x not in own}
    recs = load_recs()
    reg = region_map()

    byfile = collections.defaultdict(list)
    for r in recs:
        byfile[r.get("_file") or ""].append(r)
    for f in byfile:
        byfile[f].sort(key=lambda r: store_rank(r["_store"]))

    # school -> [(year, filename)] for library lang guides with no KB row
    per_school = collections.OrderedDict()
    for y in ("2026", "2027"):
        d = os.path.join(LIB, "lang", y)
        if not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d)):
            if not f.lower().endswith(".pdf"):
                continue
            school = re.sub(r"^\d+_", "", f).split("_")[0]
            k = nkey(school)
            if k in have or any(len(k) >= 3 and (k in x or x in k) for x in have):
                continue
            per_school.setdefault(school, []).append((y, f))

    added, registered, skipped = [], {}, []
    for school, files in per_school.items():
        rows = []
        for y, f in files:
            for r in byfile.get(f, []):
                rows.append((y, f, r))
        if not rows:
            registered[school] = os.path.join(LIB, "lang", files[-1][0], files[-1][1]).replace("/", "\\")
            skipped.append((school, "no parsed record (image-only PDF)"))
            continue
        rows.sort(key=lambda t: store_rank(t[2]["_store"]))
        period = tnote = schnote = None
        p_year, p_file, p_store = files[-1][0], files[-1][1], None
        blob = []
        for y, f, r in rows:
            if not is_lang_record(r):
                continue
            blob.append(" ".join(str(r.get(k) or "") for k in ("period", "tuition_note", "scholarship_note", "majors")))
            c = clean(r.get("period"))
            if not period and c and not FOREIGN_TRACK.search(c):
                period, p_year, p_file, p_store = c, y, f, r["_store"]
            c = clean(r.get("tuition_note"))
            if usable_tuition(c) and (tnote is None or not has_amount(tnote)):
                tnote = c
                if not period:
                    p_year, p_file, p_store = y, f, r["_store"]
            c = clean(r.get("scholarship_note"))
            if c and schnote is None and has_amount(c):
                schnote = c
        blob = " ".join(blob)
        schls = []
        for y, f, r in rows:
            if is_lang_record(r) and isinstance(r.get("scholarships"), list) and r["scholarships"]:
                schls = r["scholarships"]
                break
        if not period and not tnote and not schnote and not schls:
            registered[school] = os.path.join(LIB, "lang", p_year, p_file).replace("/", "\\")
            skipped.append((school, f"thin record ({rows[0][2]['_store']}) — no usable value"))
            continue
        pdf = os.path.join(LIB, "lang", p_year, p_file).replace("/", "\\")
        entry = {
            "region": reg.get(nkey(school)),
            "period": period,
            "tuition_note": tnote,
            "scholarship_note": schnote,
            "guide_pdf": pdf,
            "guide_effective_year": p_year,
            "guide_effective_pdf": pdf,
            "guide_year": p_year,
            "updated": datetime.date.today().isoformat(),
            "source": f"guide parse ({p_store or rows[0][2]['_store']}) — new row from 2026-09-29 collection",
            "_llm_parsed": {"_store": p_store or rows[0][2]["_store"], "_file": p_file},
            "_added_by": "_apply_new_lang_guides.py",
        }
        if tnote:
            # a semester/session fee for a Korean course sits in this band; take the
            # first amount that fits instead of blindly trusting the first number
            for raw in re.findall(r"([0-9][0-9,]{4,})\s*원|([0-9][0-9,]{5,})", tnote):
                tok = raw[0] or raw[1]
                v = int(tok.replace(",", ""))
                if 300000 <= v <= 6000000:
                    entry["tuition_range"] = v
                    break
        if schls:
            entry["scholarships"] = schls
        if re.search(r"D-?4", blob):
            entry["d4_eligible"] = True
        added.append((school, entry, sum(len(byfile.get(f, [])) for _, f in files), len(files)))

    print(f"lang guides with no KB row: {sum(len(v) for v in per_school.values())} files / {len(per_school)} schools")
    print(f"  -> new rows: {len(added)}")
    print(f"  -> registered unreadable/thin: {len(registered)}")
    print()
    for school, entry, nrec, nfile in added:
        print(f"{school}  ({nfile} pdf, {nrec} rec)  region={entry.get('region')} d4={entry.get('d4_eligible')} range={entry.get('tuition_range')}")
        print(f"    period : {str(entry.get('period'))[:100]}")
        print(f"    tuition: {str(entry.get('tuition_note'))[:100]}")
        print(f"    pdf    : {entry['guide_pdf']}")
    print()
    for s, why in skipped:
        print("  REGISTER", s, "|", why)

    if not write:
        print("\nDRY RUN — nothing written. Re-run with --write.")
        return

    bak = f"{KB}.bak_{STAMP}_newlang"
    shutil.copy2(KB, bak)
    for school, entry, _, _ in added:
        lang[school] = {k: v for k, v in entry.items() if v not in (None, {}, "")}
    if registered:
        cur = kb["lang_programs"].setdefault("image_only_pdfs_no_text", {})
        for s, p in registered.items():
            cur.setdefault(s, p)
    kb["lang_programs"]["updated"] = f"{datetime.date.today().isoformat()} (신규 어학 요강 {len(added)}교 KB 반영)"
    with open(KB, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(kb, fh, ensure_ascii=False, indent=1)
    print(f"\nWROTE {KB}\nbackup: {bak}")
    print(f"lang schools: {len(lang)} | unreadable registry: {len(kb['lang_programs'].get('image_only_pdfs_no_text') or {})}")


if __name__ == "__main__":
    main()