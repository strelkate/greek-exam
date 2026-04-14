from contextlib import contextmanager
from typing import Generator
import psycopg2
import psycopg2.extras
import config


@contextmanager
def get_conn() -> Generator:
    """Yield a psycopg2 connection, auto-closing on exit."""
    conn = psycopg2.connect(config.DATABASE_URL)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def fetchall(sql: str, params: tuple = ()) -> list[dict]:
    """Run a SELECT and return rows as list of dicts."""
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params)
            return [dict(r) for r in cur.fetchall()]


def fetchone(sql: str, params: tuple = ()) -> dict | None:
    """Run a SELECT and return first row as dict or None."""
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params)
            row = cur.fetchone()
            return dict(row) if row else None


def execute(sql: str, params: tuple = ()) -> None:
    """Run INSERT/UPDATE/DELETE."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)


def executemany(sql: str, rows: list[tuple]) -> None:
    """Run INSERT/UPDATE for many rows."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.executemany(sql, rows)
