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
import json, os, re, sys, datetime
from collections import Counter

B = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, B)
import pipeline_paths as _pp  # ONE data home (_pipeline_data/reports)
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

# 추천 제외 규칙(운영자): 신학대·교육대는 수집 대상에서 제외. 학생수<2000 예외와 동일하게
# 한국기술교육대는 유지한다. (2026-10-05: 갭 큐에 신학대 9교가 섞여 수집 대상으로 잡히던 문제)
EXCLUDE_NAME_TOKENS = ("신학대", "신학교", "장신대", "교육대")
EXCLUDE_KEEP = ("한국기술교육대",)


def is_excluded(nm: str) -> bool:
    if any(k in nm for k in EXCLUDE_KEEP):
        return False
    return any(t in nm for t in EXCLUDE_NAME_TOKENS)


# 자가감사 정확성 보강(2026-09-28): 아래 두 경우를 '수집 필요'로 오분류하지 않는다.
#  1) documented : 필드 옆 note에 부재 근거가 이미 기록된 경우 → 재파싱해도 안 채워짐(요강에 미기재).
#  2) dedupe    : lang레벨에서 표준키/단축 별칭키가 동시에 존재해 데이터가 쪼개진 경우 → 수집이 아니라 키 병합.
DOC_TOKENS = ("need=", "미공개", "미확인", "미명시", "미기재", "내부규정", "확인 불가", "없음",
              "명시되어 있지 않", "추후 공지", "공개되지 않", "정해지지 않")
# ⚠️ 부재 근거는 해당 필드 note에만 적히지 않는다. 병합기가 "need=등록금..." 처럼
#    반대편 note에 적어두는 경우가 많아(예: 재능대 tuition 부재근거가 scholarship_note에),
#    모든 note 필드를 함께 본다. (2026-10-05 실측: junior 10교가 reparse로 오분류)
_ALL_NOTES = ("tuition_note", "scholarship_note", "lang_note", "major_note", "program_note", "note")
NOTE_FOR = {f: _ALL_NOTES for f in ("tuition", "scholarship", "lang", "major", "program")}
# note에 실제 금액이 적혀 있으면 그 필드는 '데이터 보유'로 본다(구조화 필드가 비어도).
AMT_RE = re.compile(r"\d{1,3}(?:,\d{3})+|\d[\d,]{3,}")
# 장학 note에 혜택(전액/비율/금액/감면)이 적혀 있으면 장학 데이터 보유로 본다.
SCH_DATA_RE = re.compile(r"전액|%|만원|감면|면제|지급|장려금")


def documented_missing(e, mf):
    out = []
    for f in mf:
        for k in NOTE_FOR.get(f, ("note",)):
            v = e.get(k)
            if isinstance(v, str) and any(t in v for t in DOC_TOKENS):
                out.append(f)
                break
    return out


def alias_twin(nm, schools, level):
    if level != "lang":
        return None
    for cand in (nm + "학교", re.sub(r"학교$", "", nm)):
        if cand != nm and cand in schools:
            return cand
    return None


def missing_fields(e, level=None):
    m = []
    if level == "lang":
        if not (e.get("tuition_note") or e.get("tuition_semester") or e.get("tuition_min")): m.append("tuition")
        # 어학 과정 정보는 실제로는 `structure`(per_term/total_hours/per_day)에 들어있다.
        # `programs`/`levels`/`duration`만 보면 137교가 오탐(2026-10-05 실측: 194교가 structure 보유).
        if not (e.get("programs") or e.get("levels") or e.get("duration") or e.get("structure")): m.append("program")
        if not (e.get("scholarship_note") or e.get("scholarships_categorized")): m.append("scholarship")
        return m
    if not e.get("tuition_min") and not e.get("tuition_semester") and not (e.get("tuition_note") and AMT_RE.search(str(e.get("tuition_note")))): m.append("tuition")
    if e.get("topik_req") is None and e.get("ielts_req") is None and not e.get("lang_req"): m.append("lang")
    if not (e.get("majors_full") or e.get("majors_ba") or e.get("majors_sample") or e.get("majors_ma")): m.append("major")
    if not (e.get("scholarships_categorized") or e.get("scholarships") or (e.get("scholarship_note") and SCH_DATA_RE.search(str(e.get("scholarship_note"))))): m.append("scholarship")
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
        if action in ("reparse", "recollect", "collect"):
            doc = documented_missing(e, mf)
            twin = alias_twin(nm, schools, level)
            if len(doc) == len(mf):
                action = "documented"   # note에 부재 근거 기록됨 → 수집해도 안 채워짐
            elif twin:
                action = "dedupe"       # 별칭키 중복 → 키 병합으로 해결
        if action in ("reparse", "recollect", "collect", "dedupe") and is_excluded(nm):
            action = "excluded"          # 신학대·교육대 = 추천 제외 규칙 대상 (수집 불필요)
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

# actionable queue (exclude no_foreign / documented / excluded)
queue = [r for r in all_report if r["action"] in ("reparse", "recollect", "collect", "dedupe")]

json.dump({"generated": today, "summary": {"by_action": dict(by_action), "by_level": dict(by_level),
           "by_missing": dict(by_missing), "actionable": len(queue)},
           "gaps": all_report},
          open(_pp.path("gap_report"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump({"generated": today, "queue": queue},
          open(_pp.path("gap_queue"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

print(f"=== KB 갭 감사 ({today}) ===")
print(f"총 갭 학교: {len(all_report)} | 조치가능: {len(queue)}")
print(f"조치 유형: {dict(by_action)}")
print(f"레벨별: {dict(by_level)}")
print(f"누락 필드: {dict(by_missing)}")
print("\n조치가능 상위 (2+필드 누락):")
for r in sorted([r for r in queue if len(r["missing"])>=2], key=lambda x:-len(x["missing"]))[:15]:
    print(f"  [{r['level']}] {r['school']} ({r['action']}): {r['missing']}")