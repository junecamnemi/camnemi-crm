# -*- coding: utf-8 -*-
"""Update Konyang Univ (건양대) D-2/D-4 foreigner admission data in verified_kb.json.
Verified 2026-09-07 from official sources (interedu.konyang.ac.kr + 2026 외국인 요강)."""
import json

KB_PATH = r"C:\Users\USER\camnemi-crm\backend\verified_kb.json"
kb = json.load(open(KB_PATH, encoding="utf-8"))

# ---- lang_programs: 건양대 D-4 어학연수 ----
lang = kb["lang_programs"]["schools"]
lang["건양대"] = {
    "region": "충청남도",
    "tuition_range": {"min": 4400000, "max": 4400000},  # 1년 수업료
    "tuition_note": "₩4,400,000/1년 (입학금 10만 + 전형료 10만 + 기숙사 91만/15주 + 보험 15만 별도, 총 약 ₩5,660,000)",
    "structure": {"per_term": "15주", "total_hours": "학위과정 1학기 6개월", "per_day": None},
    "is_200h_10wk": False,
    "d4_eligible": True,
    "dorm": True,
    "period": "2026 4쿼터: 원서접수 2026.9.1~10.10(유웨이 kyuklc.uway.com), 서류 10.21, 등록금 10.21까지, 표준입학허가서 10.30, 지정입국 11.27/12.11, 학기시작 11.30",
    "guide_url": "https://interedu.konyang.ac.kr/interedu/sub05_03.do",
    "qualification": "부모 모두 외국인 + 모국 12년 정규교육 이수. 고교 졸업 후 2년 이내(성적 100점만점 70점+) 또는 대학 졸업 후 2년 이내(GPA 4.5만점 3.0+). 결석 5회 이하. 비자심사 무결격.",
    "documents": "입학신청서, 여권·신분증, 가족관계증명, 학력증명+아포스티유, 부모 재직·수입증명, 은행잔고 USD 5,000+(6개월 동결), 사진 5매",
    "scholarship": "정착지원금 50만원/1년, TOPIK 2급 보유자 2쿼터 등록금 30%(66만원) 할인",
    "visa": "D-4 입국, 6개월마다 연장(최장 2년). D-4 외 비자로 변경 시 환불 불가",
    "note": "2026학년도 4쿼터(겨울) 모집 2026.9.2 공고. 입국 시 결핵·홍역확인서 필수. 3+1, 2+2 제도 운영.",
    "verified": "2026-09-07",
}
json.dump(kb, open(KB_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"건양대 어학연수 반영 완료")
print(f"  D4 수업료: {lang['건양대']['tuition_range']}")
print(f"  D4 기간: {lang['건양대']['period'][:60]}...")
