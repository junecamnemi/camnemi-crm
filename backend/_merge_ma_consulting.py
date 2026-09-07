# -*- coding: utf-8 -*-
"""Step 2: Merge MA scan (topik/ielts/toefl/tuition/scholarship) into consulting_db
MA programs. Also compute popular/similar majors for each level."""
import json, re

DB = r"C:\Users\USER\camnemi-crm\backend\consulting_db.json"
SCAN = json.load(open(r"C:\Users\USER\camnemi-crm\backend\_ma_scan_lang.json", encoding="utf-8"))
db = json.load(open(DB, encoding="utf-8"))
schools = db["schools"]

def norm(s): return re.sub(r"\[.*?\]","",s).replace("대학교","").replace("대학","").replace(" ","")

# popular-major keyword groups (for 인기과/유사과 analysis)
POPULAR = {
    "business": ["경영","회계","경제","국제경영","무역","마케팅","금융"],
    "cs": ["컴퓨터","소프트웨어","인공지능","데이터사이언스","AI","정보통신","전자"],
    "engineering": ["기계","전자","전기","화학공학","산업공학","건축","토목","식품공학"],
    "health": ["간호","보건","간호학","의료","보건행정"],
    "beauty": ["뷰티","미용","화장품","향장","코스메틱","피부"],
    "culinary": ["조리","호텔외식","외식","식품","바리스타","제과"],
    "aviation": ["항공","항공서비스","승무","항공운항"],
    "design": ["디자인","시각디자인","패션","건축디자인","미디어디자인"],
    "education": ["유아교육","보육","교육"],
    "media": ["미디어","방송","콘텐츠","영상","광고","신문"],
}
SIMILAR = {
    "business": ["경제학과","무역학과","경영정보학과","세무학과"],
    "cs": ["빅데이터학과","정보보안학과","로봇공학과","AI융합학과","게임학과"],
    "health": ["물리치료학과","작업치료학과","임상병리학과","응급구조학과","치위생학과"],
    "beauty": ["메디컬뷰티","네일","헤어디자인","패션뷰티"],
    "culinary": ["호텔조리","한식조리","제과제빵","식품영양학과"],
    "design": ["시각디자인학과","산업디자인학과","콘텐츠디자인"],
}

def analyze_majors(majors):
    if not majors: return None
    if isinstance(majors, str): majors=[m.strip() for m in majors.replace("/"," ").split() if m.strip()]
    if not isinstance(majors, list): return None
    # find popular categories present
    present=[]
    for cat, kws in POPULAR.items():
        if any(any(kw in m for kw in kws) for m in majors):
            present.append(cat)
    similar=[]
    for cat in present:
        for s in SIMILAR.get(cat,[]):
            similar.append(s)
    return {"popular": present, "similar": list(dict.fromkeys(similar))[:8]}

# merge MA scan
merged=0
for n, v in SCAN.items():
    sn = norm(n)
    target=None
    for k,s in schools.items():
        if norm(k)==sn:
            target=s; break
    if not target: continue
    prog = target["programs"].setdefault("MA", {})
    if v.get("topik") and not prog.get("topik"): prog["topik"]=v["topik"]; merged+=1
    if v.get("ielts") and not prog.get("ielts"): prog["ielts"]=v["ielts"]; merged+=1
    if v.get("toefl") and not prog.get("toefl"): prog["toefl"]=v["toefl"]
    if v.get("tuition") and not prog.get("tuition"): prog["tuition"]=v["tuition"]; merged+=1
    if v.get("scholarship") and not prog.get("scholarship"): prog["scholarship"]=v["scholarship"]; merged+=1
    if v.get("period") and not prog.get("period"): prog["period"]=v["period"]

# compute popular/similar for all levels
for k,s in schools.items():
    for level, prog in s["programs"].items():
        if isinstance(prog, dict) and prog.get("majors"):
            analysis = analyze_majors(prog["majors"])
            if analysis:
                prog["popular_majors"]=analysis["popular"]
                prog["similar_majors"]=analysis["similar"]

json.dump(db, open(DB,"w",encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"MA 갭 병합 {merged} 필드 | 인기과/유사과 분석 완료")

# summary
n_ma_topik=sum(1 for s in schools.values() if s["programs"].get("MA",{}).get("topik"))
n_ma_ielts=sum(1 for s in schools.values() if s["programs"].get("MA",{}).get("ielts"))
n_ma_tuit=sum(1 for s in schools.values() if s["programs"].get("MA",{}).get("tuition"))
n_popular=sum(1 for s in schools.values() if any(p.get("popular_majors") for p in s["programs"].values()))
print(f"MA: TOPIK {n_ma_topik} | IELTS {n_ma_ielts} | 수업료 {n_ma_tuit} | 인기과 분석 {n_popular}개 학교")
