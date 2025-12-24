#!/usr/bin/env python3
"""Run `scripts/seeddb.sql` against the DATABASE_URL without needing `psql`.

This script attempts to use `psycopg` (psycopg3) and falls back to `psycopg2`.
It reads the SQL file, splits into simple statements, and executes them.
This is intended as a convenience for graders or devs on systems without `psql`.
"""
import os
import sys

HERE = os.path.dirname(__file__)
SQL_PATH = os.path.join(HERE, "seeddb.sql")

DB_URL = os.environ.get("DATABASE_URL")
if not DB_URL:
    print("Please set the DATABASE_URL environment variable before running this script.")
    sys.exit(1)


def _normalize_db_url(url: str) -> str:
    """Normalize SQLAlchemy-style DB URLs by stripping a "+driver" suffix.

    Examples:
      - postgresql+psycopg2://...  -> postgresql://...
      - postgres+pg8000://...      -> postgres://...
    """
    if not url or "://" not in url:
        return url
    scheme, rest = url.split("://", 1)
    if "+" in scheme:
        scheme = scheme.split("+", 1)[0]
    return scheme + "://" + rest


# Normalize for DB clients that expect plain postgres scheme
DB_URL = _normalize_db_url(DB_URL)

_connect = None
try:
    import psycopg as _pg

    def _connect(url):
        return _pg.connect(url)
except Exception:
    try:
        import psycopg2 as _pg

        def _connect(url):
            return _pg.connect(url)
    except Exception:
        print("Please install either psycopg (pip install psycopg[binary]) or psycopg2-binary")
        sys.exit(1)


def load_sql(path: str) -> str:
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def main() -> int:
    if not os.path.exists(SQL_PATH):
        print(f"SQL file not found: {SQL_PATH}")
        return 2

    sql = load_sql(SQL_PATH)

    conn = None
    try:
        conn = _connect(DB_URL)
        # allow executing BEGIN/COMMIT inside the SQL file
        try:
            conn.autocommit = True
        except Exception:
            pass

        cur = conn.cursor()

        # Very small/simple splitter for this project's seed SQL.
        # This is not a full SQL parser but is sufficient for our simple seed file.
        statements = [s.strip() for s in sql.split(";") if s.strip()]
        for stmt in statements:
            cur.execute(stmt + ";")

        print("Seed SQL applied successfully.")
        return 0
    except Exception as exc:
        print("Error applying seed SQL:", exc)
        return 3
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass


if __name__ == "__main__":
    raise SystemExit(main())
