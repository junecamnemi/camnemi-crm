# -*- coding: utf-8 -*-
"""Keep ONE guide per (school, campus, level, year) in the active library.

Rule (operator 2026-09-28): 4-year univ -> ba/ma/lang, 2-year junior -> junior/lang,
and only the latest guide survives per school+level. Duplicates / broken / partial
downloads are MOVED (never deleted) to guides/_archive/_dupes/<level>/<year>/.

Usage:
  python _library_dedupe.py            # dry-run, prints plan + writes _library_dedupe_plan.json
  python _library_dedupe.py --apply    # perform the moves
"""
import json, os, re, sys, shutil, hashlib, collections, datetime

GUIDES = r"G:/공유 드라이브/Hermes/Camnemi/02_Crawling_Sheet/University_Project/guides"
HERE = os.path.dirname(os.path.abspath(__file__))
PLAN = os.path.join(HERE, "_pipeline_data", "reports", "_library_dedupe_plan.json")
APPLY = "--apply" in sys.argv

import fitz
try:
    fitz.TOOLS.mupdf_display_errors(False)
except Exception:
    pass


def norm_campus(n):
    return re.sub(r"\[.*?\]|\(.*?\)", "", n).strip()


def school_campus(fname):
    base = re.sub(r"\.(pdf|hwp|html|docx|do)$", "", fname, flags=re.I)
    parts = [p for p in base.split("_") if not re.fullmatch(r"\d{4,}", p)]
    name = ""
    for p in parts:
        q = norm_campus(p)
        if q.endswith("대학교") or q.endswith("대학"):
            name = q; break
    if not name:
        for p in parts:
            q = norm_campus(p)
            if q.endswith("대") and len(q) >= 2:
                name = q; break
    if not name:
        name = norm_campus(parts[0]) if parts else base
    campus = ""
    for p in parts:
        if norm_campus(p) != name:
            continue
        m = re.search(r"[\[(](.*?)[\])]", p)
        if m:
            campus = m.group(1)
    if campus == "본교":
        campus = ""
    return name, campus


def fingerprint(path):
    ok = False
    try:
        with open(path, "rb") as f:
            magic = f.read(4)
    except Exception:
        return {"exists": False, "pdf": False, "pages": 0, "md5": "", "chars": 0,
                "sample": "", "html": False}
    ok = magic == b"%PDF"
    if not ok:
        try:
            with open(path, "rb") as f:
                head = f.read(400)
            html = head.lstrip()[:15].lower().startswith(b"<!doctype") or b"<html" in head.lower()
        except Exception:
            html = False
        return {"exists": True, "pdf": False, "pages": 0, "md5": "", "chars": 0,
                "sample": "", "html": html}
    try:
        d = fitz.open(path)
        pc = d.page_count
        t = "".join(d[i].get_text() for i in range(min(3, pc)))
        d.close()
        t = re.sub(r"\s+", "", t)
        return {"exists": True, "pdf": True, "pages": pc,
                "md5": hashlib.md5(t.encode("utf-8")).hexdigest()[:10], "chars": len(t),
                "sample": t[:400], "html": False}
    except Exception as e:
        return {"exists": True, "pdf": True, "pages": -1, "md5": "ERR", "chars": 0,
                "sample": "", "html": False}


JUNK = ("JavaScriptiscurrentlydisabled", "주메뉴바로가기", "본문내용바로가기",
        "사이트정보바로가기", "AdobeAcrobatReader", "이페이지는프레임")


def is_junk(sample):
    return any(t in sample for t in JUNK)


# --- KB guide_pdf references -------------------------------------------------
kb = json.load(open(os.path.join(HERE, "verified_kb.json"), encoding="utf-8"))
ms = kb.get("master", {}).get("schools", kb)
KBREF = {}
for s, v in ms.items():
    if not isinstance(v, dict):
        continue
    for k, x in v.items():
        if k.startswith("guide_pdf") and isinstance(x, str) and x.lower().endswith(".pdf"):
            KBREF.setdefault(os.path.normcase(os.path.basename(x)), set()).add(s)

man = json.load(open(os.path.join(GUIDES, "_library_manifest.json"), encoding="utf-8"))
ent = [e for e in man["entries"] if not e.get("archived")]

