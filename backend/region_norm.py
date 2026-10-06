#!/usr/bin/env python3
"""region_norm.py — 지역(region/loc) 표기 단일 정본 (데이터 + 표시).

문제 (2026-10-06 운영자: "University DB에 지역이 영어/한글 혼용"):
  - DB(`universities.loc`, `verified_kb.region`, `consulting_db.region`)에 축약형(`경기`·`서울`),
    괄호 시군(`경기(안산)`), 공백 시군(`경북 경산시`), 구표기(`강원도`·`전라북도`)가 섞여 있었다(69종).
  - CRM UI(`index.html`)의 `LOC_EN` 사전은 정식명 18개만 알고, **사전에 없는 값은 한글로 그대로**
    노출했다(`locEn(l) => LOC_EN[l] || l`). 그래서 영어 화면에서 여러 값이 한글로 튀었다.

정책 (단일 정본):
  - **저장은 항상 한글 정식명**(예: `경기도`, `서울특별시`, `강원특별자치도`).
  - **표시는 `to_en()` 하나로만** 영어 라벨을 만든다(UI/시트/영문출력 공통).
  - 시·군 상세(`경기(안산)`, `경북 경산시`)는 **버리지 않고 detail 로 분리**해 보존하고,
    표시할 때는 영어(`Gyeonggi (Ansan)`)로 번역한다.
  - **영문 라벨에 한글이 남지 않는다**: 시·군 번역이 없으면 시·군을 빼고 시·도만 표시.

사용법:
    python region_norm.py --dry-run        # 변경 예정 집계(쓰기 없음)
    python region_norm.py --js             # index.html 주입용 JS 사전 출력
"""
import argparse
import json
import os
import re
from collections import Counter

# 시·도 정식명 (현행 공식 명칭) + 영문 라벨
CANONICAL = {
    "서울특별시": "Seoul",
    "부산광역시": "Busan",
    "대구광역시": "Daegu",
    "인천광역시": "Incheon",
    "광주광역시": "Gwangju",
    "대전광역시": "Daejeon",
    "울산광역시": "Ulsan",
    "세종특별자치시": "Sejong",
    "경기도": "Gyeonggi",
    "강원특별자치도": "Gangwon",
    "충청북도": "North Chungcheong",
    "충청남도": "South Chungcheong",
    "전북특별자치도": "Jeonbuk",
    "전라남도": "South Jeolla",
    "경상북도": "North Gyeongsang",
    "경상남도": "South Gyeongsang",
    "제주특별자치도": "Jeju",
}

# 별칭 → 정식명 (실측 69종 + 구표기)
ALIASES = {
    "서울": "서울특별시", "서울시": "서울특별시",
    "부산": "부산광역시", "부산시": "부산광역시",
    "대구": "대구광역시", "대구시": "대구광역시",
    "인천": "인천광역시", "인천시": "인천광역시",
    "광주": "광주광역시", "광주시": "광주광역시",
    "대전": "대전광역시", "대전시": "대전광역시",
    "울산": "울산광역시", "울산시": "울산광역시",
    "세종": "세종특별자치시", "세종시": "세종특별자치시",
    "경기": "경기도", "경기도": "경기도",
    "강원": "강원특별자치도", "강원도": "강원특별자치도", "강원특별자치도": "강원특별자치도",
    "충북": "충청북도", "충청북도": "충청북도",
    "충남": "충청남도", "충청남도": "충청남도",
    "전북": "전북특별자치도", "전라북도": "전북특별자치도", "전북특별자치도": "전북특별자치도",
    "전남": "전라남도", "전라남도": "전라남도",
    "경북": "경상북도", "경상북도": "경상북도",
    "경남": "경상남도", "경상남도": "경상남도",
    "제주": "제주특별자치도", "제주도": "제주특별자치도", "제주특별자치도": "제주특별자치도",
}

