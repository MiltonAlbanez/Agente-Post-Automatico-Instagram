#!/usr/bin/env python3
"""
Monitoramento da próxima execução programada (BRT) e verificação de prontidão.
- Calcula próxima execução configurada (Stories 21h BRT).
- Opcionalmente envia notificação ao Telegram se variáveis estiverem presentes.
- Integra com verificadores existentes para validar arquivos e variáveis.
"""

import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

try:
    from zoneinfo import ZoneInfo  # Python 3.9+
except Exception:
    ZoneInfo = None

# Importa utilitários existentes, se disponíveis
BASE_PATH = Path(__file__).parent
sys.path.append(str(BASE_PATH))

# Telegram
telegram_available = False
try:
    from src.services.telegram_client import TelegramClient
    telegram_available = True
except Exception:
    telegram_available = False

# Verificadores
scheduler_info = {}
try:
    import scheduler_verification
except Exception:
    scheduler_verification = None

try:
    import system_integrity_verification
except Exception:
    system_integrity_verification = None


def brt_now():
    """Retorna datetime atual em BRT (America/Sao_Paulo)."""
    if ZoneInfo:
        tz = ZoneInfo("America/Sao_Paulo")
        return datetime.now(tz)
    # Fallback sem zoneinfo (assume local como BRT)
    return datetime.now()


def next_brt_time(target_hour: int) -> datetime:
    """Calcula próxima ocorrência de target_hour (0-23) em BRT."""
    now = brt_now()
    candidate = now.replace(hour=target_hour, minute=0, second=0, microsecond=0)
    if candidate <= now:
        candidate += timedelta(days=1)
    return candidate


def check_files_and_env():
    """Verifica arquivos essenciais e variáveis de ambiente."""
    status = {
        "files_present": {},
        "issues": [],
        "env": {
            "TZ": os.environ.get("TZ"),
            "RAILWAY_ENVIRONMENT": os.environ.get("RAILWAY_ENVIRONMENT"),
            "TELEGRAM_BOT_TOKEN": bool(os.environ.get("TELEGRAM_BOT_TOKEN")),
            "TELEGRAM_CHAT_ID": bool(os.environ.get("TELEGRAM_CHAT_ID")),
        }
    }
    for fname in ["Procfile", "railway.json", "accounts.json", "src/main.py"]:
        status["files_present"][fname] = (BASE_PATH / fname).exists()
        if not status["files_present"][fname]:
            status["issues"].append(f"Arquivo ausente: {fname}")
    return status


def send_telegram(message: str):
    """Envia mensagem ao Telegram se disponível e configurado."""
    if not telegram_available:
        return False
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        return False
    try:
        client = TelegramClient(bot_token=token, chat_id=chat_id)
        client.send_message(message)
        return True
    except Exception:
        return False


def main():
    print("🕒 Monitoramento da Próxima Execução (Stories 21h BRT)")
    print("=" * 60)

    # Valida configuração básica
    cfg = check_files_and_env()
    for k, v in cfg["files_present"].items():
        print(f"  {'✅' if v else '❌'} {k}")
    if cfg["issues"]:
        print("\n⚠️  Issues:")
        for issue in cfg["issues"]:
            print(f" - {issue}")

    # Integra verificadores se disponíveis
    if scheduler_verification:
        try:
            print("\n🔎 Verificando scheduler_verification...")
            verifier = scheduler_verification.SchedulerVerifier(base_path=BASE_PATH)
            _ = verifier.verify_railway_configuration()
        except Exception as e:
            print(f"  ❌ Falha scheduler_verification: {e}")

    if system_integrity_verification:
        try:
            print("\n🔎 Verificando system_integrity_verification...")
            siv = system_integrity_verification.SystemIntegrityVerification(base_path=BASE_PATH)
            _ = siv.verify_scheduler_readiness()
        except Exception as e:
            print(f"  ❌ Falha system_integrity_verification: {e}")

    # Calcula próxima execução 21h BRT
    target = next_brt_time(21)
    now = brt_now()
    delta = target - now
    hours, remainder = divmod(int(delta.total_seconds()), 3600)
    minutes = remainder // 60

    print("\n⏰ Próxima execução (Stories) configurada:")
    print(f"  • Data/hora BRT: {target.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"  • Em ~ {hours}h {minutes}m")

    # Notifica Telegram
    msg = (
        f"📣 Monitoramento: Próxima execução de Stories às 21h BRT\n"
        f"Data/hora: {target.strftime('%Y-%m-%d %H:%M:%S %Z')}\n"
        f"Faltam ~ {hours}h {minutes}m"
    )
    if send_telegram(msg):
        print("\n✅ Notificação enviada ao Telegram")
    else:
        print("\nℹ️ Telegram não configurado ou indisponível (pulado)")


if __name__ == "__main__":
    main()