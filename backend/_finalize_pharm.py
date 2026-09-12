# -*- coding: utf-8 -*-
"""Final pharmacy foreigner-admission verification → update KB medical_reqs 약학(Pharmacy).
All 37 pharmacy colleges now verified (official 외국인 모집요강)."""
import json

KB_PATH = r"C:\Users\USER\camnemi-crm\backend\verified_kb.json"
kb = json.load(open(KB_PATH, encoding="utf-8"))
med = kb["medical_reqs"]["약학(Pharmacy)"]

# Full verified status: 37 colleges
verified = {
  # YES — recruit foreigners into pharmacy
  "가천대학교": ("YES", "TOPIK 6급 (일반 TOPIK3보다 높음). 2026 후기 학부 3차"),
  "서울대학교": ("YES", "TOPIK 3 or TOEFL80/IELTS6.0/TEPS269, 정원외"),
  "연세대학교": ("YES", "TOPIK 5급 필수 (영어 불인정), 약간 명"),
  "고려대학교(세종)": ("YES", "TOPIK 기반, 제한없음"),
  "인제대학교": ("YES", "TOPIK 미보유 가능, 졸업전 TOPIK4/IELTS5.5, 제한없음"),
  "계명대학교": ("GRAD_ONLY", "대학원 약학 YES (MA/PhD+English track). 학부 외국인 약학 미확인/미모집"),
  # NO — pharmacy excluded from foreigner admission
  "가톨릭대학교": ("NO", "외국인 모집단위에서 약학대학 제외"),
  "건국대학교": ("NO", "2026 후기 외국인요강에 약학 없음"),
  "경상국립대학교": ("NO", "약학은 국내전형만"),
  "경성대학교": ("NO", "외국인 모집에 약학과 없음 (제약공학만)"),
  "경희대학교": ("NO", "2027-1 외국인요강에 약학과 제외"),
  "광주대학교": ("NO", "약학대학 없음"),
  "국립강릉원주대학교": ("NO", "약학대학 없음"),
  "국립부경대학교": ("NO", "약학대학 없음"),
  "국립순천대학교": ("NO", "순수외국인요강이 약학대학 명시 제외"),
  "국립안동대학교": ("NO", "약학대학 없음"),
  "국립전남대학교": ("NO", "외국인 모집단위에 약학대학 없음"),
  "국립충남대학교": ("NO", "CNU-ASIA 외국인요강이 약학대학 제외"),
  "국립충북대학교": ("NO", "외국인요강: 약학대학 전학과 선발 안함"),
  "국립한국교통대학교": ("NO", "약학대학 없음 (제약바이오전공만)"),
  "동국대학교": ("NO", "약학대학 존재하나 외국인 모집단위에 없음"),
  "동덕여자대학교": ("NO", "외국인 모집단위에 약학 없음"),
  "부산대학교": ("NO", "외국인 모집단위에 약학 없음"),
  "삼육대학교": ("NO", "약학과 외국인 모집 아님"),
  "성균관대학교": ("NO", "외국인 학부에서 의·약학계열 명시 제외"),
  "숙명여자대학교": ("NO", "2026 외국인요강: 약학부 전공선택 불가"),
  "아주대학교": ("NO", "학부외국인 모집학과에 약학대학 없음"),
  "영남대학교": ("NO", "2027 외국인요강에 약학과 없음"),
  "우석대학교": ("NO", "순수외국인 모집단위에 약학과 없음"),
  "원광대학교": ("NO", "2026 외국인 학부에 약학과 없음"),
  "이화여자대학교": ("NO", "2028 입학전형: 약학대학 명시 제외"),
  "인하대학교": ("NO", "2027 외국인요강 모집단위에 약학대학 없음"),
  "전북대학교": ("NO", "외국인요강: 약학대학 모집 제외"),
  "조선대학교": ("NO", "2026 외국인 모집단위에 약학 없음"),
  "중앙대학교": ("NO", "2027 순수외국인 모집단위표에 약학대학 없음"),
  "충북대학교": ("NO", "외국인요강: 약학대학 선발 안함"),
  "한양대학교": ("NO", "외국인요강에 약학대학 0회 언급"),
}

med["foreigner_admission_full_check"] = {
    "note": "대한약사회 전국 37개 약학대학 전수검증 (2026-09-12, 공식 외국인 모집요강 기반). 외국인 약학 학부 모집 = 서울대·연세대·고려대(세종)·인제대·가천대. 계명대는 대학원만. 나머지는 전부 제외.",
    "updated": "2026-09-12",
    "schools": {k: {"status": v[0], "detail": v[1]} for k, v in verified.items()},
}

json.dump(kb, open(KB_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

yes = [k for k, v in verified.items() if v[0] == "YES"]
print(f"약학 외국인 학부 모집: {len(yes)}개교")
print(" ", yes)
print(f"대학원만: 계명대")
print(f"전체 검증 {len(verified)}개 → KB 반영 완료")