# 시·군·구 상세 → 영문 (실측 33종). 여기에 없으면 상세를 표시하지 않는다(한글 노출 방지).
CITY_EN = {
    "안산": "Ansan", "안산시": "Ansan", "안성": "Anseong", "평택": "Pyeongtaek", "안양": "Anyang",
    "남양주": "Namyangju", "포천": "Pocheon", "구리": "Guri", "용인": "Yongin", "수원": "Suwon",
    "성남": "Seongnam", "고양": "Goyang", "부천": "Bucheon", "화성": "Hwaseong", "오산": "Osan",
    "의정부": "Uijeongbu", "파주": "Paju", "김포": "Gimpo",
    "춘천": "Chuncheon", "원주": "Wonju", "강릉": "Gangneung", "속초": "Sokcho", "삼척": "Samcheok",
    "청주": "Cheongju", "충주": "Chungju", "제천": "Jecheon", "천안": "Cheonan", "아산": "Asan",
    "아산시": "Asan", "공주": "Gongju", "논산": "Nonsan", "금산": "Geumsan", "금산군": "Geumsan",
    "홍성": "Hongseong", "예산": "Yesan", "서산": "Seosan", "당진": "Dangjin",
    "전주": "Jeonju", "군산": "Gunsan", "익산": "Iksan", "정읍": "Jeongeup", "남원": "Namwon",
    "목포": "Mokpo", "여수": "Yeosu", "순천": "Suncheon", "나주": "Naju", "광양": "Gwangyang",
    "무안": "Muan",
    "포항": "Pohang", "경주": "Gyeongju", "구미": "Gumi", "경산": "Gyeongsan", "경산시": "Gyeongsan",
    "안동": "Andong", "김천": "Gimcheon", "영주": "Yeongju", "상주": "Sangju", "문경": "Mungyeong",
    "칠곡": "Chilgok", "의성": "Uiseong", "영덕": "Yeongdeok",
    "창원": "Changwon", "진주": "Jinju", "김해": "Gimhae", "양산": "Yangsan", "거제": "Geoje",
    "통영": "Tongyeong", "밀양": "Miryang", "사천": "Sacheon",
    "제주시": "Jeju City", "서귀포": "Seogwipo",
    "광진구": "Gwangjin-gu", "구로구": "Guro-gu", "동대문구": "Dongdaemun-gu",
    "성북구": "Seongbuk-gu", "북구": "Buk-gu", "부산진구": "Busanjin-gu", "사상구": "Sasang-gu",
    "서울": "Seoul", "부산": "Busan", "대구": "Daegu", "인천": "Incheon", "대전": "Daejeon",
    "본교": "Main campus", "서울캠퍼스": "Seoul campus", "부산캠퍼스": "Busan campus",
    "제2캠퍼스": "2nd campus", "글로벌캠퍼스": "Global campus",
}

# 긴 접두어부터 매칭해야 '경기'가 '경상'보다 먼저 잡히지 않는다. 정식명도 키로 포함(→ 자기 자신).
_MAP = dict(ALIASES)
for _k in CANONICAL:
    _MAP.setdefault(_k, _k)
_PREFIXES = sorted(_MAP, key=len, reverse=True)


def split_detail(v):
    """'경기(안산)' / '충남 금산군 (본교)' → (괄호 앞 지역부, 괄호 안 상세)."""
    s = str(v or "").strip()
    if not s:
        return "", ""
    m = re.match(r"^([^()\[\],/]*?)\s*[\(\[]([^)\]]*)[\)\]]\s*$", s)   # 지역(상세)
    if m:
        return m.group(1).strip(), m.group(2).strip()
    return s, ""


