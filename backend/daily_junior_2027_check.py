#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Daily 2027 guide check for JUNIOR colleges (전문대학).
Adds junior colleges to the daily 2027 guide tracking, separate from 4-year univs.

Sources for each junior college's 2027 foreigner guide:
  1. adiga.kr univFileAjax (if we have the unvCd)
  2. The college's own international/ipsi page (checked via guide map)

Since adiga's collAjax only returns the first 15 via POST, we maintain a
school->unvCd map (from adiga when available) and fall back to the college
website. Outputs:
  _guide_2027_junior.json   per-junior status (2027 published vs 2026/unknown)
  _junior_pending.json      junior schools needing a browser check
"""
import json, os, re, datetime

BASE = r"C:\Users\USER\camnemi-crm\backend"
OUT = os.path.join(BASE, "_guide_2027_junior.json")
PENDING = os.path.join(BASE, "_junior_pending.json")

# Junior colleges with known adiga unvCd (from the collAjax first page + manual)
# format: school name -> adiga unvCd
KNOWN_UNVCD = {
    "가톨릭상지대학교": "0000410",
    "강동대학교": "0000433",
    "강릉영동대학교": "0000514",
    "강원관광대학교": "0000548",
    "강원도립대학교": "0002639",
    "거제대학교": "0000412",
    "경기과학기술대학교": "0000560",
    "경남도립거창대학": "0000402",
    "경남도립남해대학": "0000403",
    "경남정보대학교": "0002640",
    "경민대학교": "0000416",
    "경복대학교": "0002641",
    "경북과학대학교": "0000456",
    "경북보건대학교": "0000438",
    "경북전문대학교": "0002642",
    # additional known:
    "인하공업전문대학": "0002654",
}


def load_junior_schools():
    """Load the 126 junior colleges from verified_kb.json + unvCd map."""
    with open(os.path.join(BASE, "verified_kb.json"), encoding="utf-8") as f:
        kb = json.load(f)
    juniors = kb.get("junior", {}).get("schools", {})
    # load unvCd map if it exists (from adiga search-by-name)
    unvcd_map = {}
    map_path = os.path.join(BASE, "_junior_unvcd_map.json")
    if os.path.exists(map_path):
        try:
            with open(map_path, encoding="utf-8") as f:
                unvcd_map = json.load(f)
        except Exception:
            pass
    return {name: (unvcd_map.get(name, ""), info.get("region", "")) for name, info in juniors.items()}


def check_adiga(unvCd):
    """Check if a junior college has a 2027 foreigner guide on adiga (enabled = published)."""
    if not unvCd:
        return None
    import requests
    requests.packages.urllib3.disable_warnings()
    try:
        r = requests.post(
            "https://www.adiga.kr/ucp/uvt/uni/univFileAjax.do",
            data={"searchSyr": "2027", "unvCd": unvCd},
            headers={"User-Agent": "Mozilla/5.0"},
            verify=False, timeout=30,
        )
        html = r.text
        # find 외국인 모집요강 item; 'disabled' class means not yet published
        if "외국인" in html:
            # find the li containing 외국인 and check if it's disabled
            idx = html.find("외국인")
            # look backward for class
            li_start = html.rfind("<li", 0, idx)
            li_tag = html[li_start:idx] if li_start >= 0 else ""
            disabled = "disabled" in li_tag
            return "2027_not_yet" if disabled else "2027_published"
        return "no_foreigner_item"
    except Exception as e:
        return f"error:{e}"


def main():
    juniors = load_junior_schools()
    print(f"전문대학 {len(juniors)}개 로드")

    # load previous status if exists
    prev = {}
    if os.path.exists(OUT):
        with open(OUT, encoding="utf-8") as f:
            prev = json.load(f)

    result = {}
    pending = []
    today = datetime.date.today().isoformat()

    for name, (unvCd, region) in juniors.items():
        status = check_adiga(unvCd) if unvCd else "no_unvcd"
        result[name] = {
            "name": name,
            "region": region,
            "unvCd": unvCd,
            "status": status,
            "checked": today,
        }
        # if we can't confirm 2027 via adiga, mark pending for browser check
        if status not in ("2027_published", "2027_not_yet"):
            pending.append({"school": name, "unvCd": unvCd, "region": region})

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    with open(PENDING, "w", encoding="utf-8") as f:
        json.dump(pending, f, ensure_ascii=False, indent=2)

    # summary
    from collections import Counter
    st = Counter(v["status"] for v in result.values())
    print("상태 분포:", dict(st))
    print(f"브라우저 확인 필요: {len(pending)}개")
    print(f"저장: {OUT}")


if __name__ == "__main__":
    main()
