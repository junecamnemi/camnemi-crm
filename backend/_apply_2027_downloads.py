# -*- coding: utf-8 -*-
"""Point KB guide_pdf/guide_page_url to the newly-downloaded 2027 guides."""
import json, os, re, sys, shutil, datetime

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
import pipeline_paths as _pp  # ONE data home
UP = str(_pp.drive_root())
KB = os.path.join(BASE, "verified_kb.json")
STATE = str(_pp.state_file())

kb = json.load(open(KB, encoding="utf-8"))
state = json.load(open(STATE, encoding="utf-8"))

dl = {n: v for n, v in state.items() if v.get("downloaded") and v.get("saved")}
print(f"다운로드 기록: {len(dl)}")

def norm(value):
    value = re.sub(r"\[.*?\]|\(.*?\)", "", str(value or ""))
    value = re.sub(r"[^가-힣A-Za-z0-9]", "", value)
    for suffix in ("대학원대학교", "대학교", "대학원", "대학", "전문대"):
        if value.endswith(suffix):
            value = value[:-len(suffix)]
            break
    return value

def find_section(school, level):
    sec_map = {"ba": ("schools", None), "ma": ("master", "schools"),
               "junior": ("junior", "schools"), "lang": ("lang_programs", "schools")}
    sec, sub = sec_map.get(level, ("schools", None))
    try:
        d = kb[sec][sub] if sub else kb[sec]
    except Exception:
        return None, None
    key = norm(school)
    exact = [k for k in d if norm(k) == key]
    if len(exact) == 1:
        return sec, exact[0]
    close = [k for k in d if key and len(key) >= 3 and (key in norm(k) or norm(k) in key)]
    return (sec, close[0]) if len(close) == 1 else (None, None)

updated = 0
changed = False
for n, v in dl.items():
    pdf_path = v.get("saved", "")
    if not os.path.isfile(pdf_path):
        print(f"  {n}: 저장 PDF 파일 없음 — skip")
        continue
    with open(pdf_path, "rb") as f:
        if f.read(4) != b"%PDF":
            print(f"  {n}: 유효 PDF 아님 — skip")
            continue
    sec, key = find_section(n, v.get("level", "ba"))
    if not key:
        print(f"  {n}: KB 매칭 실패/모호함")
        continue
    if sec == "schools":
        d = kb["schools"][key]
    else:
        d = kb[sec]["schools"][key]
    values = {"guide_pdf": pdf_path, "guide_year": "2027"}
    if v.get("page_url"):
        values["guide_page_url"] = v["page_url"]
    item_changed = any(d.get(field) != value for field, value in values.items())
    if item_changed:
        d.update(values)
        changed = True
        updated += 1
    print(f"  {n} -> {sec}/{key} valid 2027 PDF" + (" [updated]" if item_changed else " [unchanged]"))

if changed:
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    shutil.copy2(KB, KB.replace(".json", f"_bak_guide2027_{stamp}.json"))
    tmp = KB + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(kb, f, ensure_ascii=False, indent=1)
    os.replace(tmp, KB)
print(f"KB 신규/변경 업데이트: {updated}교" if changed else "KB 변화 없음")
