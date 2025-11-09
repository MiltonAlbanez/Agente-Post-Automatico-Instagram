import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv
from typing import Optional


def _strip_newlines_and_whitespace(value: str | None) -> str:
    if value is None:
        return ""
    # Remove CR/LF e espaços extras
    return value.replace("\r", "").strip()


def _env_value_or_file(name: str, default: str = "") -> str:
    """Obtém o valor da variável de ambiente `name`.
    Se o valor parecer ser um caminho de arquivo e o arquivo existir,
    lê o conteúdo do arquivo e retorna seu conteúdo sanitizado.

    Isso torna o código compatível com ambientes que montam secrets
    como arquivos (ex.: Railway), enquanto também funciona com
    variáveis de ambiente comuns em texto.
    """
    val = os.getenv(name)
    if not val:
        return default
    val = _strip_newlines_and_whitespace(val)
    try:
        # Se for um caminho absoluto/relativo e o arquivo existir, ler conteúdo
        if (val.startswith("/") or val.startswith(".\") or val.startswith(".//") or 
            val.startswith("\\") or "/" in val or "\\" in val) and os.path.isfile(val):
            with open(val, "r", encoding="utf-8") as f:
                file_content = f.read()
            return _strip_newlines_and_whitespace(file_content)
    except Exception:
        # Em caso de qualquer falha, retorna o valor em memória
        return val
    return val


def _sanitize_env_in_place() -> dict:
    """Sanitiza o ambiente de execução:
    - Remove sufixo "\n" de nomes de chaves acidentais
    - Aplica strip() aos valores para remover "\n" finais
    - Promove aliases para chaves canônicas
    Retorna um dicionário com as chaves saneadas para logging/diagnóstico.
    """
    canonical_map = {
        # RapidAPI
        "RAPIDAPI_KEY": ["RAPIDAPI_KEY", "RAPIDAPI_KEY\n"],
        "RAPIDAPI_HOST": ["RAPIDAPI_HOST", "RAPIDAPI_HOST\n"],
        "RAPIDAPI_ALT_HOSTS": ["RAPIDAPI_ALT_HOSTS", "RAPIDAPI_ALT_HOSTS\n"],
        # Instagram / Telegram
        "INSTAGRAM_ACCESS_TOKEN": ["INSTAGRAM_ACCESS_TOKEN", "INSTAGRAM_ACCESS_TOKEN\n"],
        "INSTAGRAM_BUSINESS_ACCOUNT_ID": ["INSTAGRAM_BUSINESS_ACCOUNT_ID", "INSTAGRAM_BUSINESS_ACCOUNT_ID\n"],
        "TELEGRAM_BOT_TOKEN": ["TELEGRAM_BOT_TOKEN", "TELEGRAM_BOT_TOKEN\n"],
        "TELEGRAM_CHAT_ID": ["TELEGRAM_CHAT_ID", "TELEGRAM_CHAT_ID\n"],
        # OpenAI / Replicate
        "OPENAI_API_KEY": ["OPENAI_API_KEY", "OPENAI_API_KEY\n"],
        "REPLICATE_TOKEN": ["REPLICATE_TOKEN", "REPLICATE_TOKEN\n"],
        # Banco de dados
        "DATABASE_URL": ["DATABASE_URL", "DATABASE_URL\n", "POSTGRES_DSN", "POSTGRES_DSN\n", "SUPABASE_DB_URL", "SUPABASE_DB_URL\n"],
        # Supabase
        "SUPABASE_URL": ["SUPABASE_URL", "SUPABASE_URL\n"],
        "SUPABASE_SERVICE_KEY": ["SUPABASE_SERVICE_KEY", "SUPABASE_SERVICE_KEY\n"],
        "SUPABASE_ANON_KEY": ["SUPABASE_ANON_KEY", "SUPABASE_ANON_KEY\n"],
        "SUPABASE_BUCKET": ["SUPABASE_BUCKET", "SUPABASE_BUCKET\n"],
        "SUPABASE_PROJECT_REF": ["SUPABASE_PROJECT_REF", "SUPABASE_PROJECT_REF\n"],
        # Diversos
        "TZ": ["TZ"],
    }

    sanitized = {}
    # Primeiro, normalizar quaisquer chaves que terminem com \n genéricas
    keys_with_newline = [k for k in list(os.environ.keys()) if k.endswith("\n")]
    for k in keys_with_newline:
        v = _strip_newlines_and_whitespace(os.environ.get(k))
        k_clean = k.rstrip("\n")
        # Promover para chave sem sufixo, se não existir ou estiver vazia
        if not os.environ.get(k_clean):
            os.environ[k_clean] = v
        # Remover chave suja do processo para evitar leituras futuras
        os.environ.pop(k, None)

    # Em seguida, aplicar o mapa canônico
    for canonical, aliases in canonical_map.items():
        chosen_value = ""
        for alias in aliases:
            if alias in os.environ and _strip_newlines_and_whitespace(os.environ.get(alias)):
                chosen_value = _strip_newlines_and_whitespace(os.environ.get(alias))
                break
        if chosen_value:
            os.environ[canonical] = chosen_value
            sanitized[canonical] = chosen_value

    # Pós-processamento específico: corrigir valores problemáticos
    try:
        # OPENAI_API_KEY: remover '=' inicial e espaços extras
        if os.environ.get("OPENAI_API_KEY"):
            v = os.environ.get("OPENAI_API_KEY", "").strip()
            if v.startswith("="):
                v = v[1:].strip()
            # Remover aspas acidentais
            if (v.startswith("\"") and v.endswith("\"")) or (v.startswith("'") and v.endswith("'")):
                v = v[1:-1].strip()
            os.environ["OPENAI_API_KEY"] = v
            sanitized["OPENAI_API_KEY"] = v
    except Exception:
        pass

    try:
        # SUPABASE_URL: remover '=' inicial, garantir https:// e remover pontuação final
        if os.environ.get("SUPABASE_URL"):
            u = os.environ.get("SUPABASE_URL", "").strip()
            if u.startswith("="):
                u = u[1:].strip()
            # Normalizar protocolo
            if not u.startswith(("http://", "https://")):
                if u.startswith("//"):
                    u = "https:" + u
                else:
                    u = "https://" + u
            # Remover barra/ponto finais supérfluos
            u = u.rstrip("./ ")
            os.environ["SUPABASE_URL"] = u
            sanitized["SUPABASE_URL"] = u
    except Exception:
        pass

    # Por fim, fazer strip em todos os valores remanescentes
    for k in list(os.environ.keys()):
        os.environ[k] = _strip_newlines_and_whitespace(os.environ.get(k))

    return sanitized


def init_runtime_monitoring():
    """Configura logging com timestamp e flush imediato em stdout."""
    try:
        # Garantir flush imediato
        os.environ.setdefault("PYTHONUNBUFFERED", "1")
        try:
            sys.stdout.reconfigure(line_buffering=True)
        except Exception:
            pass
        logging.basicConfig(
            level=logging.INFO,
            format="[%(asctime)s] %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            force=True,
        )
        logging.info("Runtime monitoring inicializado")
    except Exception:
        # fallback silencioso
        pass


def perform_preflight_checks(cfg: dict) -> bool:
    """Verificações essenciais antes da postagem das 19h.
    - Tokens presentes e com formato esperado
    - DSN do banco resolvido
    Retorna True se tudo parece OK; caso contrário, loga avisos e retorna False.
    """
    ok = True
    def _safe(s: str | None, n: int = 10):
        s = s or ""
        return (s[:n] + "...") if s else "VAZIO"

    ia_token = cfg.get("INSTAGRAM_ACCESS_TOKEN")
    ia_ok = bool(ia_token) and ia_token.startswith("EAA")
    logging.info(f"Instagram token: {'OK' if ia_ok else 'FALHO'} ({_safe(ia_token)})")
    ok = ok and ia_ok

    tg_token = cfg.get("TELEGRAM_BOT_TOKEN")
    tg_ok = bool(tg_token) and (":" in tg_token)
    logging.info(f"Telegram token: {'OK' if tg_ok else 'FALHO'} ({_safe(tg_token)})")
    ok = ok and tg_ok

    sup_url = cfg.get("SUPABASE_URL")
    sup_key = cfg.get("SUPABASE_SERVICE_KEY")
    sup_bkt = cfg.get("SUPABASE_BUCKET")
    sup_ok = bool(sup_url) and sup_url.startswith("http") and bool(sup_key) and bool(sup_bkt)
    logging.info(f"Supabase: {'OK' if sup_ok else 'FALHO'} (url={_safe(sup_url, 20)}, bucket={sup_bkt or 'VAZIO'})")
    ok = ok and sup_ok

    dsn = cfg.get("POSTGRES_DSN")
    dsn_ok = bool(dsn)
    logging.info(f"Postgres DSN: {'OK' if dsn_ok else 'FALHO'} ({_safe(dsn, 25)})")
    ok = ok and dsn_ok

    return ok


def load_config():
    load_dotenv()
    # Sanitizar variáveis em memória (corrige sufixo "\n" e valores com quebra de linha)
    sanitized = _sanitize_env_in_place()
    if sanitized:
        logging.info(f"Variáveis sanitizadas: {', '.join(sorted(sanitized.keys()))}")

    # Suporte ao Railway: preferir DATABASE_URL quando disponível
    postgres_dsn = (
        os.getenv("DATABASE_URL")
        or os.getenv("POSTGRES_DSN")
        or os.getenv("SUPABASE_DB_URL")
        or ""
    )

    # Se DATABASE_URL contém endereço interno do Railway, usar DATABASE_PUBLIC_URL para testes locais
    if postgres_dsn and "railway.internal" in postgres_dsn:
        public_dsn = os.getenv("DATABASE_PUBLIC_URL")
        if public_dsn:
            postgres_dsn = public_dsn

    return {
        "INSTAGRAM_BUSINESS_ACCOUNT_ID": _env_value_or_file("INSTAGRAM_BUSINESS_ACCOUNT_ID", ""),
        "INSTAGRAM_ACCESS_TOKEN": _env_value_or_file("INSTAGRAM_ACCESS_TOKEN", ""),
        "TELEGRAM_CHAT_ID": _env_value_or_file("TELEGRAM_CHAT_ID", ""),
        "TELEGRAM_BOT_TOKEN": _env_value_or_file("TELEGRAM_BOT_TOKEN", ""),
        "RAPIDAPI_KEY": _env_value_or_file("RAPIDAPI_KEY", ""),
        "RAPIDAPI_HOST": os.getenv("RAPIDAPI_HOST", "instagram-scraper-api2.p.rapidapi.com"),
        "RAPIDAPI_ALT_HOSTS": _env_value_or_file("RAPIDAPI_ALT_HOSTS", ""),
        "REPLICATE_TOKEN": _env_value_or_file("REPLICATE_TOKEN", ""),
        "OPENAI_API_KEY": _env_value_or_file("OPENAI_API_KEY", ""),
        "POSTGRES_DSN": postgres_dsn,
        # Supabase Storage (compatível com secrets montados como arquivos)
        "SUPABASE_URL": _env_value_or_file("SUPABASE_URL", ""),
        "SUPABASE_SERVICE_KEY": _env_value_or_file("SUPABASE_SERVICE_KEY", ""),
        "SUPABASE_BUCKET": _env_value_or_file("SUPABASE_BUCKET", ""),
        # Observability
        "TZ": os.getenv("TZ", "America/Sao_Paulo"),
    }