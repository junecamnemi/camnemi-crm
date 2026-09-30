# Camnemi 학비·요강 데이터 — 최종 마무리 리포트 (2026-09-30)

## 요약
이번 세션은 ①과별/계열별 등록금 데이터 완성, ②요강 가이드 라이브러리 정리, ③등록금일람표
크롤 시도·결과 확정, ④학교 레벨/타입 정리, ⑤DB 쓰기 경로 수리·정본(`cat.*`) 동기화,
⑥기본 모델 pro 전환까지 마쳤다.

## 1. 과별/계열별 학비 — `backend/tuition_by_department.json`
- **292개 학교 · BA 169 · MA 144 · 전문학사 99** (학교 중복 레벨 포함).
- 입학금은 전부 `"별도 (separate)"` 라벨, 행 값은 **수업료만** (운영자 규칙).
- 출처: 요강 계열표 · `tuition_semester_by_dept` · Pro 추출+qwen 검증 · Playwright 계열별 · 학교 공표 값.
- 검증 가드: verbatim 원문 일치, unit=unknown 환산 금지, 검증자=추출자와 다른 패밀리.
- school-level fallback(68교) + phantom 레벨 제거 + `school_type` 스탬프(4년제 305 · 전문대 101 · 전공심화 35).

## 2. 요강 가이드 라이브러리
- **1,961 → 1,554 라이브 PDF · 내용 중복 0.**
- 중복 386개는 `_dedup_removed\` 격리(삭제 아님), 구년도(2019~2025) 21개는 `_archive\`로.
- 레벨 오배정 94그룹(연세대 LANG=MA=BA 등 동일 파일이 3개 레벨에 등록) 해소 — 내용 기준 재분류 207개.
- 분포: ba 449 · ma 375 · junior 380 · lang 349. 모든 이동 `_guide_cleanup_ledger.json`에 기록 → 원복 가능.

## 3. 등록금일람표 크롤 — 측정 결과 (더 시도하지 말 것)
- 정적(urllib) · JS(Playwright) · 문서(vision) 세 경로를 다 돌렸고, **학교 단위로 못 묶는 게 확정**됐다.
- 성과: Playwright 계열별로 4건 채움(광운대 MA · 호남대 MA · 가톨릭대 성신교정 BA · 한국관광대 전문학사).
- 차단 사유(전부 실측): 검색이 다른 학교 문서 반환 · 동일 파일 5개교 배정 · 2015 교비 예산서 통과.
- 가드: md5 dedup · 문서 내 학교명 필수 · 연도≥2025 · 예산/교비/고지서 거부 · 라벨 모양 → **빈칸 > 그럴듯한 오답.**
- 27개를 닫으려면 학교별 등록금 페이지 URL을 사람이 확정한 목록이 먼저 필요.

## 4. DB 쓰기 경로 수리 + 정본 동기화 (세션 후반 핵심)
**발견**: DB가 마이그레이션 중(Phase 2 완료) — `universities`가 **VIEW**로 바뀌었는데 쓰기 스크립트
3개가 안 고쳐져 **매일 조용히 실패**하고 있었다.

- **폐기**: 07:00 `sync_programs_to_supabase_wrap.py` 크론 정지 (레거시 blob writer, 매일 실패).
- **수리**: `publish_all.py`(08:00 게시) → `universities_blob` (VIEW는 읽기전용). 311개교 정상 게시.
- **anon REST 키 401** (RLS 강화로 UPDATE 권한 상실) → 쓰기는 `psycopg2`(postgres 롤)로 전환.

### 학비 동기화 (2곳)
| 대상 | 경로 | 결과 |
|---|---|---|
| `universities_blob.tuition` (CRM 뷰) | `_sync_tuition_db.py` | 174개교 ba/ma, 0 unresolved |
| `cat.tuition` (typed 정본) | `_sync_tuition_to_cat.py` | **2,801행 / 394프로그램** (ba/ma/junior) |

- `cat.tuition` 규약: scope=college · tier=semester · unit=per_semester · 단과대명 note ·
  source_doc_id=현재 프로그램 요강 문서. 멱등(프로그램별 clear+reinsert).
- 전문학사(junior) 283 → **440행** 확충.
- **제외(운영자 확정)**: 농협대학교 · 영남외국어대학 — `cat.program`에 junior 행 없음 → `EXCLUDED_JUNIOR`.

## 5. 기본 모델
- `deepseek/deepseek-v4.1-flash` → **`deepseek/deepseek-v4-pro`** (nous, config.yaml).
- Nous 인증은 OAuth(`june@camnemi.com`) 이미 연결됨 — 별도 키 불필요.
- 어학연수·한국어과정 가격은 등록금에서 전면 제외.

## 남은 것 (Phase 3 마지막 단계, 미시행)
- `sync_kb_to_postgres.py`(verified_kb.json → cat.*)가 데일리 크론에 미편입 — cat.*는 1회 수동 채움.
- JSON export(verified_kb/consulting_db/data.js)를 cat.*에서 **재생성** + blob 폐기가 최종 단계.

## 산출물 위치
```
backend/tuition_by_department.json     정본 (292교, 2,875행급)
backend/verified_kb.json               원천 (BA 200 · MA 152 · 전문 126)
backend/_sync_tuition_db.py            blob(CRM뷰) 학비 동기화
backend/_sync_tuition_to_cat.py        cat.tuition(정본) 학비 동기화
backend/_guide_cleanup_ledger.json     가이드 이동 원장 (원복용)
backend/_fees_docs_FINDINGS.md         크롤 결론 문서
backend/FINAL_REPORT_2026-09-30.md     본 문서
```

## 커밋
`2dc407e → 3d36e12 → 9d6f59b → e2adc10 → 2972bf1 → f6c7517 → 805638d → c72b695 → 82c1e0c → 9464621 → 520efbd → 530b70b`
