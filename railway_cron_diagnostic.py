import os
import sys
import time
import json


def check_env_vars():
    required = [
        "TZ",
        "RAILWAY_ENVIRONMENT",
        "TELEGRAM_BOT_TOKEN",
        "TELEGRAM_CHAT_ID",
        "OPENAI_API_KEY",
        "POSTGRES_DSN",
        "SUPABASE_URL",
        "SUPABASE_SERVICE_KEY",
    ]
    missing = [v for v in required if not os.getenv(v)]
    return missing


def main():
    info = {
        "timestamp": int(time.time()),
        "env": {
            k: (os.getenv(k) is not None)
            for k in [
                "TZ",
                "RAILWAY_ENVIRONMENT",
                "TELEGRAM_BOT_TOKEN",
                "TELEGRAM_CHAT_ID",
                "OPENAI_API_KEY",
                "POSTGRES_DSN",
                "SUPABASE_URL",
                "SUPABASE_SERVICE_KEY",
            ]
        },
    }

    missing = check_env_vars()
    info["missing_env_vars"] = missing

    print(json.dumps(info, indent=2, ensure_ascii=False))
    if missing:
        print("⚠️  Variáveis de ambiente ausentes:", ", ".join(missing))
    else:
        print("✅ Diagnóstico básico OK: variáveis de ambiente presentes")


if __name__ == "__main__":
    main()