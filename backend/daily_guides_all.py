#!/usr/bin/env python3
"""daily_guides_all.py — one daily pass over every admission-guide source.

Runs (in order) — all DIRECT school-URL collection (adiga NOT used):
  1. daily_guide_scraper.py          — BA/MA/lang direct collection (school guide_url)
  2. daily_homepage_2027_check.py    — school-homepage 2027 detection (BA/MA)
  3. daily_junior_direct.py          — junior-college direct collection (school URL)
  4. upsert_2027_guides.py           — push any NEW 2027 guides into Supabase

Prints a SHORT summary to stdout ONLY (safe for a no_agent cron: silent when
nothing changed is not possible for a status line, so we always print one line —
the cron delivers it daily so the user sees the check ran).

Run by the Hermes cron 'Camnemi 모집요강 데일리 체크' every day.
"""
import os, subprocess, sys, json, datetime

BASE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable
STEPS = [
    ("daily_guide_scraper.py", "BA/MA/어학 직접 수집 (학교 URL)"),
    ("daily_homepage_2027_check.py", "홈페이지 2027 탐지"),
    ("daily_junior_direct.py", "전문대 외국인 요강 직접 수집 (학교 URL)"),
    ("upsert_2027_guides.py", "Supabase 반영"),
]

def run(script, label):
    p = os.path.join(BASE, script)
    if not os.path.exists(p):
        return f"⚠️ {script} 없음"
    try:
        r = subprocess.run([PY, p], cwd=BASE, capture_output=True, text=True, timeout=1800)
        tail = (r.stdout or "").strip().splitlines()
        last = tail[-1][:80] if tail else ""
        if r.returncode != 0:
            err = (r.stderr or "").strip().splitlines()
            return f"❌ {script}: {(err[-1] if err else 'exit '+str(r.returncode))[:90]}"
        return f"✅ {label}"
    except subprocess.TimeoutExpired:
        return f"⏱ {script} timeout"
    except Exception as e:
        return f"❌ {script}: {e}"

def counts():
    """report how many 2027 guides we have per track, from the master report."""
    m = os.path.join(BASE, "_guide_2027_master.json")
    try:
        rows = json.load(open(m, encoding="utf-8"))
    except Exception:
        rows = []
    def n(t): return sum(1 for r in rows if str(r.get(f"{t}_status","")).startswith("2027"))
    junior_n = 0
    jf = os.path.join(BASE, "_guide_2027_junior.json")
    try:
        jrows = json.load(open(jf, encoding="utf-8"))
        junior_n = sum(1 for v in jrows.values() if str(v.get("status","")) == "2027_published")
        junior_total = len(jrows)
    except Exception:
        junior_total = 0
    if not rows and not junior_total:
        return ""
    return f"2027 확보 — 학부 {n('ba')} / 대학원 {n('ma')} / 어학 {n('lang')} / 전문대 {junior_n} (일반 {len(rows)}교 + 전문대 {junior_total}교)"

def main():
    today = datetime.date.today().isoformat()
    out = [f"📄 모집요강 데일리 체크 · {today}"]
    for s, l in STEPS:
        out.append("  " + run(s, l))
    c = counts()
    if c: out.append(c)
    print("\n".join(out))

if __name__ == "__main__":
    main()
