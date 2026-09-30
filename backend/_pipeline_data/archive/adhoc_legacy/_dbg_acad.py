import sqlite3, json, os
DB = os.path.join(os.getcwd(), "package", "data", "seed", "academyinfo_15118998.sqlite")
con = sqlite3.connect(DB)
cur = con.cursor()
# 테이블 목록
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cur.fetchall()]
print("TABLES:", tables)
# 컬럼
for t in tables:
    cur.execute(f"PRAGMA table_info({t})")
    cols = [r[1] for r in cur.fetchall()]
    print(f"\n{t}: {cols}")
# 년도 분포
cur.execute("SELECT year, COUNT(*) FROM observations GROUP BY year ORDER BY year")
print("\nobservations by year:", cur.fetchall())
# indicator 목록 (재적/외국인 관련)
cur.execute("SELECT indicator_id, label_ko FROM indicators")
inds = cur.fetchall()
print("\n지표 수:", len(inds))
for iid, lab in inds:
    if any(k in lab for k in ['재적','재학','외국','학생수','학생 수','졸업','전문']):
        print(f"  {iid}: {lab}")