#!/usr/bin/env python3
"""publish_kb.py — 정본(canonical) → KB 파일 업데이트.
① verified_kb.json : tuition_per_college_semester(계열별) · student_count · track · lang_req
② consulting_db.json: 프로그램별 tuition/tuition_max · scholarship · majors · track · period
백업 후 in-place 갱신.
"""
import json, os, re, shutil, math
from collections import Counter

BE = r'C:\Users\wisew\camnemi-crm\backend'
CANON = os.path.join(BE, 'canonical', 'schools.jsonl')
VKB = os.path.join(BE, 'verified_kb.json')
CDB = os.path.join(BE, 'consulting_db.json')


def norm(s):
    return re.sub(r'[^\uac00-\ud7a3A-Za-z0-9]', '', str(s or '')).lower()


def canon():
    return [json.loads(l) for l in open(CANON, encoding='utf-8') if l.strip()]


def match_key(names, target):
    tn = norm(target)
    for n in names:
        nn = norm(n)
        if nn == tn or (len(tn) > 3 and (tn in nn or nn in tn)):
            return n
    return None


def main():
    recs = canon()
    vkb = json.load(open(VKB, encoding='utf-8'))
    cdb = json.load(open(CDB, encoding='utf-8'))
    vk_schools = vkb.get('schools', {})
    cd_schools = cdb.get('schools', {})

    v_up = c_up = 0
    for r in recs:
        progs = r.get('programs') or {}
        # ---- verified_kb ----
        vk = match_key(vk_schools.keys(), r['school'])
        if vk:
            e = vk_schools[vk]
            # collect per-college tuition
            tp = {}
            for pk, d in progs.items():
                for c in (d.get('colleges') or []):
                    tv = c.get('tuition_krw')
                    cn = (c.get('college') or '').strip()
                    if tv and cn and cn not in tp:
                        tp[cn] = {'수업료합계': int(tv)}
            # merge with existing
            cur = e.get('tuition_per_college_semester') or {}
            if tp:
                for k, v in tp.items():
                    if k not in cur:
                        cur[k] = v
                e['tuition_per_college_semester'] = cur
                v_up += 1
            # program-level reqs
            for pk, d in progs.items():
                req = d.get('req') if isinstance(d.get('req'), dict) else {}
                if req.get('topik') and not e.get('topik_req'):
                    e['topik_req'] = req['topik']
                if req.get('ielts') and not e.get('ielts_req'):
                    e['ielts_req'] = req['ielts']
        # ---- consulting_db ----
        ck = match_key(cd_schools.keys(), r['school'])
        if ck:
            e = cd_schools[ck]
            for pk, d in progs.items():
                p = e.setdefault(pk if pk in ('ba', 'ma') else pk, {}) if isinstance(e, dict) else None
                # consult db uses keys: BA, MA, 어학연수, 전문학사 — map
                cmap = {'ba': 'BA', 'ma': 'MA', 'lang': '어학연수', 'junior': '전문학사'}
                key = cmap.get(pk)
                if not key or not isinstance(e, dict):
                    continue
                blk = e.setdefault(key, {})
                if not isinstance(blk, dict):
                    continue
                vals = [c.get('tuition_krw') for c in (d.get('colleges') or []) if c.get('tuition_krw')]
                if vals and not blk.get('tuition'):
                    blk['tuition'] = min(vals)
                    blk['tuition_max'] = max(vals)
                    c_up += 1
                depts = [x.get('major') for c in (d.get('colleges') or []) for x in (c.get('departments') or [])]
                if depts and not blk.get('majors'):
                    blk['majors'] = depts[:200]
                if d.get('period') and not blk.get('period'):
                    blk['period'] = d['period']
                req = d.get('req') if isinstance(d.get('req'), dict) else {}
                if req.get('topik') and not blk.get('topik'):
                    blk['topik'] = req['topik']
                if req.get('ielts') and not blk.get('ielts'):
                    blk['ielts'] = req['ielts']
                if (d.get('scholarships')) and not blk.get('scholarship'):
                    blk['scholarship'] = {'enroll': [s.get('criteria') or s.get('name') for s in d['scholarships']], 'existing': []}

    for f in (VKB, CDB):
        if not os.path.exists(f + '.bak'):
            shutil.copy(f, f + '.bak')
    json.dump(vkb, open(VKB, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    json.dump(cdb, open(CDB, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f"verified_kb updated: {v_up} schools | consulting_db updated: {c_up} program blocks")


if __name__ == '__main__':
    main()
