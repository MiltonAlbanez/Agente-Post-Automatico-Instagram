import psycopg
from typing import Dict
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse
import os
import logging


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
        self.dsn = self._validate_and_harden_dsn(dsn)
        self.conn = psycopg.connect(self.dsn, autocommit=True)
        with self.conn.cursor() as cur:
            cur.execute(SCHEMA_SQL)

    def _validate_and_harden_dsn(self, dsn: str) -> str:
        """Valida o DSN (URI) e aplica opções seguras para evitar erros de protocolo.
        - Garante esquema postgres/postgresql
        - Garante host e database presentes
        - Aplica sslmode=require para domínios Supabase e quando variável FORCE_SSLMODE_REQUIRE=true
        - Define connect_timeout=10 se ausente
        """
        if not dsn:
            raise ValueError("POSTGRES DSN vazio")
        # Permitir DSN em formato URI
        parsed = urlparse(dsn)
        scheme = parsed.scheme.lower()
        if scheme not in ("postgres", "postgresql"):
            raise ValueError(f"Esquema DSN inválido: {scheme} (esperado 'postgres' ou 'postgresql')")
        if not parsed.hostname:
            raise ValueError("Host ausente no DSN")
        if not parsed.path or parsed.path == "/":
            raise ValueError("Database ausente no DSN")

        # Opções da query
        query_params = dict(parse_qsl(parsed.query))
        needs_ssl = (
            os.getenv("FORCE_SSLMODE_REQUIRE", "false").lower() in ("1", "true", "yes")
            or (parsed.hostname or "").endswith("supabase.co")
        )
        if needs_ssl and query_params.get("sslmode") is None:
            query_params["sslmode"] = "require"
        if query_params.get("connect_timeout") is None:
            query_params["connect_timeout"] = "10"

        # Reconstruir DSN
        new_query = urlencode(query_params)
        hardened = urlunparse(
            (
                parsed.scheme,
                parsed.netloc,
                parsed.path,
                parsed.params,
                new_query,
                parsed.fragment,
            )
        )

        # Log de saneamento (não expõe segredos)
        try:
            logger = logging.getLogger(__name__)
            logger.info(
                f"DSN validado: host={parsed.hostname}, db={parsed.path.lstrip('/')} sslmode={query_params.get('sslmode','')} timeout={query_params.get('connect_timeout','')}"
            )
        except Exception:
            pass

        return hardened

    def check_connectivity(self) -> bool:
        """Executa SELECT 1 para validar conexão rapidamente."""
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT 1")
                return cur.fetchone() is not None
        except Exception:
            return False

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