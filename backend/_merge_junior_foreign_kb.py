# -*- coding: utf-8 -*-
"""Merge foreigner-guide scan + status into verified_kb.json junior section.
Adds per-school: foreign_guide (status), foreign_topik, foreign_tuition, foreign_majors,
guide_type (combined/degree), guide_pdf path, and flags for closed/merged."""
import json, os

KB_PATH = r"C:\Users\USER\camnemi-crm\backend\verified_kb.json"
SCAN = json.load(open(r"C:\Users\USER\camnemi-crm\backend\_junior_foreign_scan.json", encoding="utf-8"))
STATUS = json.load(open(r"C:\Users\USER\camnemi-crm\backend\_junior_foreign_status.json", encoding="utf-8"))
SAVEDIR = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project\adiga_2026_전문대학_모집요강"

kb = json.load(open(KB_PATH, encoding="utf-8"))
js = kb["junior"]["schools"]

def norm(s): return s.replace("대학교","").replace("대학","").replace("전문대","").replace(" ","")

# build scan lookup by normalized key
scan_by_norm = {norm(s): v for s,v in SCAN.items()}
status_by_norm = {norm(s): v for s,v in STATUS.items()}

count=0
for school, entry in js.items():
    sn = norm(school)
    st = status_by_norm.get(sn)
    sc = scan_by_norm.get(sn)
    # clear stale foreign fields
    for k in ["foreign_guide","foreign_topik","foreign_tuition","foreign_majors","guide_type","foreign_guide_pdf","excluded","exclude_reason"]:
        entry.pop(k, None)

    if st:
        entry["foreign_guide"] = st["foreign_guide"]
        if st["foreign_guide"]=="closed":
            entry["excluded"]=True
            entry["exclude_reason"]="폐교 (2026.08.31 운영재단 파산, 입학 모집 중단)"
        elif st["foreign_guide"]=="merged":
            entry["excluded"]=True
            entry["exclude_reason"]="조선대학교에 통합 (2027부터 4년제 간호대학 전환)"
        elif st["foreign_guide"]=="no_public_guide":
            entry["foreign_guide_note"]="외국인 전형 요강 미공개 — 국제교류처/유학원 경유 필요"
        count+=1

    if sc and "error" not in sc:
        entry["foreign_topik"] = sc.get("topik_req")
        entry["foreign_tuition"] = sc.get("tuition")
        if sc.get("majors"):
            entry["foreign_majors"] = sc["majors"]
        entry["guide_type"] = sc.get("guide_type")
        entry["foreign_guide_pdf"] = os.path.join(SAVEDIR, sc["file"])
        entry["foreign_period"] = sc.get("period")

kb["junior"]["foreign_guide_note"] = ("전문대 외국인 전용 요강 현황(2026-09-06): 16개 학교 외국인 요강 확보·분석. "
    "20개 학교는 외국인 요강 미공개(유학원 경유). 광양보건대 폐교, 조선간호대 조선대 통합. "
    "일부 학교는 어학연수+전문학사+전공심화를 하나의 외국인 요강으로 통합 제공.")
kb["junior"]["foreign_guide_updated"] = "2026-09-06"

json.dump(kb, open(KB_PATH,"w",encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"junior 반영 완료: {count}개 학교에 foreign_guide/폐교·통합 플래그, 16개 학교에 외국인 전용 데이터")
n_foreign = sum(1 for s in js.values() if s.get("foreign_guide")=="obtained")
n_closed = sum(1 for s in js.values() if s.get("exclude_reason") and "폐교" in s.get("exclude_reason",""))
n_merged = sum(1 for s in js.values() if s.get("exclude_reason") and "통합" in s.get("exclude_reason",""))
n_topik = sum(1 for s in js.values() if s.get("foreign_topik"))
n_tuit = sum(1 for s in js.values() if s.get("foreign_tuition"))
print(f"외국인요강 {n_foreign} | TOPIK {n_topik} | 등록금 {n_tuit} | 폐교 {n_closed} | 통합 {n_merged}")
