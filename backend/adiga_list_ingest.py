#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""adiga_list_ingest.py — adiga(대학알리미) 대학리스트 전수 수집.

모바일/데스크톱 collAjax·univAjax를 페이지네이션으로 순회해
4년제 + 전문대 전체 대학리스트(unvCd·한글명·본교/캠퍼스)를 수집.

핵심: 페이징 파라미터는 `pagination.currentPage` (nav JS fnSearch(page)가 내부에서 이걸 갱신).
각 페이지 15건 고정. 총: 4년제 220(N), 전문대 132.

출력: backend/_adiga_univ_list.json / _adiga_junior_list.json
"""
import requests, re, json, time, os

requests.packages.urllib3.disable_warnings()
B = os.path.dirname(os.path.abspath(__file__))
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0) Chrome/124.0",
           "Accept-Language": "ko-KR,ko;q=0.9"}
URL_UNIV = "https://www.adiga.kr/ucp/uvt/uni/univAjax.do"   # 4년제
URL_COLL = "https://www.adiga.kr/ucp/uvt/col/collAjax.do"   # 전문대

def fetch(url, page, searchSyr="2027"):
    for attempt in range(3):
        try:
            r = requests.post(url, data={"searchSyr": searchSyr,
                                         "pagination.currentPage": str(page)},
                              headers=HEADERS, verify=False, timeout=30)
            return r.text
        except Exception:
            time.sleep(1.5)
    return ""

def parse(h):
    # 둘 다 selectUniv anchor 사용
    return re.findall(r'class="selectUniv" code="(\d{7})">([^<]+)</a>', h)

def ingest(url, total_pages, label):
    all_pairs = {}
    for page in range(1, total_pages + 1):
        h = fetch(url, page)
        pairs = parse(h)
        if not pairs:
            print(f"  [{label}] page {page}: 0건 (중단)")
            break
        for cd, nm in pairs:
            # 본교/제2캠퍼스/분교 raw 유지, 중복(도:캠퍼스) 포함
            key = cd
            if key in all_pairs and all_pairs[key] == nm:
                continue
            all_pairs.setdefault(key, nm)
        print(f"  [{label}] page {page}: {len(pairs)}건 → 누적 {len(all_pairs)}")
        time.sleep(0.3)
    return all_pairs

if __name__ == "__main__":
    print("=== 4년제 (총 220, 페이지당 15 ≈ 15p) ===")
    univ = ingest(URL_UNIV, 16, "4년제")
    with open(os.path.join(B, "_adiga_univ_list.json"), "w", encoding="utf-8") as f:
        json.dump(univ, f, ensure_ascii=False, indent=1)
    print(f"4년제 저장: {len(univ)}개")

    print("\n=== 전문대 (총 132, 페이지당 15 ≈ 9p) ===")
    junior = ingest(URL_COLL, 10, "전문대")
    with open(os.path.join(B, "_adiga_junior_list.json"), "w", encoding="utf-8") as f:
        json.dump(junior, f, ensure_ascii=False, indent=1)
    print(f"전문대 저장: {len(junior)}개")