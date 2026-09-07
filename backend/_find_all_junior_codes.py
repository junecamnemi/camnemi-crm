#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Find ALL junior college unvCds via adiga search-by-name."""
import requests, re, json, time
requests.packages.urllib3.disable_warnings()
BASE = 'https://www.adiga.kr'
HEADERS = {'User-Agent': 'Mozilla/5.0', 'Accept-Language': 'ko-KR,ko;q=0.9'}

with open(r"C:\Users\USER\camnemi-crm\backend\verified_kb.json", encoding="utf-8") as f:
    kb = json.load(f)
juniors = list(kb["junior"]["schools"].keys())

# load existing known
with open(r"C:\Users\USER\camnemi-crm\backend\_guide_2027_junior.json", encoding="utf-8") as f:
    existing = json.load(f)
found = {name: v["unvCd"] for name, v in existing.items() if v["unvCd"]}
found["동양미래대학교"] = "0000463"
found["명지전문대학"] = "0000473"
found["배화여자대학교"] = "0000476"
found["삼육보건대학교"] = "0000483"
found["서울여자간호대학교"] = "0002973"
found["서울예술대학교"] = "0000489"
found["숭의여자대학교"] = "0000500"
found["한양여자대학교"] = "0000554"

def find_code(name):
    base = name.replace("대학교", "").replace("대학", "")
    # try progressively shorter names
    for probe in [name, base, base[:4], base[:3], base[:2]]:
        try:
            r = requests.post(f'{BASE}/ucp/uvt/col/collAjax.do',
                              data={'searchSyr': '2027', 'searchUnvNm': probe},
                              headers=HEADERS, verify=False, timeout=20)
            items = re.findall(r'code="(\d+)">([^<]+)</a>', r.text)
            for cd, nm in items:
                nm_clean = nm.replace("[본교]", "").strip()
                if name.replace("대학교","").replace("대학","")[:4] in nm_clean or nm_clean[:4] in name:
                    return cd
        except:
            pass
        time.sleep(0.3)
    return None

unknown = [n for n in juniors if n not in found]
print(f"미확인 {len(unknown)}개, 진행 중...")

for name in unknown:
    cd = find_code(name)
    if cd:
        found[name] = cd
        print(f"  ✓ {name} → {cd}")
    else:
        print(f"  ✗ {name} (못 찾음)")
    time.sleep(0.5)

print(f"\n총 발견: {len(found)} / {len(juniors)}")
with open(r"C:\Users\USER\camnemi-crm\backend\_junior_unvcd_map.json", "w", encoding="utf-8") as f:
    json.dump(found, f, ensure_ascii=False, indent=2)
print("저장: backend/_junior_unvcd_map.json")
