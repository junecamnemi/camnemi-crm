# -*- coding: utf-8 -*-
"""Update verified_kb.json master section with verified TOPIK-6 scholarship data
from the 2026/2027 graduate admission guide PDF scan (2026-09-03)."""
import json

KB = r"C:\Users\USER\camnemi-crm\backend\verified_kb.json"
kb = json.load(open(KB, encoding="utf-8"))
master = kb["master"]["schools"]

VERIFIED = {
    "가천대학교": "TOPIK 6급 → 입학 후 첫 2학기 등록금 100% (신입생). 출처: 2026 전기 일반대학원 외국인 특별전형 모집요강.",
    "가톨릭대학교": "TOPIK 5·6급 → 입학 당해 학기 입학금 전액 + 수업료 90% (외국인 신입생 장학금 우수A). 출처: 외국인전형 일반대학원 모집요강.",
    "건국대학교": "TOPIK 6급 또는 공인영어(TOEFL 71 등) → 수업료 50% (외국인 신입생 1학기 일반계). 출처: 2026 후기 대학원 외국인전형 모집요강.",
    "계명대학교": "TOPIK 6급 → 수업료 70% (외국인장학5); TOPIK 6급 + 직전학기 평균 95점 이상 → 수업료 100% (외국인특별우수장학). 출처: 2026 후기 일반대학원 모집요강.",
    "국립부경대학교": "TOPIK 6급 → 첫 학기 등록금 100% (A등급) [학부 입학장학 기준; 대학원 별도 확인]. 출처: 2026학년도 1학기 외국인 학부 및 대학원 신·편입생 모집요강.",
    "국립창원대학교": "TOPIK 6급 → 450,000원 지급. 출처: 2026 후기 추가 대학원 외국인 신입생 모집요강.",
    "국민대학교": "자연/공학/예체능계열 TOPIK 6급 → 수업료 100%; 인문계열 70%. 출처: 2026 전기 일반대학원 모집요강.",
    "대구가톨릭대학교": "TOPIK 6급 (또는 TOEFL PBT 590/iBT 95, TEPS 700, IELTS 7.0, TOEIC 800) → 첫 학기 수업료 전액, 잔여 학기 수업료 4/5. 출처: 2026 후기 일반대학원 외국인 신입생 모집요강.",
    "부산외국어대학교": "토픽 6급 취득자 + 학부 평균 4.3 이상 등 → 입학금 50% + 수업료 100% (우수외국인 학생). 출처: 2026 후기 대학원 외국인 유학생 모집요강.",
    "서울여자대학교": "TOPIK 6급 → 입학금+수업료 70%. 출처: 2026 후기 추가모집 일반대학원 외국인전형.",
    "이화여자대학교": "TOPIK 6급 중 입학평가 우수자 → 등록금 전액 (입학금 포함). 출처: 2026 전기 외국인특별전형 모집요강.",
    "전북대학교": "TOPIK 장학금 예시 (전일제 신입생 전원 최대 80% 등록금 감면). 출처: 2026 후기 대학원 외국인 특별전형 모집요강.",
    "중부대학교": "TOPIK 6급 → 수업료 50%. 출처: 2026 후기 대학원 외국인 특별전형 모집요강.",
    "중앙대학교": "TOPIK 6급 또는 TOEFL iBT 91 / TOEIC 780 / IELTS 6.5 → 수업료 100%. 출처: 2026학년도 후반기 일반대학원 외국인전형 모집요강.",
    "평택대학교": "대학원 신입생 TOPIK 6급 → 수업료 100% (재학생 80%). 출처: 2026 전기 외국인특별전형 모집요강.",
    "한경국립대학교": "TOPIK 6급 또는 IELTS 9.0 이상 → 등록금 전액 (Full Tuition Waiver). 출처: 2027 전기 외국인 특별전형 모집요강.",
    "한국공학대학교": "TOPIK 6급(신입) 및 평점 4.0 이상(재학) → 특수대학원 장학. 출처: 2026 후기 대학원 입학전형 안내.",
    "협성대학교": "TOPIK 6급 → 1,600,000원. 출처: 2026 후기(2차) 일반대학원 모집요강.",
    "호남대학교": "석·박사 TOPIK 4~6급 → 학비 50~70% 감면. 출처: 2026 전기 대학원 외국인 신(편)입생 모집요강.",
}

CORRECTIONS = {
    "성신여자대학교": "원본 요강: 외국인 신입생 수업료 20~70% (TOPIK 급수별 세부 기준 미명시). 기존 'TOPIK 6급 → 70%'는 요강 미확인 → 수정."
}

updated = 0
for name, info in VERIFIED.items():
    if name in master:
        master[name]["scholarship_topik6_verified"] = info
        master[name]["scholarship_topik6_verified_src"] = "2026/2027 대학원 원본 모집요강 스캔 (2026-09-03)"
        updated += 1
    else:
        print("MISSING in master:", name)

for name, corr in CORRECTIONS.items():
    if name in master:
        master[name]["scholarship_topik6_verified"] = corr
        master[name]["scholarship_topik6_verified_src"] = "2026 전기 일반대학원 모집요강 원본 확인 (2026-09-03)"
        updated += 1

json.dump(kb, open(KB, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"KB updated: {updated} schools")
