import argparse
import os
import sys
from typing import Optional

try:
    import psycopg
except ImportError:
    print("psycopg não está instalado. Execute 'pip install psycopg[binary]' e tente novamente.")
    sys.exit(1)


def get_schema_sql() -> str:
    """Obtém o SQL de criação de tabela do módulo db, com fallback local."""
    # Tenta reutilizar o schema do serviço para manter compatibilidade
    try:
        sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
        from src.services.db import SCHEMA_SQL  # type: ignore
        return SCHEMA_SQL
    except Exception:
        # Fallback: schema mínimo baseado em src/services/db.py
        return (
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


def migrate_top_trends(source_dsn: str, dest_dsn: str, copy_only_unposted: bool = False) -> None:
    """Migra dados da tabela top_trends entre duas conexões Postgres.

    - Cria a tabela de destino se não existir (mesmo schema usado pelo serviço).
    - Copia registros evitando duplicatas via ON CONFLICT (code) DO NOTHING.
    - Opcionalmente copia apenas não postados (isposted = false).
    """
    where_clause = "WHERE isposted = FALSE" if copy_only_unposted else ""
    select_sql = (
        f"SELECT prompt, thumbnail_url, code, tag, isposted, created_at FROM top_trends {where_clause}"
    )

    print("Conectando ao banco de ORIGEM...")
    with psycopg.connect(source_dsn) as src_conn:
        src_conn.execute("SET statement_timeout = '5min'")
        with src_conn.cursor() as cur:
            cur.execute(select_sql)
            rows = cur.fetchall()
            print(f"Registros encontrados na origem: {len(rows)}")

    print("Conectando ao banco de DESTINO...")
    with psycopg.connect(dest_dsn) as dst_conn:
        dst_conn.execute("SET statement_timeout = '5min'")
        schema_sql = get_schema_sql()
        with dst_conn.cursor() as cur:
            cur.execute(schema_sql)
        dst_conn.commit()

        inserted = 0
        with dst_conn.cursor() as cur:
            for (prompt, thumbnail_url, code, tag, isposted, created_at) in rows:
                cur.execute(
                    (
                        "INSERT INTO top_trends (prompt, thumbnail_url, code, tag, isposted, created_at) "
                        "VALUES (%s, %s, %s, %s, %s, %s) "
                        "ON CONFLICT (code) DO NOTHING"
                    ),
                    (prompt, thumbnail_url, code, tag, isposted, created_at),
                )
                # Conta apenas os que realmente inseriram (rowcount pode ser 1 ou 0)
                if cur.rowcount == 1:
                    inserted += 1
        dst_conn.commit()

    skipped = len(rows) - inserted
    print("Migração concluída.")
    print(f"Inseridos: {inserted}")
    print(f"Ignorados (duplicatas por code): {skipped}")


def resolve_dsn(cli_arg: Optional[str], env_keys: list[str]) -> Optional[str]:
    """Resolve DSN via argumento CLI, depois variáveis de ambiente (primeira encontrada)."""
    if cli_arg:
        return cli_arg
    for key in env_keys:
        val = os.getenv(key)
        if val:
            return val
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Migração da tabela top_trends entre bancos Postgres")
    parser.add_argument("--source", help="DSN da origem (ex: postgresql://user:pass@host:port/db)")
    parser.add_argument("--dest", help="DSN do destino (ex: postgresql://user:pass@host:port/db)")
    parser.add_argument(
        "--only-unposted",
        action="store_true",
        help="Copiar apenas registros com isposted = FALSE",
    )
    args = parser.parse_args()

    source_dsn = resolve_dsn(args.source, [
        "SOURCE_DATABASE_URL",
        "SOURCE_POSTGRES_DSN",
        "SUPABASE_DB_URL",  # caso esteja migrando da base do Supabase
    ])
    dest_dsn = resolve_dsn(args.dest, [
        "DATABASE_URL",
        "POSTGRES_DSN",
        "DEST_DATABASE_URL",
        "DEST_POSTGRES_DSN",
    ])

    if not source_dsn:
        print(
            "ERRO: DSN de origem não informado. Use --source ou exporte uma variável como SOURCE_DATABASE_URL/SUPABASE_DB_URL."
        )
        sys.exit(2)
    if not dest_dsn:
        print(
            "ERRO: DSN de destino não informado. Use --dest ou exporte uma variável como DATABASE_URL/POSTGRES_DSN/DEST_DATABASE_URL."
        )
        sys.exit(3)

    print("Iniciando migração de top_trends...")
    migrate_top_trends(source_dsn, dest_dsn, copy_only_unposted=args.only_unposted)


if __name__ == "__main__":
    main()