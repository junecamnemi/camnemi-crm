import sys, io, re, urllib.request, ssl, gzip

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def fetch(url, timeout=25):
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36',
        'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
            data = r.read()
            if r.headers.get('Content-Encoding') == 'gzip':
                data = gzip.decompress(data)
            charset = r.headers.get_content_charset() or 'utf-8'
            try:
                return data.decode(charset, errors='ignore')
            except Exception:
                return data.decode('utf-8', errors='ignore')
    except Exception as e:
        return f'__FETCH_ERROR__ {e}'

def scan(url):
    h = fetch(url)
    if h.startswith('__FETCH_ERROR__'):
        print(f'### {url}\nERROR: {h}\n')
        return
    print(f'### {url}  LEN={len(h)}')
    for kw in ['2027학년도', '2027', '외국인전형', '외국인', '전기모집', '전기', '후기모집', '모집요강', '입학안내']:
        c = h.count(kw)
        if c:
            print(f'   {kw}: {c}')
    # print anchor texts that mention 2027
    for m in re.finditer(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', h, re.S):
        txt = re.sub(r'<[^>]+>', '', m.group(2)).strip()
        if '2027' in txt or '외국인전형' in txt:
            print(f'   LINK: {txt[:70]!r} -> {m.group(1)[:130]}')
    print()

if __name__ == '__main__':
    for u in sys.argv[1:]:
        scan(u)
