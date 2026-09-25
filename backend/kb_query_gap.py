#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""kb_query_gap.py — KB 자기개선 ① 쿼리갭 자동수집 로거.

추천/상담 흐름에서 결과가 없거나 약한 쿼리를 _kb_query_gaps.jsonl에 기록한다.
야간 크론이 이 로그를 읽어 수집/파싱 대상으로 전환한다.
"""
import json, os, datetime

GAP_LOG = r"C:\Users\wisew\camnemi-crm\backend\_kb_query_gaps.jsonl"

def log_gap(query=None, level=None, ielts=None, topik=None, major=None,
            result_count=0, note="", source="univ_recommend"):
    """쿼리 갭 기록. result_count가 0이거나 매우 적을 때 호출."""
    rec = {
        "ts": datetime.datetime.now().isoformat(timespec="seconds"),
        "query": query, "level": level, "ielts": ielts, "topik": topik,
        "major": major, "result_count": result_count, "note": note, "source": source,
    }
    try:
        with open(GAP_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        return True
    except Exception:
        return False

def read_gaps(limit=None):
    """읽기: 최근 갭 로그 (야간 크론용)."""
    if not os.path.exists(GAP_LOG):
        return []
    out = []
    with open(GAP_LOG, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line: continue
            try: out.append(json.loads(line))
            except: pass
    if limit: out = out[-limit:]
    return out

if __name__ == "__main__":
    import sys
    gaps = read_gaps()
    print(f"쿼리갭 로그: {len(gaps)}건")
    for g in gaps[-10:]:
        print(f"  [{g.get('ts','')}] {g.get('query')} | level={g.get('level')} major={g.get('major')} ielts={g.get('ielts')} -> {g.get('result_count')}건")
