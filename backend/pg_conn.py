"""Read camnemi-crm/.env and return a psycopg connection to the CAMNEMI_CRM Supabase Postgres.

The password never leaves this process: it is read from .env at runtime.
Tries the IPv4 session pooler first (works on hosts without IPv6), then the direct host.
"""
from __future__ import annotations

import os
import pathlib

ENV_PATH = pathlib.Path(r"C:\Users\wisew\camnemi-crm\.env")
PROJECT_REF = "zjdvzpylxazfbazioxto"
REGIONS = ["ap-southeast-1", "ap-northeast-2", "ap-northeast-1", "us-east-1", "ap-southeast-2"]


def _load_env() -> dict:
    env = {}
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    for k in ("SUPABASE_DB_PASSWORD", "SUPABASE_URL", "SUPABASE_ANON_KEY"):
        if os.environ.get(k):
            env[k] = os.environ[k]
    return env


def candidates() -> list[dict]:
    env = _load_env()
    pw = env.get("SUPABASE_DB_PASSWORD")
    if not pw:
        raise SystemExit("SUPABASE_DB_PASSWORD missing from .env")
    out = []
    for region in REGIONS:
        for port in (5432, 6543):
            out.append(dict(host=f"aws-0-{region}.pooler.supabase.com", port=port,
                            user=f"postgres.{PROJECT_REF}", password=pw, dbname="postgres"))
    out.append(dict(host=f"db.{PROJECT_REF}.supabase.co", port=5432,
                    user="postgres", password=pw, dbname="postgres"))
    return out


def connect():
    import psycopg
    last = None
    for kw in candidates():
        try:
            conn = psycopg.connect(connect_timeout=8, sslmode="require", **kw)
            conn.autocommit = False
            return conn
        except Exception as exc:  # noqa: BLE001
            last = f"{kw['host']}:{kw['port']} -> {type(exc).__name__}: {str(exc)[:120]}"
    raise SystemExit(f"no reachable Postgres endpoint. last error: {last}")


if __name__ == "__main__":
    c = connect()
    with c.cursor() as cur:
        cur.execute("select current_database(), current_user, version()")
        print("connected:", cur.fetchone()[0], "|", cur.fetchone.__self__ and "")
        cur.execute("select count(*) from cat.school")
        print("cat.school rows:", cur.fetchone()[0])
    c.close()