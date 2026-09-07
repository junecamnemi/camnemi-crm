# -*- coding: utf-8 -*-
"""Build batches for the 22 missing 4-year BA guides (excluding edu/seminary per user rule)."""
import json

# From gap analysis — schools in data.js without local BA guide, excluding
# education universities & seminaries (user rule: not recommended)
SCHOOLS = [
    "동의대학교", "홍익대학교", "서울과학기술대학교", "포항공과대학교", "한국기술교육대학교",
    "충북대학교", "국립공주대학교", "국립금오공과대학교", "호서대학교", "백석대학교",
    "신라대학교", "한라대학교", "한세대학교", "한신대학교", "광주여자대학교",
    "대구예술대학교", "송원대학교", "세한대학교", "위덕대학교", "경운대학교",
    "화성의과학대학교", "추계예술대학교", "총신대학교", "대전신학대학교", "호남신학대학교",
]

# Split into batches of 5
batches = [SCHOOLS[i:i+5] for i in range(0, len(SCHOOLS), 5)]
json.dump(batches, open(r'C:\Users\USER\camnemi-crm\backend\_ba_gap_batches.json', 'w', encoding='utf-8'), ensure_ascii=False)
for i, b in enumerate(batches):
    print(f'batch {i}: {b}')
