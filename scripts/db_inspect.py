import os
import sys
from pathlib import Path

# Garantir que o diretório src esteja no path
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
sys.path.append(str(SRC))

from config import load_config
from services.db import Database


def main():
    cfg = load_config()
    dsn = cfg.get("POSTGRES_DSN") or os.getenv("DATABASE_URL")
    print("DSN prefix:", (dsn[:60] + "...") if dsn else None)
    try:
        db = Database(cfg["POSTGRES_DSN"])  # garante criação de schema
        # Contagem total
        try:
            with db.conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM top_trends")
                total = cur.fetchone()[0]
            print("Total rows:", total)
        except Exception as e:
            print("Count error:", e)
        # Não postados
        rows = db.list_unposted(10)
        print("Unposted count:", len(rows))
        for r in rows:
            print(r)
        # Últimos códigos
        try:
            with db.conn.cursor() as cur:
                cur.execute("SELECT code, isposted, tag, created_at FROM top_trends ORDER BY created_at DESC LIMIT 10")
                last = cur.fetchall()
            print("Last rows:", last)
        except Exception as e:
            print("Last rows error:", e)
        # Verificar seeds específicos
        try:
            with db.conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM top_trends WHERE code IN (%s, %s)", ("trae_demo_1", "trae_demo_2"))
                c = cur.fetchone()[0]
            print("Seed demo present count (1/2):", c)
        except Exception as e:
            print("Seed check error:", e)
        # Diagnóstico de defaults e triggers
        try:
            with db.conn.cursor() as cur:
                cur.execute("SELECT column_name, column_default FROM information_schema.columns WHERE table_name='top_trends'")
                cols = cur.fetchall()
            print("Column defaults:", cols)
        except Exception as e:
            print("Column defaults error:", e)
        try:
            with db.conn.cursor() as cur:
                cur.execute("SELECT tgname FROM pg_trigger WHERE NOT tgisinternal AND tgrelid = 'top_trends'::regclass")
                trigs = cur.fetchall()
            print("Triggers:", trigs)
        except Exception as e:
            print("Triggers error:", e)
    except Exception as e:
        print("DB error:", e)


if __name__ == "__main__":
    main()