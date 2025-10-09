import psycopg
from typing import Dict
from typing import Dict


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS top_trends (
    id SERIAL PRIMARY KEY,
    prompt TEXT,
    thumbnail_url TEXT,
    code TEXT UNIQUE,
    tag TEXT,
    isposted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);
"""


class Database:
    def __init__(self, dsn: str):
        self.dsn = dsn
        self.conn = psycopg.connect(dsn, autocommit=True)
        with self.conn.cursor() as cur:
            cur.execute(SCHEMA_SQL)

    def exists_code(self, code: str) -> bool:
        with self.conn.cursor() as cur:
            cur.execute("SELECT 1 FROM top_trends WHERE code = %s", (code,))
            return cur.fetchone() is not None

    def insert_trend(self, item: Dict):
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO top_trends (prompt, thumbnail_url, code, tag, isposted)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (code) DO NOTHING
                """,
                (
                    item.get("prompt"),
                    item.get("thumbnail_url"),
                    item.get("content_code"),
                    item.get("tag"),
                    False,
                ),
            )

    def mark_posted(self, code: str):
        with self.conn.cursor() as cur:
            cur.execute("UPDATE top_trends SET isposted = TRUE WHERE code = %s", (code,))

    def list_unposted(self, limit: int = 10):
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT prompt, thumbnail_url, code, tag FROM top_trends WHERE isposted = FALSE ORDER BY created_at DESC LIMIT %s",
                (limit,),
            )
            rows = cur.fetchall()
            # psycopg3 default returns tuples unless row_factory is set; map to dicts
            colnames = [desc.name for desc in cur.description]
            return [
                {colnames[i]: row[i] for i in range(len(colnames))}
                for row in rows
            ]

    def list_unposted_by_tags(self, tags: list[str], limit: int = 10):
        if not tags:
            return []
        with self.conn.cursor() as cur:
            placeholders = ",".join(["%s"] * len(tags))
            sql = (
                f"SELECT prompt, thumbnail_url, code, tag FROM top_trends "
                f"WHERE isposted = FALSE AND tag IN ({placeholders}) "
                f"ORDER BY created_at DESC LIMIT %s"
            )
            cur.execute(sql, (*tags, limit))
            rows = cur.fetchall()
            colnames = [desc.name for desc in cur.description]
            return [
                {colnames[i]: row[i] for i in range(len(colnames))}
                for row in rows
            ]