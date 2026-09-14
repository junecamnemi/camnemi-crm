# -*- coding: utf-8 -*-
"""Build structured lang_bypass field for 경운대 (exemplar) from official 2026 외국인 요강.
8 paths, incl. the missed ones: 협정기관/해외센터 추천(⑥), 정부/지자체 추천·전담학과 완화(⑦)."""
import json

KB = r"C:\Users\USER\camnemi-crm\backend\verified_kb.json"
kb = json.load(open(KB, encoding="utf-8"))

kyungwoon = {
  "note": "출처: 경운대 2026 외국인 모집요강 p.15 어학요건. 아래 '하나 이상' 충족 시 지원 가능.",
  "paths": [
    {"no": 1, "type": "TOPIK", "desc": "TOPIK 3급 이상", "bypass": False},
    {"no": 2, "type": "selftest", "desc": "경운대 한국어능력시험 3급 이상 합격 OR 경운대 한국어교육과정 3급 이상 수료", "bypass": True,
     "note": "국외 실시는 협력대학·현지센터에 위탁 가능 → 현지에서 응시 가능"},
    {"no": 3, "type": "sejong", "desc": "세종학당 중급과정 이상 이수 OR SKA 3급 이상", "bypass": True},
    {"no": 4, "type": "kiip", "desc": "사회통합프로그램(KIIP) 3단계 이상 OR 사전평가 61점 이상", "bypass": True},
    {"no": 5, "type": "english", "desc": "TOEFL 530(CBT197,iBT71)/IELTS 5.5/TEPS 600(NEW326)/CEFR B2/TOEIC 600 이상", "bypass": True},
    {"no": 6, "type": "recommend_org", "desc": "경운대와 협약한 고등교육기관장 또는 경운대 해외센터(글로벌교류·한국어교육) 추천자", "bypass": True,
     "note": "협정기관 추천서 원본 제출. 협약에 의한 입학은 한국어 인정기준 별도 가능", "key": True},
    {"no": 7, "type": "recommend_gov", "desc": "교육부장관 추천 위탁생/교환학생/정부초청장학생(GKS)/지자체 추천장학생/외국정부지원장학생/예체능입학생/외국인전담학과/이중언어과정 입학생 → 기준 완화 가능", "bypass": True, "key": True},
    {"no": 8, "type": "eng_native", "desc": "영어 모국어국(미국·영국·캐나다·남아공·뉴질랜드·호주·아일랜드 7개국) 국적자 또는 영어권 중·고교 이수자 → 영어능력 충족 간주", "bypass": True},
  ],
  "floor": "TOPIK 2급 이하/미소지자는 본교 별도 한국어교육과정 수강 필수",
  "unrecognized": "검정고시·홈스쿨링·사이버학습 불인정",
}

kb["schools"]["경운대학교"]["lang_bypass"] = kyungwoon
json.dump(kb, open(KB, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("경운대 lang_bypass 저장 완료 (8 paths)")
print("우회 핵심: ②자체시험 ③세종 ④KIIP ⑤영어 ⑥협정기관추천 ⑦정부/지자체추천 ⑧영어모국어")
