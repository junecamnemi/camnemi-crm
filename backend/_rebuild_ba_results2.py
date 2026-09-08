# -*- coding: utf-8 -*-
"""Add BA_0 and BA_3 tuition from transcripts (they were lost to overwrites)."""
import json

RESULTS = r"C:\Users\USER\camnemi-crm\backend\_ba_tuition_results.json"
results = json.load(open(RESULTS, encoding="utf-8"))

# BA_0 from task-0 transcript (경동~한서)
BA0 = {
 "경동대학교": (3061000,4319000,"경동대 2021 공시, 2026 동결. 최저 인문 3,061,000~최고 예체능·보건 4,319,000"),
 "강서대학교": (3098000,4418000,"강서대 2023 공시. 최저 인문(신학·복지) 3,098,000~최고 간호 4,418,000"),
 "나사렛대학교": (3290000,4200000,"나사렛대 2021 공시. 인문 3,290,000~보건·예체능 4,200,000"),
 "대전가톨릭대학교": (None,None,"학부 등록금 미공시(대학알리미에 석사 신학과만). 팩트로 채우지 않음"),
 "대전대학교": (3400000,4200000,"대전대 2025 공시 평균 7,453,900/yr+2026 2.95% 인상 추정. 인문~공학 추정"),
 "대진대학교": (3613000,4717000,"대진대 2027 모집요강 등록예치금. 최저 인문 3,613,000~최고 예체능·공학 4,717,000"),
 "루터대학교": (3150000,None,"루터대 2021 공시, 전학과 동일 3,150,000"),
 "청주대학교": (3562000,None,"청주대 2025 입학처 Q&A 무역학과 3,562,000(인문·상경)"),
 "칼빈대학교": (3510000,4350000,"칼빈대 2023 공시. 신학부 3,510,000~예체능·공학 4,350,000"),
 "한서대학교": (4444000,None,"한서대 2023 입학처 Q&A 항공관광학과 4,444,000"),
}

# BA_3 from task-1 transcript (중부~대구한의)
BA3 = {
 "중부대학교": (3539000,4107000,"중부대 2025 공시"),
 "호남대학교": (2969500,3445000,"호남대 2025 공시"),
 "남부대학교": (2919000,3541000,"남부대 2025 공시"),
 "예원예술대학교": (4252500,None,"예원예술대 2025 공시(예술 단일계열)"),
 "목포가톨릭대학교": (2824000,3418500,"목포가톨릭대 2025 공시"),
 "김천대학교": (3280500,3663000,"김천대 2025 공시"),
 "호원대학교": (3005000,3875000,"호원대 2025 공시"),
 "홍익대학교": (3619500,4827000,"홍익대 2025 공시(서울본교)"),
 "충남대학교": (1686500,2422000,"충남대 2025 공시(국공립→낮음)"),
 "대구한의대학교": (3036000,4027500,"대구한의대 2025 공시"),
}

def mk(mn,mx):
    return {"min":mn,"max":mx} if mx and mn else mn

for grp in [BA0,BA3]:
    for s,(mn,mx,note) in grp.items():
        if s in results: continue
        results[s] = {"school":s,"level":"BA","tuition":mk(mn,mx),"tuition_max":mx,
                      "source_url":"대학알리미/공식입학처","note":note+" (학기당)"}

json.dump(results, open(RESULTS,"w",encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"BA 수업료 최종: {len(results)}개 학교")
# check against BA gap list
need=json.load(open(r"C:\Users\USER\camnemi-crm\backend\_gap_BA_0.json",encoding="utf-8"))+json.load(open(r"C:\Users\USER\camnemi-crm\backend\_gap_BA_1.json",encoding="utf-8"))+json.load(open(r"C:\Users\USER\camnemi-crm\backend\_gap_BA_2.json",encoding="utf-8"))+json.load(open(r"C:\Users\USER\camnemi-crm\backend\_gap_BA_3.json",encoding="utf-8"))+json.load(open(r"C:\Users\USER\camnemi-crm\backend\_gap_BA_4.json",encoding="utf-8"))
missing=[x['school'] for x in need if x['school'] not in results and x['school'] not in ['대전가톨릭대학교']]
print(f"BA 갭 46개 중 결과 반영: {len([s for s in set(x['school'] for x in need) if s in results])}")
print("아직 없는(대전가톨릭 제외):", missing)
