#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_libparse_store_sync.py — _parse_library.jsonl → 병합 J4 스토어 동기화.

문제(2026-10-05 발견)
---------------------
`_parse_library_batch.py` 는 `backend/_parse_library.jsonl` 에 파싱 결과를 쓰는데,
`_merge_llm_into_kb.py` 의 J4 입력은 `_pipeline_data/parsed/guides_llm_parsed_library.jsonl`
이다. 이 둘을 잇는 코드가 없어서 **라이브러리 배치 파싱 결과가 KB에 영원히 반영되지
않았다** (J4 파일이 9/29 이후 스테일).

동작
----
두 스토어(스키마 동일)를 `(_file, school)` 키로 합쳐 J4 에 쓴다.
같은 키가 양쪽에 있으면 **비어있지 않은 필드가 더 많은 쪽**(더 신선한 파싱)을 남긴다.
J4 는 `run_guide_kb_pipeline.py` 꼬리 단계와 `_apply_new_lang_guides.py` 가 읽는다.

사용
----
    python _libparse_store_sync.py            # 병합 실행
    python _libparse_store_sync.py --check    # 병합 없이 개수만
"""
import argparse
import io
import json
import sys
from pathlib import Path

B = Path(__file__).resolve().parent
sys.path.insert(0, str(B))
import pipeline_paths as _pp                                     # noqa: E402

SRC = B / "_parse_library.jsonl"                                 # batch writer output
DST = Path(_pp.PARSED_DIR) / "guides_llm_parsed_library.jsonl"    # merge J4 input


def load(p):
    if not Path(p).exists():
        return []
    rows = []
    for line in io.open(p, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def key(r):
    return (str(r.get("_file") or ""), str(r.get("school") or ""))


def richness(r):
    return sum(1 for v in r.values() if v not in (None, "", [], {}, "unknown"))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="병합 없이 개수만 보고")
    args = ap.parse_args()

    dst_rows = load(DST)
    src_rows = load(SRC)
    print(f"src {SRC.name}: {len(src_rows)} rows")
    print(f"dst {DST.name}: {len(dst_rows)} rows")
    if args.check:
        return 0

    merged = {key(r): r for r in dst_rows}
    added = replaced = 0
    for r in src_rows:
        k = key(r)
        if k in merged:
            if richness(r) > richness(merged[k]):
                merged[k] = r
                replaced += 1
        else:
            merged[k] = r
            added += 1

    with io.open(DST, "w", encoding="utf-8", newline="") as fh:
        for r in merged.values():
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"merged -> {len(merged)} rows | added {added} | replaced {replaced}")
    print(f"wrote {DST}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())