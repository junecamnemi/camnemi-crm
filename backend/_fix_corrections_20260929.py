#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""One-off corrections (2026-09-29): 신경주대학교 = closed/excluded, and quarantine the bad
광주여자대학교 guide file (a 학과 notice page capture, not the 외국인 모집요강).

Exact normalized match only — see references/school-status-flags-and-engine-enforcement.md
(containment matching once mis-flagged 중앙대학교/국제대학교/동신대학교).
"""
import json, re, shutil, datetime
from pathlib import Path

B = Path(r"C:\Users\wisew\camnemi-crm\backend")
KB, CDB = B / "verified_kb.json", B / "consulting_db.json"
STAMP = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

FINDINGS = {
    "신경주대학교": {
        "status": "closed",
        "status_note": ("폐교·법인 파산(등록금 20억 미반환 보도). 2027 모집요강 부존재 — 추천 제외, "
                        "외국인 전형 자료 갱신 안 함."),
        "recommend_exclude": True,
    },
}


def norm(s):
    return re.sub(r"[^가-힣a-zA-Z0-9]", "", str(s or "")).replace("대학교", "").replace("대학", "")


kb = json.load(open(KB, encoding="utf-8"))
shutil.copy(KB, B / f"verified_kb_bak_corr_{STAMP}.json")

applied = []
for section in ("schools", "master", "junior", "lang_programs"):
    node = kb.get(section) or {}
    schools = node.get("schools") if isinstance(node, dict) and "schools" in node else None
    targets = schools if isinstance(schools, dict) else (node if section == "schools" else None)
    if not isinstance(targets, dict):
        continue
    idx = {norm(k): k for k in targets}          # exact normalized equality only
    for name, meta in FINDINGS.items():
        key = idx.get(norm(name))
        if not key:
            continue
        targets[key].update(meta)
        applied.append((section, key))

# --- 광주여대: quarantine the bad file, drop the KB pointer ---
q = []
for section in ("schools", "master"):
    node = kb.get(section) or {}
    schools = node.get("schools") if isinstance(node, dict) and "schools" in node else node
    for key, rec in (schools or {}).items():
        if not isinstance(rec, dict) or norm(key) != norm("광주여자대학교"):
            continue
        path = rec.get("guide_effective_pdf")
        if path and Path(path).is_file():
            dest = B / "_pipeline_data" / "reports" / "html_backups" / (
                f"광주여대_QUARANTINED_deptpage_{STAMP}_{Path(path).name}")
            shutil.move(path, dest)
            q.append((section, key, str(dest)))
        rec["guide_effective_pdf"] = None
        rec["guide_effective_note"] = ("2026 외국인 모집요강 파일 미확보 — 종전 파일은 학과 공지 페이지 "
                                       "캡처였음(=요강 아님)이라 격리함. kwu.ac.kr 국제교류처에서 재수집 필요.")
        rec["updated"] = datetime.date.today().isoformat()

open(KB, "w", encoding="utf-8", newline="\n").write(json.dumps(kb, ensure_ascii=False, indent=1) + "\n")
print("verified_kb status applied:", applied)
print("quarantined:", [q_[:2] + (q_[2][-60:],) for q_ in q])

cdb = json.load(open(CDB, encoding="utf-8"))
n = 0
for key, rec in (cdb.get("schools") or {}).items():
    if not isinstance(rec, dict):
        continue
    for name, meta in FINDINGS.items():
        if norm(key) == norm(name):
            rec.update(meta)
            n += 1
open(CDB, "w", encoding="utf-8", newline="\n").write(json.dumps(cdb, ensure_ascii=False, indent=1) + "\n")
print(f"consulting_db mirrored: {n}")

# verification
kb2 = json.load(open(KB, encoding="utf-8"))
for section in ("schools", "master", "junior", "lang_programs"):
    node = kb2.get(section) or {}
    schools = node.get("schools") if isinstance(node, dict) and "schools" in node else node
    for k, v in (schools or {}).items():
        if isinstance(v, dict) and norm(k) in (norm("신경주대학교"), norm("중앙대학교"), norm("국제대학교"), norm("광주여자대학교")):
            print(f"  check {section}/{k}: status={v.get('status')} exclude={v.get('recommend_exclude')} "
                  f"pdf={'yes' if v.get('guide_effective_pdf') else None}")