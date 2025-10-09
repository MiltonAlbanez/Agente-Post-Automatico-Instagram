import os
from dotenv import load_dotenv


def load_config():
    load_dotenv()
    return {
        "INSTAGRAM_BUSINESS_ACCOUNT_ID": os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID", ""),
        "INSTAGRAM_ACCESS_TOKEN": os.getenv("INSTAGRAM_ACCESS_TOKEN", ""),
        "TELEGRAM_CHAT_ID": os.getenv("TELEGRAM_CHAT_ID", ""),
        "TELEGRAM_BOT_TOKEN": os.getenv("TELEGRAM_BOT_TOKEN", ""),
        "RAPIDAPI_KEY": os.getenv("RAPIDAPI_KEY", ""),
        "RAPIDAPI_HOST": os.getenv("RAPIDAPI_HOST", "instagram-scraper-api2.p.rapidapi.com"),
        "REPLICATE_TOKEN": os.getenv("REPLICATE_TOKEN", ""),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
        "POSTGRES_DSN": os.getenv("POSTGRES_DSN", ""),
        # Supabase Storage (opcional)
        "SUPABASE_URL": os.getenv("SUPABASE_URL", ""),
        "SUPABASE_SERVICE_KEY": os.getenv("SUPABASE_SERVICE_KEY", ""),
        "SUPABASE_BUCKET": os.getenv("SUPABASE_BUCKET", ""),
    }