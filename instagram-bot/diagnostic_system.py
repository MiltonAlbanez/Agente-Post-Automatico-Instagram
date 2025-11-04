import os
import sys
import time
from typing import Dict, List, Optional, Tuple

import requests
from dotenv import load_dotenv
from pathlib import Path
import re

try:
    import psycopg2
except Exception:
    psycopg2 = None


def get_env(name: str, default: Optional[str] = None) -> Optional[str]:
    return os.getenv(name, default)


def check_env_vars(required: List[str]) -> List[str]:
    missing = []
    for var in required:
        if not os.getenv(var):
            missing.append(var)
    return missing


def check_http_endpoint(url: str, timeout: int = 10) -> Tuple[bool, str]:
    try:
        resp = requests.get(url, timeout=timeout)
        return (resp.status_code == 200, f"HTTP {resp.status_code} for {url}")
    except Exception as e:
        return (False, f"HTTP error for {url}: {e}")


def check_telegram(token: Optional[str], chat_id: Optional[str], send_enabled: bool) -> Tuple[bool, str]:
    if not token:
        return (False, "TELEGRAM_BOT_TOKEN ausente")
    base = f"https://api.telegram.org/bot{token}"
    try:
        me = requests.get(f"{base}/getMe", timeout=10)
        if me.status_code != 200:
            return (False, f"getMe falhou: HTTP {me.status_code}")
    except Exception as e:
        return (False, f"Falha ao conectar ao Telegram: {e}")

    sent_msg = ""
    if send_enabled and chat_id:
        try:
            txt = f"[diagnostic] Sistema de diagnóstico iniciado em {time.strftime('%Y-%m-%d %H:%M:%S')}"
            send = requests.post(f"{base}/sendMessage", json={"chat_id": chat_id, "text": txt}, timeout=10)
            sent_msg = f"; mensagem enviada: HTTP {send.status_code}"
        except Exception as e:
            return (False, f"Conectado ao Telegram, mas envio falhou: {e}")

    return (True, f"Conectado ao Telegram{sent_msg}")


def check_postgres(dsn: Optional[str]) -> Tuple[bool, str]:
    if psycopg2 is None:
        return (False, "psycopg2 não instalado; instale 'psycopg2-binary'")

    conn = None
    try:
        if dsn:
            conn = psycopg2.connect(dsn)
        else:
            host = get_env("DB_HOST")
            user = get_env("DB_USER")
            password = get_env("DB_PASSWORD")
            dbname = get_env("DB_NAME")
            port = get_env("DB_PORT", "5432")
            if not all([host, user, password, dbname]):
                return (False, "Variáveis DB_HOST/DB_USER/DB_PASSWORD/DB_NAME ausentes")
            conn = psycopg2.connect(host=host, user=user, password=password, dbname=dbname, port=int(port))

        cur = conn.cursor()
        cur.execute("SELECT 1")
        _ = cur.fetchone()
        cur.close()
        return (True, "Conexão PostgreSQL OK (SELECT 1)")
    except Exception as e:
        return (False, f"Erro PostgreSQL: {e}")
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass


