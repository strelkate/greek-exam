#!/usr/bin/env python3
"""
Migrate data from local SQLite (dev.db) to PostgreSQL.

Usage:
    uv run python migrate_sqlite_to_postgres.py \
        --sqlite ./dev.db \
        --postgres "postgresql://greekapp:PASSWORD@HOST/greekapp"
"""
import argparse
import json
import sqlite3
import asyncio
import sys
from datetime import date, datetime

import asyncpg


TABLES_IN_ORDER = [
    "curriculum_units",
    "exercises",
    "vocabulary_cards",
    "users",
    "user_progress",
    "vocabulary_progress",
]


def sqlite_val(v):
    """Convert SQLite value to Python type for asyncpg."""
    if isinstance(v, str):
        # Try JSON
        stripped = v.strip()
        if stripped.startswith(("[", "{")):
            try:
                return json.loads(stripped)
            except Exception:
                pass
    return v


async def migrate(sqlite_path: str, pg_dsn: str):
    conn_sq = sqlite3.connect(sqlite_path)
    conn_sq.row_factory = sqlite3.Row

    pg = await asyncpg.connect(pg_dsn)

    try:
        for table in TABLES_IN_ORDER:
            rows = conn_sq.execute(f"SELECT * FROM {table}").fetchall()
            if not rows:
                print(f"  {table}: 0 rows, skipping")
                continue

            cols = rows[0].keys()
            col_list = ", ".join(f'"{c}"' for c in cols)
            placeholders = ", ".join(f"${i+1}" for i in range(len(cols)))
            sql = f'INSERT INTO "{table}" ({col_list}) VALUES ({placeholders}) ON CONFLICT DO NOTHING'

            values = []
            for row in rows:
                values.append(tuple(sqlite_val(row[c]) for c in cols))

            await pg.executemany(sql, values)

            # Reset sequence if there's an id column
            if "id" in cols:
                await pg.execute(
                    f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), "
                    f"COALESCE((SELECT MAX(id) FROM \"{table}\"), 1))"
                )

            print(f"  {table}: {len(rows)} rows migrated")

        print("\n✅ Migration complete!")
    finally:
        conn_sq.close()
        await pg.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--sqlite", default="./dev.db")
    parser.add_argument("--postgres", required=True)
    args = parser.parse_args()

    print(f"Migrating {args.sqlite} → PostgreSQL...")
    asyncio.run(migrate(args.sqlite, args.postgres))
