#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_kb_gap_autofill.py — KB 자가감사 갭필러 '자동 실행' (자기개선 ②).

kb_gap_audit.py 로 갭을 재고, 조치가능(collect/reparse) 슬롯의 요강을
자동으로  파싱 → 병합 → 동기화  한다. 사람이 제안만 받고 끝나는 대신
스스로 갭을 소화하는 것이 목적이다.

왜 필요한가
-----------
04:00 파이프라인은 `parse_unparsed_pro.py` 로 "school+level+year 기준 미파싱"만
파싱한다. 그래서 같은 슬롯에 더 나은 파일(라이브러리 백로그)이 있어도
이미 파싱된 슬롯으로 보여 영원히 파싱되지 않는다.
`_parse_library_batch.py --inventory` 는 파일 단위로 세므로 그 백로그를 본다.
이 스크립트는 그 백로그를 소화하고, 파싱이 실제로 KB에 반영되도록
병합·동기화까지 수행한다.

사용
----
    python _kb_gap_autofill.py                 # 전체: 감사 → 파싱 → 병합 → 동기화 → 재감사
    python _kb_gap_autofill.py --dry-run       # 감사만 (무엇을 할지 보고)
    python _kb_gap_autofill.py --no-parse      # 병합·동기화만 (이미 파싱된 백로그 소화)

종료코드
--------
0 = 정상(갭이 줄었든 안 줄었든 실행 완료), 9 = 공유락 점유로 skip(04:00 런 진행 중).
"""
import argparse
import json
import os
import re
import subprocess
import sys
import datetime
from pathlib import Path

B = Path(__file__).resolve().parent
sys.path.insert(0, str(B))
PY = sys.executable
TODAY = datetime.date.today().isoformat()


def log(msg: str) -> None:
    print(msg, flush=True)


def run(step: str, argv, timeout=21600, fatal=True):
    log(f"\n--- {step} ---")
    log("$ " + " ".join(str(a) for a in argv))
    try:
        p = subprocess.run([str(a) for a in argv], cwd=str(B), capture_output=True,
                           text=True, encoding="utf-8", errors="replace", timeout=timeout)
    except subprocess.TimeoutExpired:
        log(f"TIMEOUT after {timeout}s")
        if fatal:
            raise SystemExit(1)
        return ""
    out = (p.stdout or "") + (p.stderr or "")
    tail = "\n".join(out.strip().splitlines()[-15:])
    log(tail if tail else "(no output)")
    if p.returncode != 0 and fatal:
        log(f"STEP FAILED rc={p.returncode}: {step}")
        raise SystemExit(1)
    return out


def audit_summary():
    """kb_gap_audit.py 를 돌리고 (총갭, 조치가능, action별, level별) 을 읽는다."""
    run("KB 갭 감사", [PY, B / "kb_gap_audit.py"], timeout=600)
    try:
        rep = json.load(open(B / "_pipeline_data" / "reports" / "_kb_gap_report.json", encoding="utf-8"))
        s = rep.get("summary", {})
        return len(rep.get("gaps", [])), s.get("actionable", 0), s.get("by_action", {}), s.get("by_level", {})
    except Exception as exc:                                    # noqa: BLE001
        log(f"report read failed: {exc}")
        return 0, 0, {}, {}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true", help="감사만 (수집/파싱/병합 안 함)")
    ap.add_argument("--no-parse", action="store_true", help="파싱은 건너뛰고 병합·동기화만")
    ap.add_argument("--workers", type=int, default=3)
    args = ap.parse_args()

    log(f"=== KB 갭 자동필 (auto) | {TODAY} ===")

    total0, act0, byact0, bylev0 = audit_summary()
    log(f"\n[before] 총 갭 {total0}교 | 조치가능 {act0}교")
    log(f"         action={byact0}")
    log(f"         level={bylev0}")

    if args.dry_run:
        log("\n--dry-run: 파싱/병합/동기화 생략")
        return 0

    if act0 == 0:
        log("\n조치가능 갭 없음 — 종료")
        return 0

    # 공유락: 04:00 야간 런과 같은 아티팩트(verified_kb/consulting_db/data.js)를 쓴다.
    # 런이 진행 중이면 기다리지 않고 skip(exit 9) — 야간 런이 이미 같은 일을 한다.
    try:
        import univ_data_lock as lock
        if not lock.acquire(wait_minutes=0):
            log("\n공유락 점유(04:00 야간 런 진행 중) — 이번 회차 skip")
            return 9
        locked = True
    except Exception as exc:                                    # noqa: BLE001
        log(f"lock 모듈 사용 불가({exc}) — 락 없이 진행")
        locked = False

    try:
        if not args.no_parse:
            run("라이브러리 백로그 파싱 (파일 단위 미파싱분, DeepSeek Pro)",
                [PY, B / "_parse_library_batch.py", "--run", "--workers", args.workers],
                timeout=21600, fatal=False)
            # ⚠️ 배치는 backend/_parse_library.jsonl 에 쓰는데 병합 J4 는
            #    _pipeline_data/parsed/guides_llm_parsed_library.jsonl 을 읽는다.
            #    이 연결이 없으면 파싱 결과가 KB에 영원히 반영되지 않는다(2026-10-05 발견).
            run("파싱 스토어 연결 (_parse_library.jsonl → 병합 J4)",
                [PY, B / "_libparse_store_sync.py"], timeout=600, fatal=False)

        run("KB 병합 (fill-only + 연도 승격)",
            [PY, B / "_merge_llm_into_kb.py", "--write", "--upgrade-years"], timeout=3600, fatal=False)
        run("3계층 동기화 (KB → consulting_db → data.js)",
            [PY, B / "sync_3layer.py"], timeout=3600, fatal=False)
        run("커버리지 가드", [PY, B / "coverage_guard.py"], timeout=900, fatal=False)

        total1, act1, byact1, bylev1 = audit_summary()
        log(f"\n[after] 총 갭 {total1}교 | 조치가능 {act1}교")
        log(f"        action={byact1}")
        log(f"        level={bylev1}")
        log(f"\n=== 자동필 완료 | 조치가능 {act0} → {act1} ===")
    finally:
        if locked:
            try:
                lock.release()
            except Exception:                                   # noqa: BLE001
                pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())