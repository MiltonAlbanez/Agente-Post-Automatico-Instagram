from typing import List

from services.rapidapi_client import RapidAPIClient
from services.db import Database


def collect_hashtags(api_key: str, host: str, dsn: str, hashtags: List[str]) -> int:
    """Coleta posts top por hashtags, filtra imagens e insere novos no DB.
    Retorna quantidade de novos itens inseridos.
    """
    rapid = RapidAPIClient(api_key, host)
    db = Database(dsn)
    inserted = 0

    for tag in hashtags:
        try:
            data = rapid.get_top_by_hashtag(tag)
        except Exception as e:
            print(f"Erro RapidAPI para hashtag '{tag}': {e}")
            data = {}
        # Diagnóstico: contar itens retornados antes do filtro
        total_raw = 0
        try:
            total_raw = len(
                data.get("data", {}).get("items", [])
                or data.get("items")
                or data.get("results")
                or []
            )
        except Exception:
            pass
        items = RapidAPIClient.filter_images(data)
        print(f"Hashtag '{tag}': bruto={total_raw}, imagens={len(items)}")
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
    rapid = RapidAPIClient(api_key, host)
    db = Database(dsn)
    inserted = 0

    for user in usernames:
        try:
            data = rapid.get_user_posts(user)
        except Exception as e:
            print(f"Erro RapidAPI para usuário '{user}': {e}")
            data = {}
        total_raw = 0
        try:
            total_raw = len(
                data.get("data", {}).get("items", [])
                or data.get("items")
                or data.get("results")
                or []
            )
        except Exception:
            pass
        items = RapidAPIClient.filter_images(data)
        print(f"User '{user}': bruto={total_raw}, imagens={len(items)}")
        for item in items:
            if not item.get("tag"):
                item["tag"] = user
            if not db.exists_code(item["content_code"]):
                db.insert_trend(item)
                inserted += 1
    return inserted