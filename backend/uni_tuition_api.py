#!/usr/bin/env python3
"""uni_tuition_api.py — fetch official 2026 tuition (등록금) from 대학알리미 (academyinfo.go.kr).

Flow (discovered from the mobile site):
  1. search      : /search/search.do?kwd=<name>&category=SCHL  -> schlId
  2. departments : /pubinfo/pubinfo1600/doInit.do?schlId=..     -> form fields
                   POST /pubinfo/pubinfo1600/selectMjrList.do   -> [{schl_mjr_id,mjr_id,mjr_nm,srs_lclft_nm}]
  3. tuition     : POST /pubinfo/pubinfo0081/selectFreshStudentRate.do  flag=v8 -> [{year,val}]

Usage: python uni_tuition_api.py "한양대학교" ["인하대학교" ...]
"""
import subprocess, re, json, sys, html as H, time, urllib.parse
UA = 'Mozilla/5.0 (Linux; Android 12) Chrome/120 Mobile'

def curl(args):
    try:
        return subprocess.run(['curl','-s','-L','-A',UA,'--max-time','30']+args,
                              capture_output=True, timeout=45).stdout.decode('utf-8','ignore')
    except Exception:
        return ''

def get(u): return curl([u])

def post(url, data, ref):
    a = ['-X','POST',url,'-H','X-Requested-With: XMLHttpRequest','-H','Referer: '+ref]
    for k, v in data.items(): a += ['--data-urlencode', f'{k}={v}']
    return curl(a)

def form_fields(h):
    d = {}
    for m in re.finditer(r'<input[^>]*>', h):
        s = m.group(0); n = re.search(r'name="([^"]+)"', s); v = re.search(r'value="([^"]*)"', s)
        if n: d[n.group(1)] = H.unescape(v.group(1)) if v else ''
    return d

def find_schlid(name):
    h = get('https://m.academyinfo.go.kr/search/search.do?kwd=' + urllib.parse.quote(name) + '&category=SCHL&pageNum=1&pageSize=10')
    ids = re.findall(r"fn_moveSchlDetail\('(\d+)'\)", h)
    return list(dict.fromkeys(ids))

def depts(sid):
    ref = f'https://m.academyinfo.go.kr/pubinfo/pubinfo1600/doInit.do?schlId={sid}'
    h = get(ref); f = form_fields(h)
    out = post('https://m.academyinfo.go.kr/pubinfo/pubinfo1600/selectMjrList.do', f, ref)
    try: rl = json.loads(out).get('resultList', [])
    except Exception: rl = []
    return ref, [(d.get('schl_mjr_id'), d.get('mjr_id'), d.get('mjr_nm'),
                  d.get('srs_lclft_nm'), d.get('dght_div_nm')) for d in rl]

def v8(sid, smid, mid, name, ref):
    d = {'svyYr':'2026','schlMjrId':smid,'schlId':sid,'mjrId':mid,'flag':'v8','tabSelect':'d1',
         'schlMjrIdSe':smid,'schlIdSe':sid,'mjrIdSe':mid,'mjrIdDt':'','mjrNm':name,'schNm':''}
    out = post('https://m.academyinfo.go.kr/pubinfo/pubinfo0081/selectFreshStudentRate.do', d, ref)
    try:
        for r in json.loads(out).get('resultList', []):
            if r.get('year') == '2026': return r.get('val')
    except Exception: pass
    return None

def one(name):
    ids = find_schlid(name)
    if not ids: return {'univ': name, 'error': 'no schlId'}
    sid = ids[0]
    ref, ds = depts(sid)
    if not ds: return {'univ': name, 'schlId': sid, 'error': 'no depts'}
    rows = []
    for smid, mid, nm, lclft, dght in ds:
        val = v8(sid, smid, mid, nm, ref)
        if val is not None: rows.append((lclft, nm, val, dght))
    return {'univ': name, 'schlId': sid, 'n': len(rows), 'rows': rows[:60]}

if __name__ == '__main__':
    names = sys.argv[1:] or ['한양대학교']
    out = []
    for n in names:
        r = one(n)
        out.append(r)
        print(json.dumps(r, ensure_ascii=False)[:800], flush=True)
        time.sleep(1)
    json.dump(out, open(r'C:\Users\USER\_acadinfo_out.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
