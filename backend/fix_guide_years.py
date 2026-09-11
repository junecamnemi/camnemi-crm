#!/usr/bin/env python3
"""fix_guide_years.py — set university_guides.year from the year stated INSIDE each
guide PDF (not the filename, which adiga mislabels).

WHY (lesson 2026-09): adiga filenames like `0000149_연세대학교[본교]_2026_외국인.pdf`
claim 2026 but the document inside says "2025학년도" — 26 such files. The filename's
year is the COLLECTION cycle, not the guide's academic year. Always read the year from
the first pages of the PDF: prefer "<YYYY>학년도", then "Academic Year YYYY", then a
year attached to 학기/전기/후기/Spring/Fall. Clamp to 2018..2028 to reject noise.

Run after any guide ingest, before trusting year filters.
"""
import os, re, sys, json, zipfile, urllib.request, urllib.parse
from collections import defaultdict, Counter
sys.path.insert(0, r'C:\Users\USER\pdf-venv\Lib\site-packages')
import pymupdf

UP = r'C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project'
PROG = {'대학원':'ma','어학연수':'lang','외국인':'ba','전문대학':'junior'}
ALIAS = {'포스텍':'포항공과대학교','한국해양대학교':'국립한국해양대학교','한국교통대학교':'국립한국교통대학교',
         '부경대학교':'국립부경대학교','창원대학교':'국립창원대학교','용인송담대학교':'용인예술과학대학교'}

def intake_from_period(t):
    """Derive the intake academic year from the application dates in the document.
    Korean 전기(3월 입학) applications run Aug–Dec of the PREVIOUS year, so a
    period starting 2025.8 means the 2026 intake. This beats reading '<YYYY>학년도',
    because guides often carry a next-year PRE-NOTICE (사전 예고) section — e.g.
    고려대's guide says '2027학년도 사전 예고' while its schedule (2025.8) is 2026."""
    dates=[]
    for m in re.finditer(r'(20\d\d)\s*[.\-년]\s*(\d{1,2})', t):
        y,mo=int(m.group(1)),int(m.group(2))
        if 2018<=y<=2028 and 1<=mo<=12: dates.append((y,mo,m.start()))
    if not dates: return None
    # the application window is usually the earliest full date pair in the doc
    dates.sort(key=lambda d:(d[2]))
    y,mo,_=dates[0]
    if mo>=8: return str(y+1)      # 전기 (March intake) of next year
    if mo<=2: return str(y)        # 정시/추가 (Jan-Feb) -> same-year intake
    return str(y)                  # 3–7월 (후기/9월 입학 등)

def doc_year(t):
    # If the document itself is a next-year PRE-NOTICE (title says 사전 예고), the
    # real intake comes from its schedule, not the year it announces (고려대 case).
    if re.search(r'사전\s*예고|예고\s*모집요강', t[:1200]):
        py = intake_from_period(t)
        if py: return py
    # 1) most common "<YYYY>학년도", IGNORING pre-notice mentions — a guide often carries
    #    a next-year 사전예고/예고 section that must not become the guide's year.
    ys=[]
    for m in re.finditer(r'(20\d\d)\s*학년도', t):
        ctx=t[max(0,m.start()-40):m.start()+40]
        if re.search(r'사전\s*예고|예고\s*(사항|안내)|예정|변경\s*사항|개정', ctx): continue
        y=m.group(1)
        if 2018<=int(y)<=2028: ys.append(y)
    if ys: return Counter(ys).most_common(1)[0][0]
    # 2) explicit English academic year
    m=re.search(r'(?:academic\s*year|AY)\s*[:\-]?\s*(20\d\d)', t, re.I)
    if m and 2018<=int(m.group(1))<=2028: return m.group(1)
    # 3) derive from the application window (전기 = Aug–Dec of the previous year)
    return intake_from_period(t)

def school_of(name):
    n=os.path.basename(name)
    n=re.sub(r'^\d+_','',n); n=re.sub(r'\[.*?\]','',n)
    n=re.sub(r'_?20\d\d_?.*$','',n)
    n=re.sub(r'_(대학원|어학연수|외국인|전문대학|한국어교육원|전문학사).*$','',n)
    return re.sub(r'\.pdf$','',n,flags=re.I).strip('_ ').strip()

def key():
    h=open(r"C:\Users\USER\camnemi-crm\index.html",encoding="utf-8").read()
    return re.search(r"DEFAULT_SUPABASE_KEY\s*=\s*'([^']+)'",h).group(1)

def main():
    K=key(); base="https://zjdvzpylxazfbazioxto.supabase.co/rest/v1/"
    def q(p):
        r=urllib.request.Request(base+p,headers={'apikey':K,'Authorization':'Bearer '+K})
        return json.loads(urllib.request.urlopen(r,timeout=40).read())
    univs={u['id'] for u in q('universities?select=id&limit=500')}
    def resolve(s):
        s=(s or '').strip()
        if s in univs: return s
        if s in ALIAS and ALIAS[s] in univs: return ALIAS[s]
        for a,uid in ALIAS.items():
            if a in s and uid in univs: return uid
        for uid in univs:
            if uid in s or s.startswith(uid): return uid
        return None

    items=[]
    for d in os.listdir(UP):
        p=os.path.join(UP,d)
        if not os.path.isdir(p) or '모집요강' not in d: continue
        pr=next((v for k,v in PROG.items() if k in d),'ba')
        for f in os.listdir(p):
            if f.lower().endswith('.pdf'): items.append((os.path.join(p,f),pr,f))
    z=os.path.join(UP,'adiga_2026_외국인_모집요강.zip')
    if os.path.exists(z):
        with zipfile.ZipFile(z) as zf:
            for nm in zf.namelist():
                if nm.lower().endswith('.pdf'): items.append(((z,nm),'ba',os.path.basename(nm)))

    truth=defaultdict(lambda: defaultdict(list))
    for src,pr,name in items:
        try:
            if isinstance(src,tuple):
                with zipfile.ZipFile(src[0]) as zf: doc=pymupdf.open(stream=zf.read(src[1]),filetype='pdf')
            else: doc=pymupdf.open(src)
            t="".join(doc[i].get_text() for i in range(min(len(doc),4))); doc.close()
        except Exception: continue
        dy=doc_year(t); uid=resolve(school_of(name))
        if dy and uid: truth[uid][pr].append(dy)

    fixed=0
    for g in q('university_guides?select=univ_id,track,year&limit=2000'):
        yrs=truth.get(g['univ_id'],{}).get(g['track'])
        if not yrs: continue
        newest=max(yrs)                      # we hold (at least) the newest of them
        if g['year']==newest: continue
        r=urllib.request.Request(base+'university_guides?univ_id=eq.'+urllib.parse.quote(g['univ_id'])+'&track=eq.'+g['track'],
            data=json.dumps({'year':newest}).encode(), method='PATCH',
            headers={'apikey':K,'Authorization':'Bearer '+K,'Content-Type':'application/json','Prefer':'return=minimal'})
        try: urllib.request.urlopen(r,timeout=25).read(); fixed+=1
        except Exception: pass
    print(f"corrected {fixed} guide years from document content")
    from collections import Counter
    print("year distribution now:", dict(Counter(x['year'] for x in q('university_guides?select=year&limit=2000'))))

if __name__=='__main__': main()
