# -*- coding: utf-8 -*-
"""Junior-college 어학연수 coverage audit: KB lang schools vs library files vs guide_url."""
import json, os, re, collections
HERE = os.path.dirname(os.path.abspath(__file__))
G = r"G:/공유 드라이브/Hermes/Camnemi/02_Crawling_Sheet/University_Project/guides"

kb = json.load(open(os.path.join(HERE, "verified_kb.json"), encoding="utf-8"))
sc = kb["lang_programs"]["schools"]
univ = json.load(open(os.path.join(HERE, "_adiga_univ_list.json"), encoding="utf-8"))
junior = json.load(open(os.path.join(HERE, "_adiga_junior_list.json"), encoding="utf-8"))


def norm(n): return re.sub(r"\[.*?\]|\(.*?\)", "", n).strip()
def key(n): return re.sub(r"(대학교|대학|대)$", "", norm(n))


UNIV = {key(v) for v in univ.values()}
JUNIOR = {key(v) for v in junior.values()}
print("adiga univ list:", len(UNIV), "junior list:", len(JUNIOR))

# library files (all levels) -> set of (key, level)
files = collections.defaultdict(list)
for root, dirs, fs in os.walk(G):
    for f in fs:
        if not f.lower().endswith((".pdf", ".hwp")):
            continue
        rel = os.path.relpath(os.path.join(root, f), G).replace("\\", "/")
        parts = rel.split("/")
        rest = parts[parts.index("_archive") + 1:] if "_archive" in parts else parts
        lv = next((p for p in rest if p in ("ba", "ma", "junior", "lang")), None)
        yr = next((p for p in rest if re.fullmatch(r"20\d\d", p)), None) or \
             (re.search(r"(20\d\d)", f).group(1) if re.search(r"(20\d\d)", f) else "unknown")
        # school name from filename
        p = [x for x in re.sub(r"\.(pdf|hwp)$", "", f, flags=re.I).split("_") if not re.fullmatch(r"\d{4,}", x)]
        nm = None
        for x in p:
            q = norm(x)
            if q.endswith(("대학교", "대학")):
                nm = q; break
        if nm is None:
            for x in p:
                q = norm(x)
                if q.endswith("대") and len(q) >= 2:
                    nm = q; break
        if nm is None and p:
            nm = norm(p[0])
        files[(key(nm or f), lv)].append((rel, yr, nm))

rows = []
for name, v in sc.items():
    k = key(name)
    is_jr = k in JUNIOR
    is_un = k in UNIV
    typ = "junior" if is_jr and not is_un else ("univ" if is_un else "?")
    fl = files.get((k, "lang"), [])
    gp = v.get("guide_pdf")
    exists = bool(gp) and os.path.exists(gp)
    rows.append(dict(name=name, key=k, typ=typ, nfile=len(fl), files=fl,
                     url=v.get("guide_url") or v.get("guide_page_url"),
                     gpdf=gp, exists=exists,
                     eff=v.get("guide_effective_year"), note=v.get("note") or v.get("lang_note")))

c = collections.Counter((r["typ"], r["nfile"] > 0, r["exists"]) for r in rows)
for k in sorted(c, key=str):
    print(k, c[k])
jr = [r for r in rows if r["typ"] == "junior"]
print("\nKB lang schools:", len(rows), "| junior:", len(jr), "| univ:", sum(1 for r in rows if r["typ"] == "univ"),
      "| unknown:", sum(1 for r in rows if r["typ"] == "?"))
print("junior w/ library lang file:", sum(1 for r in jr if r["nfile"] > 0))
print("junior w/ guide_url:", sum(1 for r in jr if r["url"]))
print("junior w/ guide_pdf existing:", sum(1 for r in jr if r["exists"]))
print("\n--- junior w/ NO library file (first 40):")
for r in jr:
    if r["nfile"] == 0:
        print("  %-16s url=%s eff=%s nopdf=%s" % (r["name"], (r["url"] or "-")[:70], r["eff"], not r["exists"]))
print("\n--- junior missing guide_url:")
for r in jr:
    if not r["url"]:
        print("  ", r["name"], r["nfile"], r["eff"])
print("\n--- junior lang files in library not in KB:")
kbk = {r["key"] for r in jr}
for (k, lv), v in files.items():
    if lv == "lang" and k in JUNIOR and k not in kbk:
        print("  ", k, v[:2])
json.dump(rows, open(os.path.join(HERE, "_junior_lang_audit.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("\nwrote _junior_lang_audit.json")