groups = collections.defaultdict(list)
for e in ent:
    p = e.get("library_path") or e["path"]
    s, c = school_campus(e["name"])
    fp = fingerprint(p)
    groups[(s, c, e["level"], e["year"])].append({
        "name": e["name"], "path": p, "bytes": e["bytes"], **fp,
        "kb_ref": os.path.normcase(e["name"]) in KBREF,
    })

plan, kept1 = [], []
for key, items in sorted(groups.items()):
    if len(items) == 1:
        it = items[0]
        if (not it["pdf"]) or it["pages"] <= 0:
            r = ("HTML saved as .pdf, not a guide" if it.get("html")
                 else "PDF with 0 readable pages (truncated/empty)")
            plan.append({"group": key, "action": "archive_junk", "keep": None,
                         "archive": [it["name"]], "archive_path": it["path"], "reason": r})
        elif is_junk(it.get("sample", "")):
            plan.append({"group": key, "action": "archive_junk", "keep": None,
                         "archive": [it["name"]], "archive_path": it["path"],
                         "reason": "web-page capture, not a guide"})
        continue

    def conv(n):
        has_year = 1 if re.search(r"(20\d\d)", n) else 0
        is_foreign = 1 if "외국인" in n else 0
        return has_year, is_foreign

    def score(x):
        good = 1 if (x["pdf"] and x["pages"] > 0) else 0
        hj = 0 if is_junk(x.get("sample", "")) else 1
        hy, isf = conv(x["name"])
        return (good, hj, 1 if x["kb_ref"] else 0, hy, isf, x["pages"], x["bytes"])

    items_sorted = sorted(items, key=score, reverse=True)
    keep = items_sorted[0]
    for it in items_sorted[1:]:
        same_text = (it["md5"] and it["md5"] == keep["md5"])
        broken = (not it["pdf"]) or it["pages"] <= 0
        partial = (it["pages"] < 3 and it["bytes"] < 150000)
        if same_text:
            plan.append({"group": key, "action": "archive_dup", "keep": keep["name"],
                         "keep_path": keep["path"], "archive": [it["name"]],
                         "archive_path": it["path"],
                         "reason": "identical content (same text fingerprint)",
                         "keep_kb_ref": keep["kb_ref"], "dup_kb_ref": it["kb_ref"]})
        elif broken or partial or is_junk(it.get("sample", "")):
            r = ("HTML saved as .pdf, not a guide" if it.get("html") else
                 "PDF with 0 readable pages (truncated/empty)" if broken else
                 "partial download (<3 pages, <150KB)" if partial else
                 "web-page capture, not a guide")
            plan.append({"group": key, "action": "archive_dup", "keep": keep["name"],
                         "keep_path": keep["path"], "archive": [it["name"]],
                         "archive_path": it["path"], "reason": r,
                         "keep_kb_ref": keep["kb_ref"], "dup_kb_ref": it["kb_ref"]})
        elif (it["pages"] == keep["pages"] and it["pages"] > 0
              and abs(it["bytes"] - keep["bytes"]) / max(it["bytes"], keep["bytes"]) <= 0.02):
            plan.append({"group": key, "action": "archive_dup", "keep": keep["name"],
                         "keep_path": keep["path"], "archive": [it["name"]],
                         "archive_path": it["path"],
                         "reason": f"near-identical rebuild (same {it['pages']}p, size within 2%)",
                         "keep_kb_ref": keep["kb_ref"], "dup_kb_ref": it["kb_ref"]})
        else:
            plan.append({"group": key, "action": "flag_diff", "keep": keep["name"],
                         "keep_path": keep["path"], "archive": [it["name"]],
                         "archive_path": it["path"],
                         "reason": f"different text ({it['pages']}p/{it['bytes']}B vs keeper {keep['pages']}p/{keep['bytes']}B) - review, not auto-archived",
                         "keep_kb_ref": keep["kb_ref"], "dup_kb_ref": it["kb_ref"]})

