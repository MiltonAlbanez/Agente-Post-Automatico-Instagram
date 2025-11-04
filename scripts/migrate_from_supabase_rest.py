import os
import sys
import json
from typing import List, Tuple

try:
    import psycopg
except ImportError:
    print("psycopg não está instalado. Execute 'pip install psycopg[binary]' e tente novamente.")
    sys.exit(1)

try:
    import requests
except ImportError:
    print("requests não está instalado. Execute 'pip install requests' e tente novamente.")
    sys.exit(1)


def normalize_supabase_url(url: str) -> str:
    """Corrige SUPABASE_URL duplicada como 'https://x...cohttps://x...co'."""
    if not url:
        return url
    if url.count("https://") > 1:
        # pega a última ocorrência válida
        parts = url.split("https://")
        return "https://" + parts[-1]
    return url


def fetch_top_trends_from_supabase(supabase_url: str, service_key: str) -> List[Tuple]:
    """Busca registros via PostgREST (Supabase REST) e retorna tuplas compatíveis."""
    headers = {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Accept": "application/json",
    }
    # Seleciona colunas esperadas no destino
    endpoint = f"{supabase_url}/rest/v1/top_trends?select=prompt,thumbnail_url,code,tag,isposted,created_at"
    resp = requests.get(endpoint, headers=headers, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    rows = []
    for item in data:
        rows.append(
            (
                item.get("prompt"),
                item.get("thumbnail_url"),
                item.get("code"),
                item.get("tag"),
                bool(item.get("isposted")),
                item.get("created_at"),
            )
        )
    return rows


def ensure_schema(conn: psycopg.Connection) -> None:
    """Cria a tabela se não existir (schema mínimo compatível)."""
    schema_sql = (
        "CREATE TABLE IF NOT EXISTS top_trends (\n"
        "    id SERIAL PRIMARY KEY,\n"
        "    prompt TEXT,\n"
        "    thumbnail_url TEXT,\n"
        "    code TEXT UNIQUE,\n"
        "    tag TEXT,\n"
        "    isposted BOOLEAN DEFAULT FALSE,\n"
        "    created_at TIMESTAMP DEFAULT NOW()\n"
        ");"
    )
    with conn.cursor() as cur:
        cur.execute(schema_sql)
    conn.commit()


def insert_rows(conn: psycopg.Connection, rows: List[Tuple]) -> Tuple[int, int]:
    inserted = 0
    with conn.cursor() as cur:
        for (prompt, thumbnail_url, code, tag, isposted, created_at) in rows:
            cur.execute(
                (
                    "INSERT INTO top_trends (prompt, thumbnail_url, code, tag, isposted, created_at) "
                    "VALUES (%s, %s, %s, %s, %s, %s) "
                    "ON CONFLICT (code) DO NOTHING"
                ),
                (prompt, thumbnail_url, code, tag, isposted, created_at),
            )
            if cur.rowcount == 1:
                inserted += 1
    conn.commit()
    return inserted, (len(rows) - inserted)


def main() -> None:
    supabase_url = normalize_supabase_url(os.getenv("SUPABASE_URL", ""))
    service_key = os.getenv("SUPABASE_SERVICE_KEY", "")
    dest_dsn = os.getenv("DATABASE_URL") or os.getenv("POSTGRES_DSN") or os.getenv("DEST_DATABASE_URL")

    if not supabase_url or not service_key:
        print("ERRO: SUPABASE_URL/SUPABASE_SERVICE_KEY ausentes nas variáveis de ambiente.")
        sys.exit(2)
    if not dest_dsn:
        print("ERRO: Defina DATABASE_URL/POSTGRES_DSN/DEST_DATABASE_URL para o destino.")
        sys.exit(3)

    print("Buscando registros no Supabase REST...")
    rows = fetch_top_trends_from_supabase(supabase_url, service_key)
    print(f"Registros obtidos: {len(rows)}")

    print("Conectando ao Postgres de DESTINO...")
    with psycopg.connect(dest_dsn) as conn:
        ensure_schema(conn)
        inserted, skipped = insert_rows(conn, rows)
    print("Migração via REST concluída.")
    print(f"Inseridos: {inserted}")
    print(f"Ignorados (duplicatas por code): {skipped}")


if __name__ == "__main__":
    main()