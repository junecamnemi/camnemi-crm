#!/usr/bin/env python3
"""enrich_canonical.py — 정본 보강:
① colleges[].tuition_krw 빈칸 → 대학알리미(계열 최빈값) / KB 계열별
② departments: 한국어트랙인데 topik 없음 → 프로그램 req.topik / KB
③ 영어트랙인데 ielts 없음 → 프로그램 req.ielts
④ programs[].req 없으면 KB lang_req에서 추출
canonical/schools.jsonl 을 in-place 갱신.
"""
import json, os, re, math
from collections import Counter

BE = r'C:\Users\wisew\camnemi-crm\backend'
CANON = os.path.join(BE, 'canonical', 'schools.jsonl')
ACAD = r'C:\Users\wisew\_tuition_acad.jsonl'
KB = os.path.join(BE, 'verified_kb.json')


def norm(s):
    return re.sub(r'[^\uac00-\ud7a3A-Za-z0-9]', '', str(s or '')).lower()


def load_lines(p):
    return [json.loads(l) for l in open(p, encoding='utf-8') if l.strip()]


def main():
    canon = load_lines(CANON)
    acad = {}
    for r in load_lines(ACAD):
        if r.get('n'):
            acad[norm(r['univ'])] = r
    kb = json.load(open(KB, encoding='utf-8')).get('schools', {})

    t_fill = t_kb = req_fill = 0
    for s in canon:
        nm = s['school']
        ac = acad.get(norm(nm))
        kb_rec = next((v for k, v in kb.items() if norm(k) == norm(nm)), None)
        for pk, d in (s.get('programs') or {}).items():
            req = d.get('req') if isinstance(d.get('req'), dict) else {}
            ptopik = req.get('topik') or d.get('topik')
            pielts = req.get('ielts') or d.get('ielts')
            kbt = (kb_rec or {}).get('topik_req') or (kb_rec or {}).get('topik')
            if not ptopik and kbt:
                ptopik = kbt
            cols = d.get('colleges') or []
            for c in cols:
                # ① tuition
                if not c.get('tuition_krw'):
                    vals = []
                    dept_names = [norm(x.get('major')) for x in (c.get('departments') or [])]
                    if ac and ac.get('rows'):
                        for row in ac['rows']:
                            if norm(row['mjr']) in dept_names:
                                vals.append(row['krw'])
                    if not vals and ac and ac.get('rows'):
                        vals = [r['krw'] for r in ac['rows'][:40]]
                    if vals:
                        c['tuition_krw'] = Counter(vals).most_common(1)[0][0]
                        t_fill += 1
                    elif kb_rec:
                        tp = kb_rec.get('tuition_per_college_semester') or {}
                        if isinstance(tp, dict):
                            for kk, vv in tp.items():
                                val = vv.get('합계') if isinstance(vv, dict) else vv
                                if isinstance(val, (int, float)) and val > 0 and \
                                   norm(kk) and (norm(kk) in norm(c.get('college')) or norm(c.get('college')) in norm(kk)):
                                    c['tuition_krw'] = int(val); t_kb += 1; break
                # ②③ dept reqs
                for dep in (c.get('departments') or []):
                    if dep.get('korean_track') and not dep.get('topik') and ptopik:
                        dep['topik'] = ptopik; req_fill += 1
                    if dep.get('english_track') and not dep.get('ielts') and pielts:
                        dep['ielts'] = pielts; req_fill += 1
                    if not dep.get('korean_track') and not dep.get('english_track') and ptopik:
                        dep['korean_track'] = True
                        if not dep.get('topik'):
                            dep['topik'] = ptopik; req_fill += 1
            if ptopik or pielts:
                d['req'] = {'topik': ptopik, 'ielts': pielts}
    with open(CANON, 'w', encoding='utf-8') as f:
        for s in canon:
            f.write(json.dumps(s, ensure_ascii=False) + '\n')
    print(f"tuition filled: {t_fill} (academyinfo) + {t_kb} (KB) | reqs filled: {req_fill}")


if __name__ == '__main__':
    main()
