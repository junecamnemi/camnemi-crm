import subprocess, re, os
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
url = "https://www.gachon.ac.kr/bbs/kor/740/120007/artclView.do"
r = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
                    "--dump-dom", "--virtual-time-budget=8000", url],
                   capture_output=True, timeout=60)
dom = (r.stdout or b"").decode("utf-8", "ignore")
print(f"DOM len {len(dom)}")
print("전체 href 샘플(앞 20):")
for m in list(re.finditer(r'href=["\']([^"\']+)["\']', dom))[:20]:
    print("  ", m.group(1)[:80])
print("\n'.pdf' 포함 href:")
for u in set(re.findall(r'href=["\']([^"\']*\.pdf[^"\']*)["\']', dom, re.I)):
    print("  ", u[:100])
print("\n모집요강/입학 관련 텍스트:")
for kw in ["모집요강", "외국인", "입학", "다운로드", "download"]:
    c = dom.lower().count(kw.lower())
    if c: print(f"  {kw}: {c}")