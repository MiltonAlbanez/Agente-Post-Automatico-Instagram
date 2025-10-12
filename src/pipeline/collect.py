from typing import List
import os

from services.rapidapi_client import RapidAPIClient
from services.db import Database


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
        for current_host in hosts_order:
            try:
                rapid = RapidAPIClient(api_key, current_host)
                data = rapid.get_top_by_hashtag(tag)
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
                print(
                    f"Hashtag '{tag}' via host '{current_host}': bruto={total_raw}, imagens={len(items)}"
                )
                # Se retornou qualquer dado bruto ou imagens, considerar sucesso
                if total_raw > 0 or len(items) > 0:
                    break
            except Exception as e:
                last_err = e
                print(f"Erro RapidAPI no host '{current_host}' para hashtag '{tag}': {e}")
                continue

        if not items and last_err:
            print(f"Falha final para hashtag '{tag}': {last_err}")

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
                print(
                    f"User '{user}' via host '{current_host}': bruto={total_raw}, imagens={len(items)}"
                )
                if total_raw > 0 or len(items) > 0:
                    break
            except Exception as e:
                last_err = e
                print(f"Erro RapidAPI no host '{current_host}' para usuário '{user}': {e}")
                continue

        if not items and last_err:
            print(f"Falha final para usuário '{user}': {last_err}")

        for item in items:
            if not item.get("tag"):
                item["tag"] = user
            if not db.exists_code(item["content_code"]):
                db.insert_trend(item)
                inserted += 1
    return inserted