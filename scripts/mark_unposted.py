import sys
import os
from pathlib import Path

# Ensure src on path
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
sys.path.append(str(SRC))

from config import load_config
import psycopg


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/mark_unposted.py <code>")
        return
    code = sys.argv[1]
    cfg = load_config()
    dsn = cfg.get("POSTGRES_DSN") or os.environ.get("DATABASE_URL")
    print("Using DSN prefix:", (dsn[:60] + "...") if dsn else None)
    conn = psycopg.connect(dsn, autocommit=True)
    with conn.cursor() as cur:
        cur.execute("UPDATE top_trends SET isposted = FALSE WHERE code = %s", (code,))
        cur.execute("SELECT prompt, thumbnail_url, code, tag, isposted FROM top_trends WHERE code = %s", (code,))
        row = cur.fetchone()
    print("Row:", row)


if __name__ == "__main__":
    main()