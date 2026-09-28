# -*- coding: utf-8 -*-
"""_lang_dedupe_merge.py — lang_programs.schools 별칭 키(단축명) 중복 병합.

배경: 어학연수 KB(240교)에 표준키(예: 서울대학교)와 단축 별칭(예: 서울대)이 동시에 존재해
한 학교의 데이터가 두 키에 쪼개져 있다. sync_3layer.norm()은 두 키를 같은 키로 정규화하므로
뒤에 나온 쪽이 앞쪽 데이터를 덮어쓴다(비결정적). → fill-only 병합 후 별칭 키 제거.

안전장치: canonical에는 값을 덮어쓰지 않고 '빈 필드만 채운다'(fill-only). 병합 결과가
양쪽 원본을 모두 포함하는지 검증하고, 검증 실패 시 아무것도 쓰지 않는다.
사용: python _lang_dedupe_merge.py            (dry-run)
      python _lang_dedupe_merge.py --apply    (기록)
"""
import json, os, re, sys, shutil, datetime
B = r"C:\Users\wisew\camnemi-crm\backend"
KB = os.path.join(B, "verified_kb.json")
sys.path.insert(0, B)
import school_keys

APPLY = "--apply" in sys.argv
kb = json.load(open(KB, encoding="utf-8"))
lng = kb["lang_programs"]["schools"]

def norm(n):
    x = re.sub(r"\[.*?\]|\(.*?\)", "", str(n))
    for suf in ["대학원대학교", "대학교", "대학원", "대학", "전문대학", "전문대"]:
        if x.endswith(suf):
            x = x[:-len(suf)]; break
    if x.endswith("대") and len(x) > 1: x = x[:-1]
    return x.replace(" ", "")

def empty(v):
    return v in (None, "", [], {}, 0) or (isinstance(v, str) and not v.strip())

# 1) alias candidate list
pairs = []
for nm in list(lng):
    for cand in (nm + "학교", re.sub(r"학교$", "", nm)):
        if cand != nm and cand in lng:
            pairs.append((nm, cand))
seen, uniq = set(), []
for a, b in pairs:
    k = tuple(sorted((a, b)))
    if k not in seen:
        seen.add(k); uniq.append(k)

# 2) decide canonical per pair: prefer school_keys.resolve(name) if present
plan, ambiguous = [], []
for a, b in uniq:
    if norm(a) != norm(b):
        ambiguous.append((a, b)); continue
    ra, rb = school_keys.resolve(a), school_keys.resolve(b)
    if ra in (a, b):
        canon = ra
    elif rb in (a, b):
        canon = rb
    else:  # resolve didn't map to either -> longer name wins
        canon = a if len(a) >= len(b) else b
    alias = b if canon == a else a
    plan.append((canon, alias))

merged, filled_total, problems = [], 0, []
for canon, alias in plan:
    c, al = lng[canon], lng[alias]
    before_c = dict(c)
    copied = []
    for k, v in al.items():
        if k not in c or empty(c.get(k)):
            if not empty(v):
                c[k] = v; copied.append(k)
    # verify superset: every non-empty field of alias present in merged canonical
    for k, v in al.items():
        if not empty(v) and empty(c.get(k)):
            problems.append((canon, alias, k))
    filled_total += len(copied)
    merged.append({"canon": canon, "alias": alias, "fields_filled": copied,
                   "canon_before": list(before_c.keys()), "canon_after": list(c.keys())})

print(f"별칭쌍 {len(uniq)} | 병합대상 {len(plan)} | 정규화 불일치(제외) {len(ambiguous)} | 채운 필드 {filled_total}개")
print("검증 문제:", problems[:5], len(problems))
before_norm = len({norm(n) for n in lng})
for m in merged[:12]:
    print("  ", m["alias"], "->", m["canon"], "| +", m["fields_filled"])

if problems:
    print("!! 검증 실패 — 기록하지 않음"); sys.exit(1)

if APPLY:
    shutil.copy(KB, KB.replace(".json", f"_bak_langdedupe_{datetime.datetime.now():%Y%m%d_%H%M}.json"))
    for m in merged:
        lng.pop(m["alias"], None)
    after_norm = len({norm(n) for n in lng})
    assert after_norm == before_norm, (after_norm, before_norm)
    json.dump(kb, open(KB, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"APPLIED: lang schools {len(lng)+len(merged)} -> {len(lng)} | norm-keys {before_norm} == {after_norm}")
else:
    print(f"DRY-RUN: lang schools {len(lng)} -> {len(lng)-len(merged)} 예정")
if ambiguous:
    print("ambiguous:", ambiguous[:10])