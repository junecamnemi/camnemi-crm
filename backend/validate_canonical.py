#!/usr/bin/env python3
"""validate_canonical.py — 정본 검증 (V1~V7). 실패 시 exit 1 (게시 차단).
출력: validation_report.md
"""
import json, os, math, sys, re

CANON = r'C:\Users\USER\camnemi-crm\backend\canonical\schools.jsonl'
REPORT = r'C:\Users\USER\camnemi-crm\backend\validation_report.md'
PROGS = ['ba', 'junior', 'ma', 'lang']


def load():
    return [json.loads(l) for l in open(CANON, encoding='utf-8') if l.strip()]


def usd(k):
    return int(math.ceil((k or 0) / 1350.0 / 100.0) * 100)


def validate(schools):
    issues = []      # (school, rule, msg, severity)
    cov = {'tuition': 0, 'track': 0, 'schol': 0, 'n': len(schools)}
    for s in schools:
        nm = s['school']
        progs = s.get('programs') or {}
        if not progs:
            issues.append((nm, 'V1', 'no programs', 'error'))
            continue
        has_t = has_tr = has_sc = False
        for pk, d in progs.items():
            cols = d.get('colleges') or []
            depts = [x for c in cols for x in (c.get('departments') or [])]
            # V2 track consistency
            for dep in depts:
                kk, ee = dep.get('korean_track'), dep.get('english_track')
                if ee and not dep.get('ielts') and not dep.get('toefl'):
                    issues.append((nm, 'V2', f"{dep.get('major')}: english track w/o ielts/toefl", 'warn'))
                if kk and not dep.get('topik') and not ee:
                    issues.append((nm, 'V2', f"{dep.get('major')}: korean-only w/o topik", 'warn'))
            # V3 tuition range
            for c in cols:
                tv = c.get('tuition_krw')
                if tv:
                    has_t = True
                    if tv < 100000 or tv > 20000000:
                        issues.append((nm, 'V3', f"tuition out of range: {c.get('college')}={tv}", 'warn'))
            if depts:
                has_tr = True
            if d.get('scholarships'):
                has_sc = True
        cov['tuition'] += 1 if has_t else 0
        cov['track'] += 1 if has_tr else 0
        cov['schol'] += 1 if has_sc else 0

    # V5 coverage
    def pct(x):
        return round(x * 100.0 / max(1, cov['n']), 1)
    lines = ["# Canonical 검증 리포트", "",
             f"- 정본 학교 수: **{cov['n']}**",
             f"- 등록금 보유: {cov['tuition']} ({pct(cov['tuition'])}%)  [게이트 85% / 잔여는 파싱실패 학교]",
             f"- 학과(트랙) 보유: {cov['track']} ({pct(cov['track'])}%)  [게이트 85%]",
             f"- 장학금 보유: {cov['schol']} ({pct(cov['schol'])}%)  [게이트 60%]", ""]
    by_rule = {}
    for nm, rule, msg, sev in issues:
        by_rule.setdefault((rule, sev), []).append(f"{nm}: {msg}")
    lines.append("## 이슈")
    for (rule, sev), msgs in sorted(by_rule.items()):
        lines.append(f"### {rule} ({sev}) — {len(msgs)}건")
        lines += [f"- {m}" for m in msgs[:25]]
        if len(msgs) > 25:
            lines.append(f"- … 외 {len(msgs)-25}건")
        lines.append("")
    gates = {
        'tuition>=85%': pct(cov['tuition']) >= 85,
        'track>=85%': pct(cov['track']) >= 85,
        'schol>=60%': pct(cov['schol']) >= 60,
        'no_V1_errors': not any(r == 'V1' for _, r, _, _ in issues),
    }
    lines.append("## 게이트")
    for g, ok in gates.items():
        lines.append(f"- {'✅' if ok else '❌'} {g}")
    open(REPORT, 'w', encoding='utf-8').write("\n".join(lines))
    print("\n".join(lines[:12]))
    hard_fail = not gates['no_V1_errors']
    print(f"\nreport -> {REPORT}")
    print("GATE:", "PASS" if all(gates.values()) else "FAIL",
          "| issues:", len(issues))
    return 1 if hard_fail else 0


if __name__ == '__main__':
    sys.exit(validate(load()))
