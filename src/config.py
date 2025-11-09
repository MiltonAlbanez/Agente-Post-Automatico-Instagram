import os
from dotenv import load_dotenv


def load_config():
    load_dotenv()
    # Suporte ao Railway: preferir DATABASE_URL quando disponível
    postgres_dsn = os.getenv("DATABASE_URL") or os.getenv("POSTGRES_DSN", "")
    
    # Se DATABASE_URL contém endereço interno do Railway, usar DATABASE_PUBLIC_URL para testes locais
    if postgres_dsn and "railway.internal" in postgres_dsn:
        public_dsn = os.getenv("DATABASE_PUBLIC_URL")
        if public_dsn:
            postgres_dsn = public_dsn
    return {
        "INSTAGRAM_BUSINESS_ACCOUNT_ID": os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID", ""),
        "INSTAGRAM_ACCESS_TOKEN": os.getenv("INSTAGRAM_ACCESS_TOKEN", ""),
        "TELEGRAM_CHAT_ID": os.getenv("TELEGRAM_CHAT_ID", ""),
        "TELEGRAM_BOT_TOKEN": os.getenv("TELEGRAM_BOT_TOKEN", ""),
        "RAPIDAPI_KEY": os.getenv("RAPIDAPI_KEY", ""),
        "RAPIDAPI_HOST": os.getenv("RAPIDAPI_HOST", "instagram-scraper-api2.p.rapidapi.com"),
        "RAPIDAPI_ALT_HOSTS": os.getenv("RAPIDAPI_ALT_HOSTS", ""),
        "REPLICATE_TOKEN": os.getenv("REPLICATE_TOKEN", ""),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
        "POSTGRES_DSN": postgres_dsn,
        # Supabase Storage (opcional)
        "SUPABASE_URL": os.getenv("SUPABASE_URL", ""),
        "SUPABASE_SERVICE_KEY": os.getenv("SUPABASE_SERVICE_KEY", ""),
        "SUPABASE_BUCKET": os.getenv("SUPABASE_BUCKET", ""),
    }