# explicit mis-file corrections (verified by reading the PDF text; content is not
# unique — an identical file is kept under its correct level)
EXTRA = {
    "ba/2027/연세대학교_BA_2027.pdf": "identical to the kept 연세대학교_MA_2027.pdf (대학원 guide) - mis-filed under ba",
    "lang/2027/연세대_LANG_2027.pdf": "identical to the kept 연세대학교_MA_2027.pdf (대학원 guide) - mis-filed under lang",
    "ma/2027/동의대학교_MA_2027.pdf": "identical to the kept ba guide 동의대학교[본교]_2027_외국인.pdf - mis-filed under ma",
}
for rel, why in list(EXTRA.items()):
    lv, yr, nm = rel.split("/")
    cand = [e for e in ent if e["name"] == nm and e["level"] == lv]
    if not cand:
        EXTRA.pop(rel)
        continue
    p = cand[0]
    plan.append({"group": (nm, "", lv, yr), "action": "archive_dup", "keep": "(kept in another level)",
                 "keep_path": "", "archive": [nm],
                 "archive_path": p.get("library_path") or p["path"],
                 "reason": why, "keep_kb_ref": False, "dup_kb_ref": False})

# cross-level identical content (same PDF filed under >1 level for one school)
bytext = collections.defaultdict(list)
for key, items in groups.items():
    for it in items:
        if it["md5"] and it["md5"] != "ERR":
            bytext[(key[0], it["md5"])].append((key[2], it["name"]))
cross = {f"{k[0]}|{k[1]}": v for k, v in bytext.items() if len({x[0] for x in v}) > 1}

os.makedirs(os.path.dirname(PLAN), exist_ok=True)
json.dump({"plan": plan, "cross_level": cross}, open(PLAN, "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

n_archive = sum(1 for p in plan if p["action"] == "archive_dup")
n_junk = sum(1 for p in plan if p["action"] == "archive_junk")
n_diff = sum(1 for p in plan if p["action"] == "flag_diff")
print(f"groups: {len(groups)}   duplicates: {n_archive}   junk-only: {n_junk}   diff-review: {n_diff}\n")
for p in plan:
    if p["action"] == "archive_dup":
        k = "KB" if p["keep_kb_ref"] else "  "
        print(f"KEEP[{k}] {p['keep']}")
        print(f"  ARCH {p['archive'][0]}   << {p['reason']}")
print("\n--- junk-only groups (school has NO usable guide left) ---")
for p in plan:
    if p["action"] == "archive_junk":
        print(f"  {p['group'][0]} [{p['group'][2]}] {p['archive'][0]}  | {p['reason']}")
print("\n--- NOT auto-archived (need review) ---")
for p in plan:
    if p["action"] == "flag_diff":
        print(f"  {p['group']}: {p['archive'][0]}  | {p['reason']}")
print("\n--- same PDF filed under multiple levels ---")
for k, v in cross.items():
    print("  ", k, v)

kb_hits = [(p["archive"][0], sorted(KBREF[os.path.normcase(p["archive"][0])]))
           for p in plan
           if p["action"] in ("archive_dup", "archive_junk")
           and os.path.normcase(p["archive"][0]) in KBREF]
print(f"\n--- files being archived that the KB guide_pdf points at (must repoint): {len(kb_hits)} ---")
for nm, schools in kb_hits:
    print(f"  {nm}  <- {schools}")

if APPLY:
    moved, errs, seen = 0, [], set()
    for p in plan:
        if p["action"] not in ("archive_dup", "archive_junk"):
            continue
        src = p["archive_path"]
        if src in seen:
            continue
        seen.add(src)
        lv, yr = p["group"][2], p["group"][3]
        sub = "_dupes" if p["action"] == "archive_dup" else "_junk"
        dst_dir = os.path.join(GUIDES, "_archive", sub, lv, yr)
        os.makedirs(dst_dir, exist_ok=True)
        dst = os.path.join(dst_dir, os.path.basename(src))
        if os.path.exists(dst):
            dst = os.path.join(dst_dir, datetime.datetime.now().strftime("%H%M%S_") + os.path.basename(src))
        try:
            if os.path.exists(src):
                shutil.move(src, dst)
                moved += 1
            else:
                errs.append(f"missing src {src}")
        except Exception as ex:
            errs.append(f"{src}: {ex}")
    print(f"\nMOVED {moved} file(s) to _archive/   errors: {len(errs)}")
    for e in errs:
        print("  !", e)
    still = [p["archive_path"] for p in plan if p["action"] in ("archive_dup", "archive_junk")
             and os.path.exists(p["archive_path"])]
    print("read-back: source files still present (must be 0):", len(still))
    lost = [p["keep_path"] for p in plan if p["action"] == "archive_dup" and p["keep_path"]
            and not os.path.exists(p["keep_path"])]
    print("read-back: KEEP files missing (must be 0):", len(lost))