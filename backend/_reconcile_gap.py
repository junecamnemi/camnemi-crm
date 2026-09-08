# -*- coding: utf-8 -*-
"""Reconcile: convert _gap_fill_results.json to a dict and merge BA_1/BA_2 data
(recovered from transcripts). Output stays a dict keyed by school."""
import json, os

RESULTS = r"C:\Users\USER\camnemi-crm\backend\_gap_fill_results.json"

# load existing (could be list or dict)
raw = json.load(open(RESULTS, encoding="utf-8"))
if isinstance(raw, list):
    results = {}
    for item in raw:
        results[item["school"]] = item
elif isinstance(raw, dict):
    results = raw
else:
    results = {}

# BA_1 (from task-1 transcript)
BA1 = {
    "금강대학교": (3299000, None, "금강대 2025 공시"),
    "예수대학교": (3636500, None, "예수대 2025 공시"),
    "초당대학교": (3005500, 4064500, "초당대 2025 공시"),
    "가야대학교": (3180000, 3767000, "가야대 2025 공시"),
    "백석대학교": (3668500, 4729500, "백석대 2025 공시"),
    "포항공과대학교": (2807000, None, "POSTECH 2025 공시"),
    "한세대학교": (3764500, 4980000, "한세대 2025 공시"),
    "한신대학교": (3635500, 4339000, "한신대 2025 공시"),
    "제주대학교": (1622000, 2173500, "제주대 2025 공시(국립)"),
    "한국체육대학교": (1930000, None, "한국체육대 2025 공시(국립)"),
}
BA2 = {
    "광신대학교": (2812659, 3536000, "광신대 2024 공시"),
    "극동대학교": (3237408, 4119835, "극동대 2024 공시"),
    "대신대학교": (3191500, None, "대신대 2024 공시"),
    "서울기독대학교": (3774150, None, "서울기독대 2024 공시"),
    "동덕여자대학교": (3013000, 4473250, "동덕여대 2024 공시"),
    "동양대학교": (3655750, None, "동양대 2024 공시"),
    "성결대학교": (3231250, 4410167, "성결대 2024 공시"),
    "유원대학교": (3170098, 3960820, "유원대 2024 공시"),
    "울산대학교": (2891250, 5459000, "울산대 2024 공시"),
    "인천가톨릭대학교": (2723000, None, "인천가톨릭대 2024 공시"),
}

def mk(mn, mx):
    return {"min": mn, "max": mx} if mx else mn

for school, (mn, mx, note) in {**BA1, **BA2}.items():
    if school in results: continue
    results[school] = {"school": school, "level": "BA", "tuition": mk(mn, mx),
                       "tuition_max": mx, "source_url": "대학알리미 공시",
                       "note": note + " (학기당, 2024-25 대학정보공시 연간/2)"}

json.dump(results, open(RESULTS, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"재구성 완료: {len(results)}개 학교 (dict 형태)")
print("포함:", ", ".join(sorted(results.keys())))
