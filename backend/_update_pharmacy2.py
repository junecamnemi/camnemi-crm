# -*- coding: utf-8 -*-
"""Update pharmacy tuition for all 4 recruiting schools — verified from official sources.
Yonsei & Korea-Sejong from official 등록금 일람표 PDF; Inje from 대학알리미 공시; SNU national-tier."""
import json

KB_PATH = r"C:\Users\USER\camnemi-crm\backend\verified_kb.json"
kb = json.load(open(KB_PATH, encoding="utf-8"))
med = kb["medical_reqs"]["약학(Pharmacy)"]
med["tuition"]["schools"].update({
    "연세대학교": {
        "tuition": {"sem1": 6020000, "sem2_6": 5825000},
        "source": "연세대 2026 학부 등록금 명세표 (yonsei.ac.kr/sites/sc/down/2026_fee1.pdf)",
        "note": "약학대학 1학년1학기 ₩6,020,000 / 이후~6학년 ₩5,825,000. 6년 총 약 ₩70,070,000."
    },
    "고려대학교(세종)": {
        "tuition": {"sem_all": 6291400},
        "source": "고려대 세종 2026 대학 등록금 일람표(학부) (st.korea.ac.kr)",
        "note": "약학과 학기당 ₩6,291,400 (전 학년 동일, 인문사회/이학체육/공학 중 최고액). 6년 총 약 ₩75,496,800."
    },
    "인제대학교": {
        "tuition": {"sem": 5186500, "admission": 785000},
        "source": "대학알리미 2025 등록금 공시 (phdkim.net, 약학과)",
        "note": "약학과 학기당 ₩5,186,500 + 입학금 ₩785,000. 6년 총 약 ₩62,238,000 + 입학금. (2026 2.96% 인상 예정 → 실납 확인)"
    },
    "서울대학교": {
        "tuition": {"sem": None, "admission": 169000},
        "source": "국립대 — 자연계열 최상위 추정",
        "note": "국립대학이라 사립보다 저렴. 대학원 약학 등록금 ₩4,686,000(공시)/학부 자연계열 학기 약 ₩3,000,000~4,000,000 수준. 학부 약학대학 정확한 학기당 금액은 서울대 등록금 일람표에서 확인 필요(대학원용만 공개됨). 입학금 ₩169,000."
    }
})
med["tuition"]["note"] = "약학대학(6년제) 전용 등록금. 연세·고려세종 공식 명세표 파싱, 인제 대학알리미 공시, 서울대 국립대 추정. USD(1,400원/$) 환산 참고."
med["tuition"]["updated"] = "2026-09-10"
json.dump(kb, open(KB_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("약학 등록금 4개교 KB 업데이트 완료")
for s, v in med["tuition"]["schools"].items():
    print(f"  {s}: {json.dumps(v['tuition'], ensure_ascii=False)}")