def normalize(value):
    """지역 원문 → (정식명, 상세). 정식명을 못 찾으면 (원문, '') 그대로 반환(창작 금지)."""
    head, detail = split_detail(value)
    if not head:
        return "", detail
    if head in _MAP:                                   # 1) 정확히 일치
        return _MAP[head], detail
    for p in _PREFIXES:                                # 2) '경기 안산시'처럼 지역부가 접두어
        if head == p:
            return _MAP[p], detail
        if head.startswith(p) and len(head) > len(p):
            rest = head[len(p):].strip(" ,/-")
            return _MAP[p], " ".join(x for x in (rest, detail) if x)   # 둘 다 보존
    return head, detail


def translate_detail(detail):
    """시·군 상세 → 영문. 하나라도 번역 불가면 ''(빈값) — 영문 라벨에 한글이 남지 않게."""
    if not detail:
        return ""
    toks = [t.strip() for t in re.split(r"[/,·\s]+", detail) if t.strip()]
    out = []
    for t in toks:
        en = CITY_EN.get(t)
        if not en:
            return ""
        out.append(en)
    seen, uniq = set(), []
    for t in out:
        if t not in seen:
            seen.add(t)
            uniq.append(t)
    return " / ".join(uniq)          # ASCII 구분자(한글 판정 혼동 방지)


_HANGUL = re.compile(r"[가-힣]")

# 짧은 영문 라벨 — 봇/시트/영문출력이 기존에 쓰던 표기(Gyeongnam 등)를 유지하기 위한 것.
SHORT_EN = {
    "서울특별시": "Seoul", "부산광역시": "Busan", "대구광역시": "Daegu", "인천광역시": "Incheon",
    "광주광역시": "Gwangju", "대전광역시": "Daejeon", "울산광역시": "Ulsan", "세종특별자치시": "Sejong",
    "경기도": "Gyeonggi", "강원특별자치도": "Gangwon", "충청북도": "Chungbuk",
    "충청남도": "Chungnam", "전북특별자치도": "Jeonbuk", "전라남도": "Jeonnam",
    "경상북도": "Gyeongbuk", "경상남도": "Gyeongnam", "제주특별자치도": "Jeju",
}


def to_en_short(value):
    """봇/시트용 짧은 영문 라벨(시·군 생략). 한글은 절대 남기지 않는다."""
    s = str(value or "").strip()
    if not s:
        return ""
    kr = canonical_kr(s)
    en = SHORT_EN.get(kr)
    if en:
        return en
    return s if not _HANGUL.search(s) else ""


# 약칭(한글) — 필터 매칭용. 예: 경기도 → 경기
SHORT_KR = {
    "서울특별시": "서울", "부산광역시": "부산", "대구광역시": "대구", "인천광역시": "인천",
    "광주광역시": "광주", "대전광역시": "대전", "울산광역시": "울산", "세종특별자치시": "세종",
    "경기도": "경기", "강원특별자치도": "강원", "충청북도": "충북", "충청남도": "충남",
    "전북특별자치도": "전북", "전라남도": "전남", "경상북도": "경북", "경상남도": "경남",
    "제주특별자치도": "제주",
}


def canonical_or_none(value):
    """빈값/None 은 그대로 유지(파이프라인의 coalesce 보존), 값이 있으면 정식명."""
    if value is None or not str(value).strip():
        return value
    return canonical_kr(value)


def to_en(value):
    """표시용 영문 라벨. 한글이 남지 않도록 보장: 미해석 값은 ASCII일 때만 그대로."""
    s = str(value or "").strip()
    if not s:
        return ""
    kr, detail = normalize(s)
    en = CANONICAL.get(kr)
    if not en:
        return s if not _HANGUL.search(s) else ""
    d = translate_detail(detail)
    if d and _HANGUL.search(d):
        d = ""
    return f"{en} ({d})" if d else en


def is_canonical(value):
    kr, detail = normalize(value)
    return kr in CANONICAL and not detail and str(value).strip() == kr


def canonical_kr(value):
    """저장용 정식명 — 미해석 값은 원문 유지(창작 금지)."""
    return normalize(value)[0]


