import os
import psycopg

def main():
    dsn = os.getenv("DATABASE_URL") or os.getenv("POSTGRES_DSN")
    if not dsn:
        print("DATABASE_URL/POSTGRES_DSN não definido no ambiente.")
        return
    print("Connecting to:", dsn[:60] + "...")
    with psycopg.connect(dsn, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "CREATE TABLE IF NOT EXISTS top_trends (id SERIAL PRIMARY KEY, prompt TEXT, thumbnail_url TEXT, code TEXT UNIQUE, tag TEXT, isposted BOOLEAN DEFAULT FALSE, created_at TIMESTAMP DEFAULT NOW())"
            )
            cur.execute(
                "INSERT INTO top_trends (prompt, thumbnail_url, code, tag, isposted) VALUES (%s,%s,%s,%s,%s) ON CONFLICT (code) DO NOTHING",
                ("Demo prompt", "https://example.com/th.jpg", "trae_demo_1", "demo", False),
            )
            cur.execute("SELECT COUNT(*) FROM top_trends")
            print("Total rows:", cur.fetchone()[0])

if __name__ == "__main__":
    main()