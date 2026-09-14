#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""경운대학교 대학원(석사/박사) 외국인입학 특별장학금 (행복특A~B) → KB 반영 + 출처 기록.

Source: 2026학년도 경운대학교 대학원 후기 신입생 추가 2차 모집요강, '10. 장학제도 안내'
PDF: adiga_2026_대학원_모집요강/경운대학교_대학원_모집요강.pdf
"""
import json, os, shutil, datetime

B = r"C:\Users\USER\camnemi-crm\backend"
KB = os.path.join(B, "verified_kb.json")
CDB = os.path.join(B, "consulting_db.json")

kb = json.load(open(KB, encoding="utf-8"))
shutil.copy(KB, KB.replace(".json", f"_bak_kwgrad_{datetime.date.today()}.json"))
m = kb["master"]["schools"]["경운대학교"]

m["scholarships_categorized"] = [
    {
        "name": "외국인입학 특별장학금 (입학 첫 학기)",
        "type": "enroll",
        "category": "language",
        "tiers": [
            {"score_type": "TOPIK/IELTS", "score": "TOPIK 5급 이상 (또는 한국어교육과정 4급 수료 / IELTS 7.0 / TOEIC 900 / TOEFL iBT 90 / SKA 5급)",
             "amount": "입학금 + 첫학기 수업료 100%"},
            {"score_type": "TOPIK/IELTS", "score": "TOPIK 4급 이상 (또는 IELTS 6.5 / TOEIC 800 / TOEFL iBT 80 / SKA 4급)",
             "amount": "첫학기 수업료 100%"},
            {"score_type": "TOPIK/IELTS", "score": "TOPIK 3급 (또는 한국어교육과정 3급 수료 / IELTS 6.0 / TOEIC 700 / TOEFL iBT 70 / SKA 3급)",
             "amount": "입학금 100% + 첫학기 수업료 50%"},
            {"score_type": "TOPIK/IELTS", "score": "한국어능력시험 합격자 (또는 IELTS 5.5 / TOEIC 650 / TOEFL iBT 65)",
             "amount": "첫학기 수업료 50%"},
        ],
    },
]
m["scholarship_source"] = {
    "type": "모집요강",
    "guide": "2026학년도 경운대학교 대학원 후기 신입생 추가 2차 모집요강 — '10. 장학제도 안내'",
    "pdf": "adiga_2026_대학원_모집요강/경운대학교_대학원_모집요강.pdf",
    "verified": "2026-09-12",
    "note": "학부 장학기준과 다름(학부는 국제처 웹 기준: TOPIK4→70%/IELTS5.5→20%). 대학원은 TOPIK4→100%/IELTS5.5→50%.",
}
m["scholarships_verified"] = True

open(KB, "w", encoding="utf-8", newline="\n").write(json.dumps(kb, ensure_ascii=False, indent=1) + "\n")
print("verified_kb master.경운대학교 장학금 반영 완료")
for t in m["scholarships_categorized"][0]["tiers"]:
    print(f"  - {t['score'][:55]} → {t['amount']}")
print("  source:", m["scholarship_source"]["guide"])

# mirror
cdb = json.load(open(CDB, encoding="utf-8"))
if "경운대학교" in cdb["schools"]:
    ma = (cdb["schools"]["경운대학교"].get("programs") or {}).get("MA")
    if ma is not None:
        ma["scholarship"] = m["scholarships_categorized"]
        ma["scholarship_source"] = m["scholarship_source"]["guide"]
    open(CDB, "w", encoding="utf-8", newline="\n").write(json.dumps(cdb, ensure_ascii=False, indent=1) + "\n")
    print("consulting_db 반영 완료")
