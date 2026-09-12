# -*- coding: utf-8 -*-
"""Update pharmacy (약학대학) tuition data in KB — verified from official 2026 등록금 명세표.
So far only Yonsei's official 명세표 was fully parsed; mark others honestly as needs-verify."""
import json

KB_PATH = r"C:\Users\USER\camnemi-crm\backend\verified_kb.json"
kb = json.load(open(KB_PATH, encoding="utf-8"))

med = kb["medical_reqs"]["약학(Pharmacy)"]
if "tuition" not in med:
    med["tuition"] = {}
med["tuition"].update({
    "note": "약학대학(6년제) 전용 등록금. 연세대 2026 공식 명세표 파싱 완료. 타교는 일반계열 대비 확인 필요.",
    "updated": "2026-09-10",
    "schools": {
        "연세대학교": {
            "tuition": {"sem1": 6020000, "sem2_6": 5825000},
            "source": "연세대 2026학년도 학부 등록금 명세표 (yonsei.ac.kr/sites/sc/down/2026_fee1.pdf)",
            "note": "약학대학 1학년1학기 ₩6,020,000 / 이후 ~6학년 ₩5,825,000. 6년 12학기 총 약 ₩70,070,000."
        },
        "서울대학교": {
            "tuition": None,
            "source": None,
            "note": "국립대 — 약학대는 자연계열 최상위. 2025 공시 연평균 ₩6,058,797, 학기당 약 ₩300만+ (약대는 이보다 높음). 학부 등록금 일람표 미확보(대학원용만 게시) → 정확한 명세 확인 필요."
        },
        "인제대학교": {
            "tuition": None,
            "source": None,
            "note": "사립 — 약학대학 등록금 명세표 미확보. AI·컴퓨터 학기 ₩4,335,000보다 높을 것(약대 최상위). 확인 필요."
        },
        "고려대학교(세종)": {
            "tuition": None,
            "source": None,
            "note": "사립 — 약학대학 등록금은 고려대 계열 중 최고 수준(2025 공시 연 ₩9,156,000~10,223,000 자연·공학급). 세종캠퍼스 명세표 미확보 → 확인 필요."
        }
    }
})

json.dump(kb, open(KB_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("약학 등록금 KB 업데이트 완료")
print("연세대: 1학년 ₩6,020,000 / 이후 ₩5,825,000")
print("서울대/인제/고려대세종: 정확한 명세표 미확보 — 표기됨")
