당신은 Camnemi(캄보디아 학생 한국 유학 상담) 데이터 감사관입니다. 실제 파일을 직접 열어 조사하고 정직하게 보고하세요. 추측 금지, 실제 계산만.

## 배경
3계층 데이터: verified_kb.json (원본) → consulting_db.json (상담용) → data.js (라이브 사이트).
사용자 의문: "KB 성능이 떨어진 것 같다. 등록금/장학금을 잘 분석했는데 봇/사이트에 반영이 안 된 것 같다."

## 작업 디렉터리
C:\Users\USER\camnemi-crm  (backend\ 안에 json들, 루트에 data.js)

## 조사 항목 (python3 대신 python 사용)
1. backend\verified_kb.json 실제 스케일: 최상위 키 목록. schools(BA)/master.schools(MA)/junior.schools/lang_programs.schools 각 학교 수. medical_reqs, ai_departments, free_major_programs, visa_restricted_2026 섹션 존재와 규모.
2. 각 레벨별 필드 커버리지(%) 실제 계산: tuition(수업료), scholarship(장학금), period(지원시기), topik_req, ielts_req, majors. 표로.
3. backend\consulting_db.json: 학교 수, 레벨별(BA/MA/전문학사/어학연수) 프로그램 수, 동일 필드 커버리지. verified_kb와 어긋나면 어디서.
4. data.js: 총 학교 수, type=='univ'(4년제)/'junior' 수. scholarships/period/tuition 보유 학교 수(%). 파일은 JS라 JSON 파싱 필요: content.find('[') 후 bracket 매칭으로 json.loads.
5. 불일치 진단: verified_kb에는 있으나 data.js에 없는 것을 실제로 세기. 어느 레벨/필드가 가장 누락됐는지.
6. 결론: KB가 실제로 부실한지 vs 동기화 누락인지 판정. 우선순위 갭 TOP 5 (구체적 학교명/필드명).

## 출력
- 항목별 실제 수치 (계산 근거)
- 최종 verdict
- 우선순위 갭 TOP 5 + 권장 조치
한국어로 간결하게.
