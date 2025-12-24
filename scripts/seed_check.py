#!/usr/bin/env python3
"""Simple seed validation script.

Connects to the DB defined by `DATABASE_URL` and prints counts for key tables.
Attempts to use `psycopg` (psycopg3) and falls back to `psycopg2`.
"""
import os
import sys

DB_URL = os.environ.get("DATABASE_URL")
if not DB_URL:
    print("Please set the DATABASE_URL environment variable (e.g. export DATABASE_URL=postgresql://user:pass@host/db)")
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

TABLES = ["directors", "genres", "movies", "movie_genres", "movie_ratings"]


def main() -> int:
    conn = None
    try:
        conn = _connect(DB_URL)
        cur = conn.cursor()
        print("Connected to database; counting rows:")
        for t in TABLES:
            cur.execute(f"SELECT COUNT(*) FROM {t};")
            row = cur.fetchone()
            n = row[0] if row else 0
            print(f"- {t}: {n}")
        return 0
    except Exception as exc:
        print("Error while checking seed data:", exc)
        return 2
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass


if __name__ == "__main__":
    raise SystemExit(main())
