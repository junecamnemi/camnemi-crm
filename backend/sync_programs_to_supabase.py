"""consulting_db → Supabase universities.programs 자동 동기화.
KB(모집공고)가 업데이트되면 사이트에 바로 반영. 실패 시 조용히 로그.
"""
import json, re, os, sys, datetime
import psycopg2

BD = r'C:\Users\wisew\camnemi-crm\backend'
KB = os.path.join(BD, 'consulting_db.json')
LOG = r'C:\Users\wisew\_sup_sync.log'

def log(m):
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(f"[{datetime.datetime.now():%Y-%m-%d %H:%M}] {m}\n")

def norm(s):
    return re.sub(r'(\ud559\uad50|\ub300\ud559|\ub300)$', '', s).strip()

def main():
    d = json.load(open(KB, encoding='utf-8'))
    src = d.get('schools', {})
    if not src:
        log("no schools in KB"); return
    norm_map = {norm(k): k for k in src}
    env = open(r'C:\Users\wisew\camnemi-crm\.env', encoding='utf-8', errors='ignore').read()
    pw = re.search(r'SUPABASE_DB_PASSWORD\s*=\s*(\S+)', env).group(1)
    conn = psycopg2.connect(host='aws-0-ap-northeast-2.pooler.supabase.com', port=5432,
                            dbname='postgres', user='postgres.zjdvzpylxazfbazioxto',
                            password=pw, connect_timeout=15)
    cur = conn.cursor()
    cur.execute("select name_kr from universities where name_kr <> '\uc138\uc885\uc0ac\uc774\ubc84\ub300\ud559\uad50'")
    targets = [r[0] for r in cur.fetchall()]
    n = 0
    for t in targets:
        key = t if t in src else norm_map.get(norm(t))
        if not key:
            continue
        progs = src[key].get('programs') or {}
        cur.execute("update universities set programs=%s::jsonb where name_kr=%s",
                    (json.dumps(progs, ensure_ascii=False), t))
        n += cur.rowcount
    conn.commit()
    cur.execute("select count(*) from universities where programs is not null")
    total = cur.fetchone()[0]
    conn.close()
    log(f"synced {n} rows; programs populated {total}")

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        log(f"ERROR {type(e).__name__}: {str(e)[:200]}")
        sys.exit(0)  # stay silent on failure (watchdog pattern)
