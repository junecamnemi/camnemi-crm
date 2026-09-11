#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KB Smart Index builder — turns verified_kb.json into kb_smart.json.

Produces, per school, a cross-level object with:
  eligibility : structured, machine-filterable language/entry requirements
  major_tags  : canonical major taxonomy tags
  quality     : per-record data-quality flags (missing/anomaly/stale)

Sections covered: BA (schools), MA (master), junior, lang (lang_programs).

Usage: python build_kb_smart.py
Output: backend/kb_smart.json
"""
import json, os, re, datetime

B = r"C:\Users\USER\camnemi-crm\backend"
KB = os.path.join(B, "verified_kb.json")
OUT = os.path.join(B, "kb_smart.json")


# ---------------- A. eligibility parser ----------------
def parse_eligibility(text, topik_req=None, ielts_req=None, toefl_req=None):
    t = str(text or "")
    e = {}

    # TOPIK (min level; capture ALL to detect variance)
    tks = [int(x) for x in re.findall(r"TOPIK(?:\s*IBT)?[^\d]{0,8}(\d)\s*(?:급|이상)?", t)]
    if tks:
        e["topik"] = {"min": min(tks)}
        if len(set(tks)) > 1:
            e["topik"]["all"] = sorted(set(tks))
            e["ambiguous"] = True
        am = re.search(r"예[·\-\s]*체능[^\d]{0,8}(\d)\s*급", t)
        if am:
            e["topik"]["arts_min"] = int(am.group(1))
    elif topik_req not in (None, "", "null"):
        try: e["topik"] = {"min": int(float(topik_req))}
        except Exception: pass

    # IELTS (min) — capture ALL values to detect track-specific variance
    iels = [float(x) for x in re.findall(r"IELTS(?:\s*Academic)?\s*(\d\.?\d?)", t)]
    if iels:
        e["ielts"] = {"min": min(iels)}
        if len(set(iels)) > 1:
            e["ielts"]["all"] = sorted(set(iels))
            e["ambiguous"] = True
    elif ielts_req not in (None, "", "null"):
        try: e["ielts"] = {"min": float(ielts_req)}
        except Exception: pass
    # cross-check the structured field: flag if it disagrees with lang_req text
    if iels and ielts_req not in (None, "", "null"):
        try:
            if abs(float(ielts_req) - min(iels)) > 0.01:
                e["ambiguous"] = True
                e.setdefault("ielts", {})["field"] = float(ielts_req)
        except Exception:
            pass

    # TOEFL iBT / PBT
    m = re.search(r"(?:TOEFL\s*)?iBT\s*(\d{2,3})", t) or re.search(r"TOEFL\s*iBT\s*(\d{2,3})", t)
    if m:
        e["toefl_ibt"] = {"min": int(m.group(1))}
    elif toefl_req not in (None, "", "null"):
        try: e["toefl_ibt"] = {"min": int(float(toefl_req))}
        except Exception: pass
    mp = re.search(r"TOEFL\s*(\d{3})\s*\(?PBT|PBT\s*(\d{3})", t)
    if mp:
        e["toefl_pbt"] = {"min": int(mp.group(1) or mp.group(2))}

    # TEPS
    m = re.search(r"New\s*TEPS\s*(\d{3})", t, re.I) or re.search(r"TEPS\s*(\d{3})", t)
    if m:
        e["teps"] = {"min": int(m.group(1))}

    # CEFR
    m = re.search(r"CEFR\s*(A2|B1|B2|C1|C2)", t, re.I)
    if m:
        e["cefr"] = m.group(1).upper()

    # 자체시험
    if re.search(r"자체\s*(한국어|평가|TOPIK|한국어능력시험)|SU-TOPIK|한국어능력시험\s*합격|자체평가\s*통과", t):
        e["selftest"] = True

    # KIIP / 사회통합프로그램
    m = re.search(r"(?:KIIP|사회통합프로그램)[^\d]{0,10}(\d)\s*단계", t)
    if m:
        e["kiip"] = {"min_stage": int(m.group(1))}
    elif "KIIP" in t or "사회통합프로그램" in t:
        e["kiip"] = {}
    m = re.search(r"사전평가\s*(\d{2,3})\s*점", t)
    if m:
        e.setdefault("kiip", {})["pre_eval"] = int(m.group(1))

    # 세종학당
    m = re.search(r"세종학당[^\n]{0,20}?(초급\d|중급\d)", t)
    if m:
        e["sejong"] = m.group(1)

    # 어학원/한국어과정 수료 (급수)
    m = re.search(r"(?:부설|어학당|한국어교육원|한국어학당|어학교육원|국제교육원)[^\n]{0,20}?(\d)\s*급\s*(?:이상\s*)?수료", t)
    if m:
        e["lang_school"] = {"min_level": int(m.group(1))}

    # 영어트랙 여부
    if re.search(r"영어\s*트랙\s*없음|영어성적으로\s*지원\s*불가|영어\s*대체\s*기준\s*없음|영어성적\s*기준\s*없음", t):
        e["english_track"] = False
    elif re.search(r"영어\s*트랙|ENG\s|영어과정|영어\s*강의", t):
        e["english_track"] = True

    # 영어 모국어/공용어 면제
    if re.search(r"영어\s*(?:모국어|공용어)\s*국가[^\n]{0,10}면제|영어\s*모국어\s*국적자\s*면제", t):
        e["exempt_native_english"] = True

    # 옵션 OR 여부
    if re.search(r"또는|중\s*하나|택\s*1|이상\s*or|OR", t):
        e["one_of"] = True

    # 면접으로 검증
    if re.search(r"면접[^\n]{0,20}(검증|평가)", t):
        e["interview_eval"] = True

    e["raw"] = t[:400]
    return e


# ---------------- B. major taxonomy ----------------
TAXONOMY = {
    "AI_CS": ["인공지능", "AI", "컴퓨터", "소프트웨어", "데이터", "정보통신", "지능", "로봇", "사이버",
              "게임", "정보보호", "빅데이터", "정보보안", "IT", "융합소프트", "스마트"],
    "반도체": ["반도체", "시스템반도체", "디스플레이"],
    "경영": ["경영", "경제", "회계", "세무", "무역", "통상", "금융", "유통", "물류", "마케팅",
             "창업", "벤처", "비즈니스", "국제경영", "보험"],
    "공학": ["기계", "전기", "전자", "화학공", "신소재", "건축", "토목", "산업공", "항공", "자동차",
             "조선", "에너지", "재료", "환경공", "설비", "메카트로닉스", "금속", "섬유"],
    "보건의료": ["간호", "의예", "의학", "약학", "치위생", "치기공", "물리치료", "작업치료",
                "임상병리", "방사선", "보건", "식품영양", "응급구조", "안경", "의료", "바이오"],
    "자연과학": ["물리", "수학", "통계", "생물", "생명", "지구", "천문", "화학", "과학교육"],
    "인문": ["국어", "영어", "문학", "역사", "철학", "언어", "종교", "한문", "중어", "일어", "독어", "불어"],
    "사회과학": ["사회", "정치", "행정", "심리", "언론", "미디어", "법", "국제", "지리", "복지",
                "행정학", "공공", "부동산", "경찰", "군사", "국방"],
    "예체능": ["음악", "미술", "디자인", "체육", "연기", "영상", "무용", "만화", "애니", "실용음악",
              "공연", "조형", "패션", "의상", "스포츠", "태권도", "뷰티", "미용"],
    "교육": ["교육", "유아", "초등", "특수교육", "교직"],
    "호텔관광": ["호텔", "관광", "조리", "외식", "항공서비스", "카지노", "여행"],
    "농림수산": ["농업", "원예", "축산", "산림", "수산", "해양", "식품공"],
    "자유전공": ["자유전공", "글로벌자유", "자율전공", "광역", "융합학부", "국제학부", "글로벌학부"],
}

def major_tags(majors):
    tags = []
    if isinstance(majors, str):
        majors = [majors]
    blob = " ".join(str(m) for m in (majors or []))
    for tag, kws in TAXONOMY.items():
        if any(k in blob for k in kws):
            tags.append(tag)
    return tags


# ---------------- main ----------------
def main():
    kb = json.load(open(KB, encoding="utf-8"))
    today = datetime.date.today().isoformat()
    out = {"generated": today, "source": "verified_kb.json", "schools": {}}

    # AI-department authoritative set (88 schools) — merge into AI_CS tag
    ai_sch = kb.get("ai_departments", {}).get("schools", {})
    ai_keys = list(ai_sch.keys())
    def is_ai_school(name):
        n = name.replace("대학교", "").replace("대학", "").strip()
        for k in ai_keys:
            kk = k.replace("대학교", "").replace("대학", "").strip()
            if n == kk or (len(n) >= 3 and (n in kk or kk in n)):
                depts = ai_sch[k].get("depts", {})
                return bool(depts) and any(depts.values())
        return False

    def get(school):
        return out["schools"].setdefault(school, {})

    def tagset(majors, school):
        tags = major_tags(majors)
        if is_ai_school(school) and "AI_CS" not in tags:
            tags = ["AI_CS"] + tags
        return tags

    # BA
    for k, v in kb.get("schools", {}).items():
        e = parse_eligibility(v.get("lang_req"), v.get("topik_req"), v.get("ielts_req"))
        get(k)["BA"] = {
            "eligibility": e,
            "major_tags": tagset(v.get("majors_ba") or v.get("majors"), k),
            "track": v.get("track"), "region": v.get("region"), "rank": v.get("rank"),
            "tuition_semester": v.get("tuition_semester"),
            "period": v.get("period"), "year": v.get("year"),
            "guide_analyzed": v.get("guide_analyzed"),
        }

    # MA
    for k, v in kb.get("master", {}).get("schools", {}).items():
        e = parse_eligibility(v.get("lang_req"), v.get("topik_req"), None, v.get("toefl_req"))
        get(k)["MA"] = {
            "eligibility": e,
            "major_tags": tagset(v.get("majors") or v.get("popular_majors"), k),
            "region": v.get("region"), "rank": v.get("rank"),
            "tuition_min": v.get("tuition_min"), "tuition_max": v.get("tuition_max"),
            "period": v.get("period"), "guide_status": v.get("guide_status"),
        }

    # junior
    for k, v in kb.get("junior", {}).get("schools", {}).items():
        e = parse_eligibility(v.get("lang_req"), v.get("topik_req"), v.get("ielts_req"))
        get(k)["jun"] = {
            "eligibility": e,
            "major_tags": tagset(v.get("majors_sample"), k),
            "region": v.get("region"), "rank": v.get("rank"), "type": v.get("type"),
            "tuition_semester": v.get("tuition_semester"),
            "period": v.get("period"), "selftest": v.get("selftest"),
        }

    # lang
    for k, v in kb.get("lang_programs", {}).get("schools", {}).items():
        get(k)["lang"] = {
            "eligibility": {"d4": v.get("d4_eligible")},
            "region": v.get("region"),
            "tuition": v.get("tuition_range"),
            "structure": v.get("structure"), "d4_eligible": v.get("d4_eligible"),
            "dorm": v.get("dorm"), "period": v.get("period"),
            "guide_pdf": v.get("guide_pdf"),
        }

    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    # summary
    from collections import Counter
    lv = Counter()
    for s in out["schools"].values():
        for lvl in s: lv[lvl] += 1
    print(f"kb_smart.json 생성: {len(out['schools'])}개 학교")
    print("레벨별:", dict(lv))
    # tag distribution (BA)
    tc = Counter()
    for s in out["schools"].values():
        for t in s.get("BA", {}).get("major_tags", []): tc[t] += 1
    print("BA 전공태그 분포:", dict(tc.most_common()))


if __name__ == "__main__":
    main()
