from typing import List
import os

from ..services.rapidapi_client import RapidAPIClient
from ..services.db import Database


def collect_hashtags(api_key: str, host: str, dsn: str, hashtags: List[str]) -> int:
    """Coleta posts top por hashtags, filtra imagens e insere novos no DB.
    Retorna quantidade de novos itens inseridos.
    """
    db = Database(dsn)
    inserted = 0

    # Preparar lista de hosts: primário + alternativos via env RAPIDAPI_ALT_HOSTS
    alt_hosts_env = os.environ.get("RAPIDAPI_ALT_HOSTS", "")
    alt_hosts = [h.strip() for h in alt_hosts_env.split(",") if h.strip()]
    # Remover duplicados mantendo ordem
    seen = set()
    hosts_order: List[str] = []
    for h in [host] + alt_hosts:
        if h and h not in seen:
            hosts_order.append(h)
            seen.add(h)

    for tag in hashtags:
        # Sanitização básica: remover espaços e prefixo '#'
        try:
            tag = (tag or "").strip().lstrip("#")
        except Exception:
            pass
        if not tag:
            continue

        data = {}
        total_raw = 0
        items: List[dict] = []
        last_err: Exception | None = None

        # Tentar em cada host na ordem até obter dados
        print(f"   🔍 Tentando hashtag '{tag}' em {len(hosts_order)} hosts...")
        for i, current_host in enumerate(hosts_order, 1):
            try:
                print(f"   📡 Host {i}/{len(hosts_order)}: {current_host}")
                rapid = RapidAPIClient(api_key, current_host)
                print(f"   ⏳ Fazendo requisição para hashtag '{tag}'...")
                data = rapid.get_top_by_hashtag(tag)
                print(f"   ✅ Resposta recebida para '{tag}'")
                try:
                    total_raw = len(
                        data.get("data", {}).get("items", [])
                        or data.get("items")
                        or data.get("results")
                        or []
                    )
                except Exception:
                    total_raw = 0
                items = RapidAPIClient.filter_images(data)
                # Se retornou qualquer dado bruto ou imagens, considerar sucesso
                if total_raw > 0 or len(items) > 0:
                    print(f"   ✅ Sucesso! {total_raw} itens brutos, {len(items)} imagens filtradas")
                    break
            except Exception as e:
                error_msg = str(e)
                if "timeout" in error_msg.lower():
                    print(f"   ⏰ Timeout no host {current_host}")
                elif "403" in error_msg or "forbidden" in error_msg.lower():
                    print(f"   🚫 Acesso negado no host {current_host}")
                else:
                    print(f"   ❌ Erro no host {current_host}: {error_msg[:100]}")
                last_err = e
                continue

        if not items and last_err:
            pass

        for item in items:
            # Garantir que a tag seja preenchida mesmo se a API não retornar
            if not item.get("tag"):
                item["tag"] = tag
            if not db.exists_code(item["content_code"]):
                db.insert_trend(item)
                inserted += 1
    return inserted

def collect_userposts(api_key: str, host: str, dsn: str, usernames: List[str]) -> int:
    """Coleta posts por usuário, filtra imagens e insere novos no DB.
    Retorna quantidade de novos itens inseridos.
    """
    db = Database(dsn)
    inserted = 0

    # Preparar lista de hosts: primário + alternativos via env RAPIDAPI_ALT_HOSTS
    alt_hosts_env = os.environ.get("RAPIDAPI_ALT_HOSTS", "")
    alt_hosts = [h.strip() for h in alt_hosts_env.split(",") if h.strip()]
    seen = set()
    hosts_order: List[str] = []
    for h in [host] + alt_hosts:
        if h and h not in seen:
            hosts_order.append(h)
            seen.add(h)

    for user in usernames:
        data = {}
        total_raw = 0
        items: List[dict] = []
        last_err: Exception | None = None

        for current_host in hosts_order:
            try:
                rapid = RapidAPIClient(api_key, current_host)
                data = rapid.get_user_posts(user)
                try:
                    total_raw = len(
                        data.get("data", {}).get("items", [])
                        or data.get("items")
                        or data.get("results")
                        or []
                    )
                except Exception:
                    total_raw = 0
                items = RapidAPIClient.filter_images(data)
                if total_raw > 0 or len(items) > 0:
                    break
            except Exception as e:
                last_err = e
                continue

        if not items and last_err:
            pass

        for item in items:
            if not item.get("tag"):
                item["tag"] = user
            if not db.exists_code(item["content_code"]):
                db.insert_trend(item)
                inserted += 1
    return inserted