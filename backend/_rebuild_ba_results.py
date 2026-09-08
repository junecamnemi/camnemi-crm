# -*- coding: utf-8 -*-
"""Rebuild BA tuition results from ALL batch transcripts (BA_0..BA_4) into a single
school-keyed dict, level=BA. Fixes concurrency data loss. Separate per-school file."""
import json, os

RESULTS = r"C:\Users\USER\camnemi-crm\backend\_ba_tuition_results.json"

# BA_0 (from _gap_fill_results current state)
cur = json.load(open(r"C:\Users\USER\camnemi-crm\backend\_gap_fill_results.json", encoding="utf-8"))
results = {}
for k, v in cur.items():
    if v.get("level") == "BA":
        results[k] = v

# BA_1 (transcript values) - min,max,note
BA1 = {
 "금강대학교": (3299000,None,"금강대 2025 공시"),
 "예수대학교": (3636500,None,"예수대 2025 공시"),
 "초당대학교": (3005500,4064500,"초당대 2025 공시"),
 "가야대학교": (3180000,3767000,"가야대 2025 공시"),
 "백석대학교": (3668500,4729500,"백석대 2025 공시"),
 "포항공과대학교": (2807000,None,"POSTECH 2025 공시"),
 "한세대학교": (3764500,4980000,"한세대 2025 공시"),
 "한신대학교": (3635500,4339000,"한신대 2025 공시"),
 "제주대학교": (1622000,2173500,"제주대 2025 공시(국립)"),
 "한국체육대학교": (1930000,None,"한국체육대 2025 공시(국립)"),
}
# BA_2 (transcript)
BA2 = {
 "광신대학교": (2812659,3536000,"광신대 2024 공시"),
 "극동대학교": (3237408,4119835,"극동대 2024 공시"),
 "대신대학교": (3191500,None,"대신대 2024 공시"),
 "서울기독대학교": (3774150,None,"서울기독대 2024 공시"),
 "동덕여자대학교": (3013000,4473250,"동덕여대 2024 공시"),
 "동양대학교": (3655750,None,"동양대 2024 공시"),
 "성결대학교": (3231250,4410167,"성결대 2024 공시"),
 "유원대학교": (3170098,3960820,"유원대 2024 공시"),
 "울산대학교": (2891250,5459000,"울산대 2024 공시"),
 "인천가톨릭대학교": (2723000,None,"인천가톨릭대 2024 공시"),
}
# BA_3 (transcript)
BA3 = {
 "중부대학교": (3539000,4107000,"중부대 2025 공시"),
 "호남대학교": (2969500,3445000,"호남대 2025 공시"),
 "남부대학교": (2919000,3541000,"남부대 2025 공시"),
 "예원예술대학교": (4252500,None,"예원예술대 2025 공시(예술 단일)"),
 "목포가톨릭대학교": (2824000,3418500,"목포가톨릭대 2025 공시"),
 "김천대학교": (3280500,3663000,"김천대 2025 공시"),
 "호원대학교": (3005000,3875000,"호원대 2025 공시"),
 "홍익대학교": (3619500,4827000,"홍익대 2025 공시(서울본교)"),
 "충남대학교": (1686500,2422000,"충남대 2025 공시(국공립)"),
 "대구한의대학교": (3036000,4027500,"대구한의대 2025 공시"),
}
# BA_0 missing from current file? check
BA0_missing = ["경동대학교","강서대학교","나사렛대학교","대전가톨릭대학교","대전대학교","대진대학교","루터대학교","청주대학교","칼빈대학교","한서대학교"]
print("BA_0 현재 파일에 있음:", [s for s in BA0_missing if s in results])

def mk(mn,mx):
    return {"min":mn,"max":mx} if mx else mn
for grp in [BA1,BA2,BA3]:
    for s,(mn,mx,note) in grp.items():
        if s in results: continue
        results[s] = {"school":s,"level":"BA","tuition":mk(mn,mx),"tuition_max":mx,
                      "source_url":"대학알리미/KEDI 공시","note":note+" (학기당, 공시 연간/2)"}

json.dump(results, open(RESULTS,"w",encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"\nBA 수업료 결과 재구성: {len(results)}개 학교")
print("레벨 키 확인:", set(v['level'] for v in results.values()))
