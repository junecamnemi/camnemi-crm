#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Parse unparsed guide PDFs with DeepSeek V4-Pro.
Deduplication is school + level + guide-year, so a newly issued year can be parsed
without reprocessing same-year renamed copies. --only-downloaded narrows to the
recently acquired 2027 PDFs recorded in _guide_2027_detected.json.
"""
import os, re, json, sys, time, urllib.request, argparse
from pathlib import Path

BASE = os.path.dirname(os.path.abspath(__file__))
_DRIVE_ROOTS = [Path(r"G:/공유 드라이브/Hermes/Camnemi/02_Crawling_Sheet/University_Project"),
                Path.home() / "내 드라이브" / "02_Crawling_Sheet" / "University_Project"]
UP = str(next((p for p in _DRIVE_ROOTS if (p / "guides").is_dir()), _DRIVE_ROOTS[-1]))
sys.path.insert(0, BASE)
import pipeline_paths as _pp  # ONE data home (_pipeline_data/parsed)
PARSED = str(_pp.parsed_file())
MODEL = "deepseek/deepseek-v4-pro"

def _auth():
    home = os.path.expanduser("~")
    for p in [os.path.join(home, "AppData", "Local", "hermes", "shared", "nous_auth.json"),
              os.path.join(home, "AppData", "Local", "hermes", "auth.json")]:
        if not os.path.exists(p): continue
        d = json.load(open(p, encoding="utf-8"))
        if isinstance(d, dict) and d.get("access_token"):
            return d.get("inference_base_url") or "https://inference-api.nousresearch.com/v1", d["access_token"]
        n = (d.get("providers") or {}).get("nous") or {}
        if n.get("agent_key"):
            return n.get("inference_base_url") or "https://inference-api.nousresearch.com/v1", n["agent_key"]
    raise SystemExit("no auth")
BASE_URL, KEY = _auth()

PROMPT = """한국 대학 외국인 모집요강 텍스트에서 정보를 추출해 JSON만 출력하세요(설명·마크다운 금지):
{"school":"대학명(한글)", "program":"ba|ma|lang|junior", "year":"2026|2027|unknown",
 "period":"원서접수 기간(문자열)", "topik":TOPIK최소급수 숫자 또는 null, "ielts":IELTS최소 숫자 또는 null,
 "toefl":TOEFL최소 숫자 또는 null, "majors":["모집학과 전체 목록"],
 "tuition_note":"등록금 관련 한 줄 요약",
 "scholarships":[{"name":"장학금명", "condition":"지급조건(TOPIK/IELTS/성적 등)", "benefit":"혜택(수업료 %/금액/기간)"}]}