def js_map():
    """index.html 주입용 JS 사전(단일 정본에서 생성) — 별칭 + 정식명 전부 커버."""
    m = dict(ALIASES)
    for k, v in CANONICAL.items():
        m.setdefault(k, v)
    return json.dumps(m, ensure_ascii=False, sort_keys=True)


def js_block():
    """index.html 에 들어갈 지역 i18n 블록(단일 정본에서 생성).

    LOC_EN: 한글(별칭 포함) → 영문,  CITY_EN: 시·군 → 영문,
    locEn(l, d): 시·도 라벨 + (있으면) 시·군. 한글이 화면에 남지 않는다.
    """
    m = {k: CANONICAL.get(v, v) for k, v in ALIASES.items()}
    for k, v in CANONICAL.items():
        m[k] = v
    loc = json.dumps(m, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    city = json.dumps(CITY_EN, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return (
        "const LOC_EN = " + loc + ";\n"
        "  const CITY_EN = " + city + ";\n"
        "  function locEn(l, d){ const b = LOC_EN[l] || (l && /[\\uac00-\\ud7a3]/.test(l) ? '' : (l || ''));"
        " const t = d ? (CITY_EN[d] || '') : ''; return t ? (b ? b + ' (' + t + ')' : t) : b; }\n"
    )


# ---------------------------------------------------------------- dry-run
def walk_regions(obj, path, out, key_re, depth=0):
    if depth > 8:
        return
    if isinstance(obj, dict):
        for k, v in obj.items():
            if key_re.search(str(k)) and isinstance(v, str):
                out.append((path + "." + str(k), v))
            elif isinstance(v, (dict, list)):
                walk_regions(v, path + "." + str(k), out, key_re, depth + 1)
    elif isinstance(obj, list):
        for i, it in enumerate(obj):
            walk_regions(it, f"{path}[{i}]", out, key_re, depth + 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--js", action="store_true")
    a = ap.parse_args()
    if a.js:
        print(js_map())
        return
    base = r"D:\Hermes\camnemi-crm"
    key_re = re.compile(r"^(region|loc)$", re.I)
    for f in ("backend/consulting_db.json", "backend/verified_kb.json"):
        p = os.path.join(base, f)
        if not os.path.exists(p):
            continue
        hits = []
        walk_regions(json.load(open(p, encoding="utf-8")), "", hits, key_re)
        ch = [(v, normalize(v)) for _, v in hits if not is_canonical(v)]
        print(f"\n=== {os.path.basename(f)}: 지역 필드 {len(hits)}건 중 변경 대상 {len(ch)}건 ===")
        for (v, (kr, det)), n in Counter(ch).most_common(12):
            print(f"    {n:4d}  {v!r:26s} → {kr!r}" + (f"  (detail={det!r})" if det else ""))
    djs = os.path.join(base, "data.js")
    if os.path.exists(djs):
        s = open(djs, encoding="utf-8", errors="replace").read()
        vals = re.findall(r'"loc"\s*:\s*"([^"]{1,40})"', s)
        ch = [v for v in vals if not is_canonical(v)]
        print(f"\n=== data.js: loc {len(vals)}건 중 변경 대상 {len(ch)}건 ===")
        print("    " + ", ".join(f"{v}({n})" for v, n in Counter(ch).most_common(12)))
    print("\n[표시 검증] 영문 라벨에 한글이 남는가:")
    for v in ("경기", "서울", "경기(안산)", "경남(창원)", "경북 경산시", "강원(강릉)",
              "서울 동대문구 (서울캠퍼스)", "충남 금산군 (본교)", "경기도 (남양주/서울/포천)",
              "경남 양산/부산", "울산광역시", "부산광역시 (부산진구)"):
        lab = to_en(v)
        print(f"    {v!r:30s} → {lab!r:34s} {'OK' if lab.isascii() else '!! 한글 잔존'}")


if __name__ == "__main__":
    main()