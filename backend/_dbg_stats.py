import requests, re
requests.packages.urllib3.disable_warnings()
BASE='https://m.adiga.kr'
H={'User-Agent':'Mozilla/5.0 (iPhone) Chrome/120.0','Accept-Language':'ko-KR,ko;q=0.9'}
# univDetail 전체에서 통계 관련 라벨/탭 스캔
r=requests.get(BASE+'/mob/ucp/uvt/uni/univDetail.do', params={'menuId':'MOUVTINF1001','unvCd':'0002748','searchSyr':'2027'}, headers=H, verify=False, timeout=25)
h=r.text
txt=re.sub(r'<[^>]+>',' ',h)
txt=re.sub(r'\s+',' ',txt)
print('len html', len(h), 'len txt', len(txt))
print()
# 통계 키워드 다 찾기
kws=['재적','재학','학생수','학생 수','외국인','전체학생','학부생','졸업','취업률','모집인원','총정원','등록인원','신입','입학정원','국적별','중도탈락','전임교원','교원','정원내']
for kw in kws:
    i=txt.find(kw)
    if i>=0:
        seg=txt[max(0,i-30):i+80]
        print(f'[{kw}]: ...{seg}...')
# 모든 탭/메뉴 이름
print()
print('=== 탭/메뉴 후보 ===')
for m in sorted(set(re.findall(r'>([^<>]{2,12})</(?:button|a|span|li|div|p)>', h))):
    if any(k in m for k in ['학생','재적','통계','대학','경쟁','인원','교육','홈페이지','입학','모집','정보']):
        print(' ', m)