장학금 추출 규칙: 요강에 나온 모든 장학금 등급/조건/혜택을 배열로 추출. 없으면 [].
=== 모집요강 텍스트 ===
"""

def school_from(fname):
    m = re.search(r'([가-힣A-Za-z]+(?:대학교|대학|전문대학|교육원))', fname)
    return m.group(1) if m else fname

def _school_key(value):
    value = re.sub(r"\[.*?\]|\(.*?\)", "", str(value or ""))
    value = re.sub(r"[^가-힣A-Za-z0-9]", "", value)
    for suffix in ("대학원대학교", "대학교", "대학원", "대학", "전문대"):
        if value.endswith(suffix):
            value = value[:-len(suffix)]
            break
    return value

def list_unparsed(only_downloaded=False, current="2027"):
    """Select by school + level + year, not school alone, so a new-year guide is parsed."""
    parsed_keys = set()
    parsed_files = set()
    # Read ALL three parse stores. Reading only PARSED re-offered schools that were already
    # parsed via the OCR or real-guide path; they then failed as "텍스트부족" and burned a
    # model call each (2026-09-29).
    sources = [PARSED, str(_pp.path("parsed_ocr")), str(_pp.path("parsed_real"))]
    for src in sources:
        if not os.path.exists(src):
            continue
        for line in open(src, encoding="utf-8"):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
                prog = row.get("_prog_hint") or row.get("program")
                hint_year = str(row.get("_year_hint") or "")
                parsed_year = str(row.get("year") or "")
                school = _school_key(row.get("school"))
                if school and prog:
                    for year in {hint_year, parsed_year} - {"", "unknown", "None"}:
                        parsed_keys.add((school, prog, year))
                if row.get("_file"):
                    parsed_files.add((row.get("_file"), prog, hint_year or parsed_year))
            except Exception:
                continue

    downloaded_paths = set()
    if only_downloaded:
        state_path = str(_pp.state_file())
        if os.path.exists(state_path):
            try:
                state = json.load(open(state_path, encoding="utf-8"))
                downloaded_paths = {
                    os.path.normcase(os.path.abspath(v.get("saved", "")))
                    for v in state.values()
                    if v.get("downloaded") and v.get("saved")
                }
            except Exception:
                downloaded_paths = set()

    # Unusable guides (0 pages / blank content, see guide_library.py --validate) have no
    # text to parse: offering them wastes a model call and reports a misleading "텍스트부족".
    invalid = set()
    try:
        rep = _pp.REPORT_DIR / "_invalid_pdfs.json"
        if os.path.exists(str(rep)):
            invalid = {b.get("name", "") for b in
                       json.load(open(str(rep), encoding="utf-8")).get("unreadable", [])}
    except Exception:
        invalid = set()

    out = []
    # Current-year policy: only the current guide year (2027) is parsed. Older files that
    # linger in the active tree belong to _archive and must not consume model calls.
    for prog in ["ba", "ma", "junior", "lang"]:
        for year in [current]:
            folder = os.path.join(UP, "guides", prog, year)
            if not os.path.isdir(folder):
                continue
            for filename in os.listdir(folder):
                if not filename.lower().endswith(".pdf"):
                    continue
                if filename in invalid:
                    continue
                path = os.path.abspath(os.path.join(folder, filename))
                if only_downloaded and os.path.normcase(path) not in downloaded_paths:
                    continue
                if (filename, prog, year) in parsed_files:
                    continue
                school = school_from(filename)
                key = _school_key(school)
                if any(kprog == prog and kyear == year and
                       (key == old or (len(key) >= 3 and (key in old or old in key)))
                       for old, kprog, kyear in parsed_keys):
                    continue
                out.append((path, prog, year, school))
    return out

def extract_text(path):
    import pymupdf
    doc = pymupdf.open(path)
    t = "".join(doc[i].get_text() for i in range(min(len(doc), 12)))
    doc.close()
    return t

def repair_json(txt):
    """Close a JSON object cut off mid-array/mid-string (long major lists get truncated),
    dropping only the incomplete trailing token."""
    depth = []
    in_str = False
    esc = False
    last_safe = 0
    for i, ch in enumerate(txt):
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
                last_safe = i + 1
            continue
        if ch == '"':
            in_str = True
        elif ch in "{[":
            depth.append("}" if ch == "{" else "]")
            last_safe = i + 1
        elif ch in "}]":
            if depth:
                depth.pop()
            last_safe = i + 1
        elif ch in ",:" or ch.isalnum():
            last_safe = i + 1
    out = txt[:last_safe]
    if in_str:
        out += '"'
    out = out.rstrip().rstrip(",")
    return out + "".join(reversed(depth))

def safe_json(resp):
    """Model output is not always clean JSON: strip fences, take the outer object,
    and close braces lost to truncation."""
    if not resp:
        return None
    txt = re.sub(r"^\s*```(?:json)?|```\s*$", "", resp.strip(), flags=re.I)
    m = re.search(r"\{.*\}", txt, re.S)
    if not m:
        s = txt.find("{")
        if s == -1:
            return None
        txt = txt[s:]
    else:
        txt = m.group(0)
    for attempt in (txt, txt[:txt.rfind("}") + 1] if "}" in txt else txt):
        try:
            return json.loads(attempt)
        except Exception:
            continue
    try:
        d = json.loads(repair_json(txt))
        if isinstance(d, dict):
            d["_truncated"] = True   # audit flag: trailing token dropped during repair
            return d
    except Exception:
        pass
    return None

def call(text, retries=6, nudge="", prompt=None):
    import random
    for i in range(retries):
        try:
            body = {"model": MODEL, "messages": [{"role": "user", "content": (PROMPT if prompt is None else prompt) + text[:14000] + nudge}],
                    "max_tokens": 32000, "temperature": 0}
            req = urllib.request.Request(BASE_URL.rstrip("/") + "/chat/completions",
                                         data=json.dumps(body).encode(),
                                         headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=300) as r:
                d = json.loads(r.read())
            m = d["choices"][0]["message"]
            content = (m.get("content") or "").strip()
            if not content:
                # Reasoning-only response: the model burned the whole budget thinking and
                # never wrote the JSON (21.8k chars of reasoning, empty content, 2026-09-29).
                # Retry telling it not to reason; do NOT parse the reasoning as the answer.
                nudge = "\n\nReturn ONLY the JSON object. Do NOT reason. Do NOT explain. No markdown."
                continue
            return content
        except Exception as e:
            if i == retries - 1:
                raise
            # Gateway 429/5xx/timeouts under sustained load: back off with jitter and keep
            # trying (instant retries burned every attempt on 34 files, 2026-09-28;
            # 6 attempts with jitter cleared the same files later).
            code = getattr(e, "code", None)
            print(f"    RETRY {i+1}/{retries} {type(e).__name__}{f' {code}' if code else ''}", flush=True)
            time.sleep(min(10 * (2 ** i), 180) + random.uniform(0, 5))
            continue

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only-downloaded", action="store_true",
                    help="Process only PDFs marked downloaded in _guide_2027_detected.json")
    ap.add_argument("--limit", type=int, default=0, help="Process at most N files")
    ap.add_argument("--sleep", type=float, default=2.0, help="Seconds between model calls (rate-limit pacing)")
    ap.add_argument("--current", default="2027", help="Current guide year; older years are never parsed")
    args = ap.parse_args()
    items = list_unparsed(only_downloaded=args.only_downloaded, current=args.current)
    if args.limit:
        items = items[:args.limit]
    print(f"진짜 미파싱 대상: {len(items)}" + (" (신규 다운로드만)" if args.only_downloaded else ""))
    from collections import Counter
    print("레벨별:", Counter(p for _, p, _, _ in items))
    ok = 0
    with open(PARSED, "a", encoding="utf-8") as out:
        for idx, (path, prog, year, school) in enumerate(items):
            if idx and args.sleep:
                time.sleep(args.sleep)
            try:
                txt = extract_text(path)
                if len(txt.strip()) < 50:
                    print(f"  SKIP(텍스트부족): {os.path.basename(path)}")
                    continue
                resp = call(txt)
                d = safe_json(resp)
                if d is None:
                    resp2 = call(txt + "\n\nReturn ONLY one valid JSON object, no prose, no markdown.")
                    d = safe_json(resp2)
                if d is None:
                    print(f"  FAIL(no json): {os.path.basename(path)}")
                    continue
                d["_file"] = os.path.basename(path)
                d["_prog_hint"] = prog
                d["_year_hint"] = year
                out.write(json.dumps(d, ensure_ascii=False) + "\n")
                out.flush()
                ok += 1
                print(f"  OK: {school} [{prog}]")
            except Exception as e:
                print(f"  ERR: {os.path.basename(path)} {type(e).__name__}: {str(e)[:90]}")
    print(f"완료: {ok}/{len(items)} 파싱")

if __name__ == "__main__":
    main()