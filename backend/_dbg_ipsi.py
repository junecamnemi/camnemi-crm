import requests, re
requests.packages.urllib3.disable_warnings()
BASE='https://m.adiga.kr'
H={'User-Agent':'Mozilla/5.0 (iPhone) Chrome/120.0','Accept-Language':'ko-KR,ko;q=0.9'}
r=requests.get(BASE+'/mob/ucp/uvt/uni/univDetail.do', params={'menuId':'MOUVTINF1001','unvCd':'0000009','searchSyr':'2027'}, headers=H, verify=False, timeout=25)
h=r.text
h2=h.replace('&quot;','"').replace('&#39;',"'").replace('\\/','/')
# capture full quoted arg
for m in re.finditer(r"fnOpenNewUrl\(\s*[\"']([^\"']+)[\"']\s*\)", h2):
    print('FULL:', repr(m.group(1)))
