# Camnemi 데이터 단일소스(원소스) 파이프라인 + 검증 체계

> 목표: **하나의 정본(canonical) 저장소** → 모든 산출물(Supabase·KB·워크북·사이트)이 여기서 파생.
> 모집공고가 갱신되면 자동 반영 + 검증을 통과해야만 게시.

## 1. 구조

```
[수집]  adiga 모집요강 PDF · 대학알리미 API · 대학 홈페이지 · CRM(수기)
   │
[추출]  LLM(deepseek-v4-pro) 구조화 파싱 (스키마 고정)
   │
[정규화] 학교명 병합 · 트랙 판정 · 학부 매칭 · 등급/학과 코드 통일
   │
[정본]  ★ canonical/schools.jsonl  ← 유일한 진실 원천(source of truth)
   │      per-school: meta + programs{ba,ma,junior,lang} + sources + validation
   │
[검증]  schema · 교차검증(모집요강↔대학알리미) · 커버리지 게이트 · 정합성
   │      → 통과 못하면 게시 차단, 리포트 발행
   │
[게시]  ① Supabase universities.programs (사이트)
        ② verified_kb / consulting_db (CRM·봇)
        ③ Camnemi_University_Programs.xlsx (Drive)
        ④ 봇/상담 RAG 인덱스
```

## 2. 정본 스키마 (canonical)

```json
{
  "school": "전북대학교",
  "aliases": ["전북대", "JBNU", "국립전북대학교"],
  "meta": {"students": 23561, "type": "국립", "loc": "전북 전주",
           "logo": "logos/xxx.png", "photo": "photos/xxx.jpg"},
  "programs": {
    "ba": {
      "label": "BA (Bachelor)", "period": "2026 ...",
      "req": {"topik": 2, "ielts": 5.5, "toefl": 71},
      "track_policy": "per_department",           // per_department | unified
      "colleges": [
        {"college": "공과대학", "tuition_krw": 2704000,
         "departments": [
            {"major": "기계공학과", "korean_track": true, "english_track": false,
             "topik": 2, "ielts": null}
         ]}
      ],
      "scholarships": [{"name": "성적우수", "criteria": "...", "award": "..."}]
    },
    "ma": {...}, "junior": {...}, "lang": {...}
  },
  "sources": {
    "guide_pdf": ["adiga/.../전북대_외국인.pdf"],
    "academyinfo": {"schlId": "0000025", "tuition_v8": {...}},
    "kb": "verified_kb:전북대학교"
  },
  "validation": {"schema_ok": true, "coverage": {...}, "conflicts": [],
                 "checked_at": "2026-09-14T20:00"}
}
```

## 3. 검증 규칙 (게시 게이트)

| # | 규칙 | 실패 시 |
|---|---|---|
| V1 | 스키마 필수 필드(school, programs, sources) | 차단 |
| V2 | 트랙 정합성: 영어트랙 학과는 ielts 값 필수 / 한국어트랙은 topik 필수 | 경고+수정 |
| V3 | 등록금 > 0 이고 ≤ 20,000,000 (이상치 탐지) | 경고 |
| V4 | 교차검증: 모집요강 등록금 ↔ 대학알리미 계열값 차이 ≤ 25% | 경고(수동확인) |
| V5 | 커버리지: 등록금 ≥ 90% · 트랙 ≥ 85% · 장학금 ≥ 60% | 리포트 |
| V6 | 학과수 이상: 학부 합 ≠ 학교 총합 | 경고 |
| V7 | 중복 학교(정규화 키 동일) | 자동 병합 |

## 4. 실행

```
① build_canonical.py    PDF+API+KB → canonical/schools.jsonl
② validate_canonical.py 규칙 V1~V7 → validation_report.md (exit≠0 시 게시 차단)
③ publish_all.py        canonical → Supabase / KB / xlsx / RAG
④ cron: 일 1회 (모집요강 수집 다음) — 변동분만 재게시
```

## 5. 리포트

```
· validation_report.md : 규칙별 통과/실패 · 학교별 이슈 목록
· diff_report.md       : 전일 대비 변동(신규 학교·등록금 변경·요건 변경)
→ 텔레그램 알림 (변동 있을 때만)
```

---

## 현황 진단 (기존 자산)

| 자산 | 위치 | 역할 |
|---|---|---|
| 모집요강 PDF | 내 드라이브/adiga_2026_* | 원천 (686교/809 PDF) |
| 파싱 캐시 | _schools_parsed.jsonl (760) | 추출 결과 |
| 대학알리미 등록금 | _tuition_acad.jsonl (293교/11,738행) | 교차검증 소스 |
| KB | camnemi-crm/backend/verified_kb.json | 수기 검증분 |
| 컨설팅DB | consulting_db.json (395교) | 상담용 |
| 워크북 | Camnemi_University_Programs.xlsx (315교) | 산출물 |
| Supabase | universities.programs (292교) | 사이트 |

**문제**: 각자 파편화 · 서로 불일치 · 원천 추적 불가 → **정본으로 통합 필요**
