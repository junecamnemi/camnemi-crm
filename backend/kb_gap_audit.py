#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""kb_gap_audit.py — KB 자기개선 ② 자가감사 갭필러.

verified_kb에서 필수필드(학비/어학/전공/장학)가 누락된 학교를 자동 탐지하고,
수집된 요강 유무에 따라 조치 대상을 분류한다:
  - has_guide  : 수집된 요강이 있으나 파싱이 null → 재파싱/재수집 후보
  - no_guide   : 요강 미수집 → 수집 후보
  - no_foreign : 외국인 요강 자체가 없음(확인됨) → 수집 불가(무요강)
출력: _kb_gap_report.json + _kb_gap_queue.json (야간/주간 크론이 소비)
"""
import json, os, datetime
from collections import Counter

B = r"C:\Users\wisew\camnemi-crm\backend"
today = datetime.date.today().isoformat()

def load(p, d=None):
    try: return json.load(open(os.path.join(B, p), encoding="utf-8"))
    except: return d if d is not None else {}

kb = load("verified_kb.json", {})
jun_col = load("_junior_foreign_collected.json", {})
jun_collected = {e["name"]: e for e in jun_col.get("collected", [])}
jun_missing = {e["name"]: e for e in jun_col.get("missing", [])}
jun_page = {e["name"]: e for e in jun_col.get("page_guide", [])}

CRITICAL = ["tuition", "lang", "major", "scholarship"]

def missing_fields(e, level=None):
    m = []
    if level == "lang":
        if not (e.get("tuition_note") or e.get("tuition_semester") or e.get("tuition_min")): m.append("tuition")
        if not (e.get("programs") or e.get("levels") or e.get("duration")): m.append("program")
        if not (e.get("scholarship_note") or e.get("scholarships_categorized")): m.append("scholarship")
        return m
    if not e.get("tuition_min") and not e.get("tuition_semester"): m.append("tuition")
    if e.get("topik_req") is None and e.get("ielts_req") is None and not e.get("lang_req"): m.append("lang")
    if not (e.get("majors_full") or e.get("majors_ba") or e.get("majors_sample") or e.get("majors_ma")): m.append("major")
    if not (e.get("scholarships_categorized") or e.get("scholarships")): m.append("scholarship")
    return m

def audit(level, schools, collected_map, missing_map, page_map):
    report = []
    for nm, e in schools.items():
        mf = missing_fields(e, level)
        if not mf: continue
        if nm in collected_map:
            action = "reparse"   # has guide, parsed null -> re-parse/re-collect better guide
        elif nm in page_map:
            action = "recollect" # page-guide only -> try to get real PDF
        elif nm in missing_map:
            action = "no_foreign" # confirmed no foreigner guide
        else:
            action = "collect"   # no guide recorded -> collect
        report.append({"school": nm, "level": level, "missing": mf, "action": action})
    return report

all_report = []
all_report += audit("BA", kb.get("schools", {}), {}, {}, {})
all_report += audit("junior", kb["junior"]["schools"], jun_collected, jun_missing, jun_page)
# MA / lang — collected maps not tracked here; treat as collect if missing
all_report += audit("MA", kb.get("master", {}).get("schools", {}) if isinstance(kb.get("master"), dict) else {}, {}, {}, {})
all_report += audit("lang", kb.get("lang_programs", {}).get("schools", {}) if isinstance(kb.get("lang_programs"), dict) else {}, {}, {}, {})

# summary
by_action = Counter(r["action"] for r in all_report)
by_level = Counter(r["level"] for r in all_report)
by_missing = Counter()
for r in all_report:
    for m in r["missing"]: by_missing[m] += 1

# actionable queue (exclude no_foreign)
queue = [r for r in all_report if r["action"] in ("reparse", "recollect", "collect")]

json.dump({"generated": today, "summary": {"by_action": dict(by_action), "by_level": dict(by_level),
           "by_missing": dict(by_missing), "actionable": len(queue)},
           "gaps": all_report},
          open(os.path.join(B, "_kb_gap_report.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump({"generated": today, "queue": queue},
          open(os.path.join(B, "_kb_gap_queue.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

print(f"=== KB 갭 감사 ({today}) ===")
print(f"총 갭 학교: {len(all_report)} | 조치가능: {len(queue)}")
print(f"조치 유형: {dict(by_action)}")
print(f"레벨별: {dict(by_level)}")
print(f"누락 필드: {dict(by_missing)}")
print("\n조치가능 상위 (2+필드 누락):")
for r in sorted([r for r in queue if len(r["missing"])>=2], key=lambda x:-len(x["missing"]))[:15]:
    print(f"  [{r['level']}] {r['school']} ({r['action']}): {r['missing']}")