def main() -> int:
    load_dotenv()

    # Configuração
    timezone = get_env("TIMEZONE", "America/Sao_Paulo")
    telegram_token = get_env("TELEGRAM_BOT_TOKEN")
    telegram_chat_id = get_env("TELEGRAM_CHAT_ID")
    send_telegram = get_env("DIAGNOSTIC_SEND_TELEGRAM", "false").lower() in ("1", "true", "yes")
    http_test_url = get_env("HTTP_TEST_URL", "https://api.telegram.org")
    pg_dsn = get_env("POSTGRES_DSN")

    # Fallback automático: carregar de railway_env_commands.txt e accounts.json, se ausentes
    try:
        def is_placeholder_token(v: Optional[str]) -> bool:
            return (not v) or (v.strip().lower() in {"your_telegram_bot_token"}) or (":" not in v)

        def is_placeholder_chat(v: Optional[str]) -> bool:
            if (not v) or (v.strip().lower() in {"your_chat_id"}):
                return True
            return not re.match(r"^-?\d+$", v.strip())

        def is_placeholder_dsn(v: Optional[str]) -> bool:
            return (not v) or ("@host:" in v) or ("@host" in v) or ("user:password@host" in v)

        # Sempre tentar carregar de railway_env_commands.txt se existir (fonte canônica no projeto)
        base_dir = Path(__file__).resolve().parents[1]
        env_cmds_path = base_dir / "railway_env_commands.txt"
        accounts_path = base_dir / "accounts.json"

        if env_cmds_path.exists():
            try:
                print(f"[fallback] Lendo credenciais de: {env_cmds_path}")
            except Exception:
                pass
            content = env_cmds_path.read_text(encoding="utf-8", errors="ignore")
            m_token = re.search(r'railway\s+variables\s+set\s+TELEGRAM_BOT_TOKEN\s*"([^"]+)"', content)
            m_chat = re.search(r'railway\s+variables\s+set\s+TELEGRAM_CHAT_ID\s*"([^"]+)"', content)
            m_dsn = re.search(r'railway\s+variables\s+set\s+POSTGRES_DSN\s*"([^"]+)"', content)

            if m_token:
                telegram_token = m_token.group(1)
                os.environ["TELEGRAM_BOT_TOKEN"] = telegram_token
                print("[fallback] TELEGRAM_BOT_TOKEN carregado de railway_env_commands.txt")
            if m_chat:
                telegram_chat_id = m_chat.group(1)
                os.environ["TELEGRAM_CHAT_ID"] = telegram_chat_id
                print("[fallback] TELEGRAM_CHAT_ID carregado de railway_env_commands.txt")
            if m_dsn:
                pg_dsn = m_dsn.group(1)
                os.environ["POSTGRES_DSN"] = pg_dsn
                print("[fallback] POSTGRES_DSN carregado de railway_env_commands.txt")
            # Caso os padrões regex acima não tenham capturado, fazer um parse linha-a-linha
            if not (m_token and m_chat and m_dsn):
                env_map: Dict[str, str] = {}
                for line in content.splitlines():
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    prefix = "railway variables set "
                    if line.startswith(prefix):
                        rest = line[len(prefix):]
                        key, sep, value_part = rest.partition("=")
                        if sep:
                            key = key.strip()
                            value = value_part.strip().strip('"')
                            env_map[key] = value
                if "TELEGRAM_BOT_TOKEN" in env_map and not m_token:
                    telegram_token = env_map["TELEGRAM_BOT_TOKEN"]
                    os.environ["TELEGRAM_BOT_TOKEN"] = telegram_token
                    print("[fallback] TELEGRAM_BOT_TOKEN carregado de railway_env_commands.txt (map)")
                if "TELEGRAM_CHAT_ID" in env_map and not m_chat:
                    telegram_chat_id = env_map["TELEGRAM_CHAT_ID"]
                    os.environ["TELEGRAM_CHAT_ID"] = telegram_chat_id
                    print("[fallback] TELEGRAM_CHAT_ID carregado de railway_env_commands.txt (map)")
                if "POSTGRES_DSN" in env_map and not m_dsn:
                    pg_dsn = env_map["POSTGRES_DSN"]
                    os.environ["POSTGRES_DSN"] = pg_dsn
                    print("[fallback] POSTGRES_DSN carregado de railway_env_commands.txt (map)")

        # Se ainda faltar token/chat, tentar accounts.json
        if (is_placeholder_token(telegram_token) or is_placeholder_chat(telegram_chat_id)) and accounts_path.exists():
            import json
            try:
                accounts = json.loads(accounts_path.read_text(encoding="utf-8"))
                # Usar a primeira conta que tenha ambos os campos
                for acc in accounts if isinstance(accounts, list) else [accounts]:
                    tok = acc.get("telegram_bot_token")
                    cid = acc.get("telegram_chat_id")
                    if tok and cid:
                        if is_placeholder_token(telegram_token):
                            telegram_token = tok
                            os.environ["TELEGRAM_BOT_TOKEN"] = telegram_token
                            print("[fallback] TELEGRAM_BOT_TOKEN carregado de accounts.json")
                        if is_placeholder_chat(telegram_chat_id):
                            telegram_chat_id = cid
                            os.environ["TELEGRAM_CHAT_ID"] = telegram_chat_id
                            print("[fallback] TELEGRAM_CHAT_ID carregado de accounts.json")
                        break
            except Exception:
                pass
    except Exception:
        # Falha de fallback não impede diagnóstico
        pass

    required_env = [
        "TIMEZONE",
        # Telegram é opcional se DIAGNOSTIC_SEND_TELEGRAM=false
        # Quando true, exigimos token e chat_id
    ]

    missing = check_env_vars(required_env)
    if send_telegram:
        for v in ("TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"):
            if not os.getenv(v):
                missing.append(v)

    results: Dict[str, Tuple[bool, str]] = {}

    # 1) Verificação HTTP básica
    results["http"] = check_http_endpoint(http_test_url)

    # 2) Verificação Telegram
    results["telegram"] = check_telegram(telegram_token, telegram_chat_id, send_telegram)

    # 3) Verificação PostgreSQL
    results["postgres"] = check_postgres(pg_dsn)

    # Resumo
    print("=== Diagnóstico do Sistema ===")
    print(f"Timezone: {timezone}")
    print(f"Env ausentes: {', '.join(missing) if missing else 'nenhuma'}")

    for key, (ok, msg) in results.items():
        status = "OK" if ok else "FALHA"
        print(f"[{key}] {status} - {msg}")

    failed = any(not ok for ok, _ in results.values())
    if missing:
        failed = True

    if failed:
        print("Diagnóstico encontrou problemas. Verifique mensagens acima e .env.")
        return 1
    else:
        print("Diagnóstico concluído sem problemas.")
        return 0


if __name__ == "__main__":
    sys.exit(main())