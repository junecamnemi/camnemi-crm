#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Real-time Korea trend collector: Naver news ranking + TikTok hashtags + YouTube trending."""
import subprocess, os, re, json, urllib.request, urllib.parse, sys, datetime
CH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
T = os.environ.get("TEMP","/tmp")
UA = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
      "Accept-Language":"ko-KR,ko;q=0.9"}
def chrome(url, budget=12000, tag="t", t=90):
    r = subprocess.run([CH,"--headless=new","--disable-gpu","--no-sandbox","--lang=ko-KR",
        f"--virtual-time-budget={budget}","--user-data-dir="+os.path.join(T,"chr_"+tag),
        "--dump-dom", url], capture_output=True, timeout=t)
    return r.stdout.decode("utf-8","ignore")

def naver_news():
    """네이버 많이 본 뉴스 (랭킹)."""
    h = chrome("https://news.naver.com/main/ranking/popularDay.naver", 10000, "nvp")
    out=[]
    for m in re.finditer(r'>([가-힣][^<>]{7,60})</a>', h):
        s=m.group(1).strip()
        if s and s not in out and "전체" not in s and "알림" not in s:
            out.append(s)
    return out[:12]

def tiktok_trends():
    """TikTok discover 화제 해시태그."""
    h = chrome("https://www.tiktok.com/discover", 12000, "ttd")
    tags=[]
    for m in re.finditer(r'href="/tag/([^"?]+)"', h):
        t=urllib.parse.unquote(m.group(1))
        if t and t not in tags and len(t)<30: tags.append(t)
    return tags[:12]

def bugs_idol_chart():
    """벅스 K-POP 아이돌 전용 차트 (일간) — 멜론엔 없는 아이돌 차트."""
    try:
        h = chrome("https://music.bugs.co.kr/genre/chart/kpop/idol/total/day", 12000, "bugs")
        titles = re.findall(r'<p class="title"[^>]*>\s*<a[^>]*>([^<]{2,80})</a>', h)
        artists = re.findall(r'<p class="artist"[^>]*>\s*<a[^>]*>([^<]{2,60})</a>', h)
        return [{"rank":i+1,"song":t.strip(),"artist":(artists[i].strip() if i<len(artists) else "")} for i,t in enumerate(titles[:15])]
    except Exception as e:
        return [{"error":str(e)[:50]}]

def youtube_trending():
    """YouTube 트렌드: 급상승 피드는 비로그인 차단 → kworb(24h 최다조회 MV)로 대체."""
    try:
        h = urllib.request.urlopen(urllib.request.Request("https://kworb.net/youtube/",
            headers=UA), timeout=25).read().decode("utf-8","ignore")
        out=[]
        # kworb: <td class="text"><div><a href="video/XXXX.html">TITLE</a>
        for m in re.finditer(r'<td class="text">\s*<div>\s*<a[^>]+href="video/[^"]+"[^>]*>([^<]{2,90})</a>', h):
            t=re.sub(r"\s+"," ",m.group(1)).strip()
            if t and t not in out: out.append(t)
        if not out:
            for m in re.finditer(r'<td class="text">\s*<a[^>]*>([^<]{2,80})</a>', h):
                t=re.sub(r"\s+"," ",m.group(1)).strip()
                if t: out.append(t)
        return out[:12]
    except Exception as e:
        return [f"ERR:{str(e)[:40]}"]

def main():
    print("=== 네이버 많이 본 뉴스 ===")
    nv = naver_news()
    for x in nv[:8]: print("  ·", x)
    print("\n=== TikTok 화제 해시태그 ===")
    tt = tiktok_trends()
    for x in tt[:10]: print("  · #"+x)
    print("\n=== 벅스 K-POP 아이돌 차트 (일간) ===")
    bg = bugs_idol_chart()
    for x in bg[:10]:
        print(f"  {x.get('rank','')}. {x.get('song','')} — {x.get('artist','')}")
    print("\n=== YouTube 급상승 ===")
    yt = youtube_trending()
    for x in yt[:10]: print("  ·", x)
    res={"collected_at":datetime.datetime.now().isoformat(timespec="seconds"),
         "naver_news":nv, "tiktok_tags":tt, "bugs_idol":bg, "youtube_trending":yt}
    p=os.path.join(os.path.dirname(__file__),"trends_realtime.json")
    json.dump(res, open(p,"w",encoding="utf-8"), ensure_ascii=False, indent=1)
    print("\n저장:", p, "| nv",len(nv),"tt",len(tt),"idol",len(bg),"yt",len(yt))
if __name__=="__main__":
    main()
