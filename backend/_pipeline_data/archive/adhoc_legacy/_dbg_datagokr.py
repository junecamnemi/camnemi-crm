import os, json, glob
# 찾기: academyinfo-mcp 설치 여부 / data.go.kr 키 / 기존 스냅샷
print("=== academyinfo-mcp 패키지 ===")
try:
    import academyinfo_mcp
    print("academyinfo_mcp 설치됨:", academyinfo_mcp.__file__)
except ImportError:
    print("academyinfo_mcp 미설치")
# npm 전역?
home = os.path.expanduser("~")
for pat in ["**/academyinfo*/data/seed/*.sqlite", "**/academyinfo_15118998*.sqlite"]:
    for p in glob.glob(os.path.join(home, pat), recursive=True)[:5]:
        print("SQLITE:", p)
# data.go.kr 키 후보
print("=== data.go.kr 키 (env) ===")
for k in ["DATA_GO_KR_KEY","DATAGOKR_KEY","DATA_GO_KOREA_KEY","AGRI_KEY","PUBLIC_DATA_KEY"]:
    if os.environ.get(k): print("  ", k, "set")