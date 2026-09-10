# -*- coding: utf-8 -*-
"""Update KB lang_programs with verified Seoul top-university Winter-2026 (Dec) D-4 data.
Verified 2026-09-10 from official .ac.kr sites (서울대/연세/고려/성균관/한국외대/서강/이화/한양/중앙/경희/동국/건국)."""
import json

KB_PATH = r"C:\Users\USER\camnemi-crm\backend\verified_kb.json"
kb = json.load(open(KB_PATH, encoding="utf-8"))
lp = kb["lang_programs"]["schools"]

# normalize lookup: KB key -> school norm
def norm(s):
    import re
    s = re.sub(r"\[.*?\]","",s).replace("대학교","").replace("대학","").replace(" ","")
    while s.endswith(("대","학")) and len(s)>1: s=s[:-1]
    return s.replace(" ","")

data = {
 "서울대학교": {"tuition_range":{"min":1650000,"max":1800000},
   "period":"2026 겨울 12.7~2027.2.12, 접수 8.3~9.22(오후반 165만/오전 180만/연구 145만, 지원료 10만), D-4 2학기 등록"},
 "연세대학교": {"tuition_range":{"min":1860000,"max":1860000},
   "period":"2026 겨울 12.1~2027.2.12, 접수 9.7~10.16(등록 10.23), 전형료 12만, D-4 2학기 등록, TOPIK 배치 불반영"},
 "고려대학교": {"tuition_range":{"min":1800000,"max":1800000},
   "period":"2026 겨울 12.11~2027.2.25, 접수 9.7~10.28, 전형료 12만, D-4 2학기, 원본서류 10.14까지"},
 "성균관대학교": {"tuition_range":{"min":1500000,"max":1780000},
   "period":"2026 겨울(4학기) 12.2~2027.2.17, 접수 9.7~10.23(네팔·몽골·미얀마·방글라데시·베트남 10.1), 전형료 8만, 서울 인사캠 178만/수원 150만"},
 "한국외국어대학교": {"tuition_range":{"min":1600000,"max":1600000},
   "period":"2026 겨울 12.1~2027.2.12, 접수 9.1~10.30(결핵고위험·중점관리국 10.16), 보험료 3만+전형료 10만"},
 "서강대학교": {"tuition_range":{"min":1860000,"max":1860000},
   "period":"2026 겨울 12.3~2027.2.22, 서류 9.10~10.22(선착순), 전형료 10만, KGP200 정규"},
 "이화여자대학교": {"tuition_range":{"min":1850000,"max":1850000},
   "period":"2026 겨울 12.1~2027.2.12, 접수 9.7~10.27, 입학금 12만+수강료 185만, 여대"},
 "한양대학교": {"tuition_range":{"min":1850000,"max":1850000},
   "period":"2026 겨울 12.2~2027.2.12, 접수 9.9~10.8, 접수비 15만, 레벨테스트 11.24"},
 "중앙대학교": {"tuition_range":{"min":1700000,"max":1700000},
   "period":"2026 겨울 12.7~2027.2.16, 접수 8.31~10.23(캄보디아 등 기타국/중국일본 10.30/베트남몽골 등 10.9), 전형료 10만, 서울 170만/안성 150만"},
 "경희대학교": {"tuition_range":{"min":1850000,"max":1850000},
   "period":"2026 겨울 12.14~2027.2.25, 접수 9.7~10.30, 지원료 12만, D-4-1 2학기 일괄납부"},
 "동국대학교": {"tuition_range":{"min":1800000,"max":1800000},
   "period":"2026 겨울 12.14~2027.2.26, 접수 9.21~11.15(비자필요)/11.22(불요), 전형료 10만"},
 "건국대학교": {"tuition_range":{"min":1800000,"max":1800000},
   "period":"2026 겨울 12.2~2027.2.15, 상시·단계별 접수, 전형료 15만"},
}

# KB keys present
keymap = {}
for k in lp:
    keymap[norm(k)] = k

updated=0
for school, info in data.items():
    sn = norm(school)
    key = keymap.get(sn)
    if not key:
        # fuzzy
        for nk in lp:
            if sn in norm(nk) or norm(nk) in sn:
                key=nk; break
    if not key:
        print(f"  ✗ 키 없음: {school}")
        continue
    lp[key]["tuition_range"] = info["tuition_range"]
    lp[key]["period"] = info["period"]
    lp[key]["period_note"] = "2026 겨울학기(12월) D-4, 검증 2026-09-10"
    lp[key]["d4_eligible"] = True
    lp[key]["verified_winter_2026"] = True
    updated+=1

json.dump(kb, open(KB_PATH,"w",encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"서울 상위권 겨울 D-4 업데이트: {updated}개 학교")
