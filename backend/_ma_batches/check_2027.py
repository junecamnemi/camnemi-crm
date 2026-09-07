import re, sys, subprocess, html as h

def fetch(url):
    # use curl to fetch
    r = subprocess.run(['curl', '-s', '-L', '-A', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', url],
                       capture_output=True, text=True, errors='ignore')
    return r.stdout

def extract_text(html_text):
    # remove scripts/styles
    html_text = re.sub(r'(?is)<(script|style)[^>]*>.*?</\1>', ' ', html_text)
    text = re.sub(r'<[^>]+>', ' ', html_text)
    text = h.unescape(text)
    text = re.sub(r'\s+', ' ', text)
    return text

def show(url, kws=('2027', '2026', '외국인', '모집요강', '전기', '후기'), ctx=100, maxhit=25):
    raw = fetch(url)
    print(f"URL: {url}  (bytes={len(raw)})")
    text = extract_text(raw)
    if '2027' in kws:
        hits = list(re.finditer('2027', text))
        print(f"2027 count: {len(hits)}")
        for m in hits[:maxhit]:
            s = max(0, m.start() - ctx); e = min(len(text), m.end() + ctx)
            print("  2027>>", text[s:e].strip())
    for kw in kws:
        if kw == '2027':
            continue
        hits = list(re.finditer(re.escape(kw), text))
        print(f"{kw} count: {len(hits)}")
        for m in hits[:8]:
            s = max(0, m.start() - 60); e = min(len(text), m.end() + 60)
            print(f"  {kw}>>", text[s:e].strip())

if __name__ == '__main__':
    url = sys.argv[1]
    show(url)
