#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Shared English + USD output helpers for the Camnemi university advisor bot.

All student-facing output must be English, and tuition is shown in USD,
rounded UP to the nearest $100 (e.g. 2219 -> 2300).
"""
import json
import math
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))

# Exchange rate: 1 USD = 1,400 KRW (round number, matches 2219->2300 example).
# Adjust here if the rate drifts significantly.
USD_RATE_KRW = 1400.0


# --- currency ----------------------------------------------------------------
def krw_to_usd(krw):
    """Convert KRW -> USD, rounding UP to the nearest 100 USD."""
    if not krw:
        return None
    usd = float(krw) / USD_RATE_KRW
    return int(math.ceil(usd / 100.0)) * 100


def fmt_usd(krw):
    """'2219' -> '$2,300'."""
    u = krw_to_usd(krw)
    if u is None:
        return ""
    return f"${u:,}"


# --- name / major maps ---------------------------------------------------------
def _load_json(path):
    try:
        with open(os.path.join(BASE, path), encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


_EN_NAMES = _load_json("_en_names.json")      # ek (Korean) -> en (English)
_EN_MAJORS = _load_json("_en_majors.json")    # kr major -> en major
_LOGOS = _load_json("_logos.json")            # ek (Korean) -> logo path

LOGO_BASE = r"C:\Users\USER\camnemi-crm"      # relative logo paths resolve under this

# fallback translations for common majors missing from the data.js map
_MAJOR_FALLBACK = {
    "컴퓨터공학": "Computer Engineering",
    "컴퓨터공학부": "School of Computer Engineering",
    "컴퓨터공학과": "Department of Computer Engineering",
    "소프트웨어": "Software",
    "소프트웨어학과": "Department of Software",
    "소프트웨어학부": "School of Software",
    "인공지능": "Artificial Intelligence",
    "인공지능학과": "Department of Artificial Intelligence",
    "빅데이터": "Big Data",
    "빅데이터경영": "Big Data Management",
    "정보통신공학과": "Department of Information and Communication Engineering",
    "전자공학과": "Department of Electronic Engineering",
    "전기전자공학부": "School of Electrical and Electronic Engineering",
    "경영학과": "Department of Business Administration",
    "경영학부": "School of Business",
    "국제통상학부": "School of International Trade",
    "로봇학부": "School of Robotics",
    "반도체시스템공학부": "School of Semiconductor Systems Engineering",
    "AI융합학과": "Department of AI Convergence",
    "AI·빅데이터학과": "Department of AI and Big Data",
    "글로벌빅데이터AI학과": "Department of Global Big Data and AI",
    "데이터사이언스": "Data Science",
    "데이터정보학과": "Department of Data Information",
    "융합소프트웨어": "Convergence Software",
    "데이터사이언스학부": "School of Data Science",
    "AI융합학부": "School of AI Convergence",
    "글로벌미디어AI영상학과": "Department of Global Media, AI and Video",
    "글로벌철도학과": "Department of Global Railway",
    "글로벌호텔관광": "Global Hotel and Tourism",
}


def en_name(kr):
    """Korean university name -> English name.
    If the English mapping is a bare abbreviation (e.g. 'KNUG University'),
    show '한국어명 (EnglishName)' so students always recognize the school."""
    if not kr:
        return ""
    kr = kr.strip()
    en = _EN_NAMES.get(kr, kr)
    if en == kr:
        return kr
    # if English is an ambiguous abbreviation (2-4 letters + 'University'), keep Korean too
    if re.match(r"^[A-Z]{2,4}\s+University$", en):
        return f"{kr} ({en})"
    return en


def logo(kr):
    """Korean university name -> local logo path (relative, under camnemi-crm)."""
    if not kr:
        return ""
    return _LOGOS.get(kr.strip(), "")


def en_major(kr):
    """Korean major -> English major (fallback: fallback map, else Korean)."""
    if not kr:
        return ""
    kr = kr.strip()
    if kr == "전 학과" or kr == "전체학과" or kr == "전학과":
        return "All departments"
    # drop parenthetical notes like (영어트랙만) before lookup
    base = re.sub(r"\([^)]*\)", "", kr).strip()
    if base in _EN_MAJORS:
        return _EN_MAJORS[base]
    if base in _MAJOR_FALLBACK:
        return _MAJOR_FALLBACK[base]
    return kr


# --- region ---------------------------------------------------------------------
_REGION_EN = {
    "서울특별시": "Seoul",
    "서울": "Seoul",
    "경기도": "Gyeonggi",
    "경기": "Gyeonggi",
    "인천광역시": "Incheon",
    "인천": "Incheon",
    "부산광역시": "Busan",
    "부산": "Busan",
    "대구광역시": "Daegu",
    "대구": "Daegu",
    "대전광역시": "Daejeon",
    "대전": "Daejeon",
    "광주광역시": "Gwangju",
    "광주": "Gwangju",
    "울산광역시": "Ulsan",
    "울산": "Ulsan",
    "세종특별자치시": "Sejong",
    "세종": "Sejong",
    "강원도": "Gangwon",
    "강원": "Gangwon",
    "충청북도": "Chungbuk",
    "충북": "Chungbuk",
    "충청남도": "Chungnam",
    "충남": "Chungnam",
    "전라북도": "Jeonbuk",
    "전북특별자치도": "Jeonbuk",
    "전북": "Jeonbuk",
    "전라남도": "Jeonnam",
    "전남": "Jeonnam",
    "경상북도": "Gyeongbuk",
    "경북": "Gyeongbuk",
    "경상남도": "Gyeongnam",
    "경남": "Gyeongnam",
    "제주특별자치도": "Jeju",
    "제주": "Jeju",
}


def en_region(kr):
    if not kr:
        return ""
    kr = kr.strip()
    base = re.sub(r"\([^)]*\)", "", kr).strip()  # strip city suffix like (안동)
    out = _REGION_EN.get(base) or _REGION_EN.get(kr)
    if out:
        return out
    return kr


# --- scholarship translation ------------------------------------------------------
_SCH_PATTERNS = [
    (re.compile(r"TOPIK\s*(\d+)\s*급\s*[→]?\s*(?:등록금|수업료)의?\s*(\d+)%\s*[가-힣]*\s*(\d*)"),
     lambda m: f"TOPIK {m.group(1)} -> {m.group(2)}% tuition off"),
    (re.compile(r"IELTS\s*([\d.]+)[^\d]*→\s*(?:등록금|수업료)\s*(\d+)%"),
     lambda m: f"IELTS {m.group(1)} -> {m.group(2)}% tuition off"),
    (re.compile(r"TOEFL\s*(?:iBT)?\s*(\d+)"), lambda m: f"TOEFL iBT {m.group(1)}"),
]


def en_scholarship(kr):
    """Translate a scholarship line to compact English (best-effort).

    Preserves the meaningful tokens: scholarship name, TOPIK/IELTS/TOEFL levels,
    top-N% context, semester count (1학기/4년), 반액/전액 (half/full), and %.
    """
    if not kr:
        return ""
    if "대학별 확인 필요" in kr:
        return "Confirm with the university (usually GPA/language-based during study)"
    txt = kr
    # collapse parenthetical noise like (외 1단계), (외 8단계)
    txt = re.sub(r"\(외\s*\d*\s*단계\)", "", txt)
    txt = re.sub(r"\(기타\s*[^)]*\)", "", txt)

    # scholarship-name word swaps (Korean -> English) BEFORE stripping Hangul
    name_repl = [
        ("글로벌", "Global"), ("외국인", "Foreign-student"), ("유학생", "International"),
        ("입학", "admission"), ("신입", "new"), ("신입생", "freshman"),
        ("장학금", "scholarship"), ("장학", "scholarship"),
        ("성적우수", "high-GPA"), ("성적", "GPA"), ("우수", "merit"),
        ("언어능력", "language"), ("어학", "language"), ("영어", "English"),
        ("한국어", "Korean"), ("토픽", "TOPIK"),
        ("총장", "President"), ("학장", "Dean"), ("국제교류처장", "Intl-Exchange-Director"),
        ("재학", "current"), ("편입", "transfer"),
        ("감면", "off"), ("면제", "off"), ("지급", "granted"),
        ("1학기", "1 semester"), ("첫 학기", "1st semester"), ("첫 2학기", "first 2 semesters"),
        ("4년", "4 years"), ("전액", "full"), ("반액", "half"),
        ("상위", "top "), ("등록금", "tuition"), ("수업료", "tuition"),
    ]
    for a, b in name_repl:
        txt = txt.replace(a, b)

    # keep TOPIK/IELTS/TOEFL levels + numbers + arrows
    for pat, fn in _SCH_PATTERNS:
        txt = pat.sub(fn, txt)

    # drop remaining Korean, keep Latin + digits + arrows/·/~
    txt = re.sub(r"[가-힣]+", " ", txt)
    txt = re.sub(r"\(\s*\)", "", txt)
    txt = re.sub(r"\s*:\s*", ": ", txt)
    txt = re.sub(r"\s*→\s*", " → ", txt)
    txt = re.sub(r"\s*·\s*", " · ", txt)
    txt = re.sub(r"\(1 semester\)", "(1 sem)", txt)
    txt = re.sub(r"\s+", " ", txt).strip()
    txt = re.sub(r"^[:.\s\-]+", "", txt).strip()
    # cleanup: stray "scholarship( scholarship)" -> "scholarship", ") →" -> "→", "→ :" -> "→"
    txt = re.sub(r"scholarship\(\s*scholarship\s*\)", "scholarship", txt)
    txt = re.sub(r"scholarship\( scholarship\)", "scholarship", txt)
    txt = re.sub(r"\)\s*→", "→", txt)
    txt = re.sub(r"→\s*:", "→", txt)
    txt = re.sub(r"\(\s*\)", "", txt)
    txt = re.sub(r"\s+", " ", txt).strip()
    # clean dangling arrows/slashes at ends
    txt = re.sub(r"[→/]\s*$", "", txt).strip()
    return txt


def en_track(track):
    m = {"영어트랙": "English", "한국어트랙": "Korean", "영어": "English", "한국어": "Korean"}
    return m.get(track, track or "")


def en_lang(lang_req):
    """Translate a lang_req string to English (best-effort)."""
    if not lang_req:
        return ""
    t = str(lang_req)
    repl = [
        ("TOPIK 기반 (영어 불요)", "TOPIK-based (no English required)"),
        ("TOPIK 기반", "TOPIK-based"),
        ("한국어트랙", "Korean track"),
        ("영어트랙", "English track"),
        ("상위권", "top-tier"),
        ("대학별 확인 필요", "confirm with university"),
        ("한국어", "Korean"),
        ("영어", "English"),
    ]
    for a, b in repl:
        t = t.replace(a, b)
    return t


def parse_krw(s):
    """Parse a tuition string like '₩4,636,000~₩7,133,000' or '₩4,201,000'
    into (min_krw, max_krw). Returns (None, None) if unparseable.

    Handles annual->semester conversions: '연평균 ₩8,590,000/년 → 약 ₩4,295,000/학기'
    should give the SEMESTER value, not a reversed range.
    """
    if isinstance(s, (int, float)):
        return int(s), int(s)
    txt = str(s)
    nums = re.findall(r"[\d,]+", txt)
    nums = [int(n.replace(",", "")) for n in nums]
    if not nums:
        return None, None
    # annual->semester pattern: .../년 ... /학기 -> use the semester number
    if ("년" in txt or "/년" in txt) and ("학기" in txt):
        sem = [n for n in nums if n < 100000000]
        if "학기" in txt:
            # the number closest to the '학기' token
            idx = txt.rfind("학기")
            seg = txt[max(0, idx - 20):idx]
            seg_nums = [int(n.replace(",", "")) for n in re.findall(r"[\d,]+", seg)]
            if seg_nums:
                v = seg_nums[-1]
                return v, v
    # normal min~max range
    return nums[0], (nums[1] if len(nums) > 1 else nums[0])


def fmt_tuition_usd(krw_str):
    """'₩4,636,000~₩7,133,000' -> '$3,400~$5,100' (each rounded up to $100)."""
    lo, hi = parse_krw(krw_str)
    if lo is None:
        return ""
    lo_s = fmt_usd(lo)
    if hi and hi != lo:
        return f"{lo_s}~{fmt_usd(hi)}"
    return lo_s
