import requests
import time
import random
import os
import json
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Tuple


class RapidAPIClient:
    def __init__(self, api_key: str, host: str):
        self.host = host
        self.headers = {
            "x-rapidapi-host": host,
            "x-rapidapi-key": api_key,
        }
        self._cache: Dict[Tuple[str, str], Tuple[float, Dict[str, Any]]] = {}
        self._ttl_seconds = 1800
        # Cache em disco sob ./cache/rapidapi na raiz do projeto
        project_root = Path(__file__).resolve().parents[2]  # raiz do projeto
        self._cache_dir = project_root / "cache" / "rapidapi"
        try:
            self._cache_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass
        # Índice persistente para facilitar limpeza e inspeção
        self._index_path = self._cache_dir / "index.json"
        self._index: Dict[str, Dict[str, Any]] = {}
        try:
            if self._index_path.exists():
                with open(self._index_path, "r", encoding="utf-8") as f:
                    self._index = json.load(f)
        except Exception:
            self._index = {}

    def _cache_path(self, url: str, params: Dict[str, Any]) -> Path:
        key_str = url + "|" + ",".join([f"{k}={params[k]}" for k in sorted(params.keys())])
        digest = hashlib.sha1(key_str.encode("utf-8")).hexdigest()
        return self._cache_dir / f"{digest}.json"

    def _get_with_backoff(self, url: str, params: Dict[str, Any], ttl_seconds: int | None = None) -> Dict[str, Any]:
        key = (url, str(params))
        now = time.time()
        ttl = ttl_seconds or self._ttl_seconds
        if key in self._cache:
            ts, data = self._cache[key]
            if now - ts < ttl:
                print(f"RapidAPI cache-hit (mem): {url}")
                return data
        # Cache em disco
        disk_path = self._cache_path(url, params)
        try:
            if disk_path.exists():
                ts = disk_path.stat().st_mtime
                if now - ts < ttl:
                    print(f"RapidAPI cache-hit (disk): {disk_path.name}")
                    with open(disk_path, "r", encoding="utf-8") as f:
                        return json.load(f)
        except Exception:
            pass
        delay = 1.0
        for attempt in range(6):
            try:
                resp = requests.get(url, headers=self.headers, params=params, timeout=30)
                if resp.status_code in (429, 500, 502, 503, 504):
                    raise RuntimeError(f"HTTP {resp.status_code}")
                resp.raise_for_status()
                data = resp.json()
                self._cache[key] = (time.time(), data)
                try:
                    with open(disk_path, "w", encoding="utf-8") as f:
                        json.dump(data, f, ensure_ascii=False)
                    # Atualizar índice
                    entry = {
                        "url": url,
                        "params": params,
                        "path": disk_path.name,
                        "ts": time.time(),
                    }
                    self._index[disk_path.name] = entry
                    try:
                        with open(self._index_path, "w", encoding="utf-8") as idxf:
                            json.dump(self._index, idxf, ensure_ascii=False, indent=2)
                    except Exception:
                        pass
                except Exception:
                    pass
                return data
            except Exception as e:
                if attempt >= 5:
                    raise e
                time.sleep(delay + random.uniform(0.2, 0.6))
                delay = min(delay * 2, 20.0)

    def get_top_by_hashtag(self, hashtag: str) -> Dict[str, Any]:
        # Suportar diferentes APIs/hosts
        if "api2" in self.host:
            base_url = "https://instagram-scraper-api2.p.rapidapi.com/v1/hashtag"
            params = {"hashtag": hashtag, "feed_type": "top"}
            resp = requests.get(base_url, headers=self.headers, params=params, timeout=30)
            resp.raise_for_status()
            return resp.json()
        else:
            # Tentar múltiplos caminhos conhecidos para hosts alternativos
            candidates = [
                (f"https://{self.host}/hashtagposts/", {"hashtag": hashtag}),
                (f"https://{self.host}/hashtagposts", {"hashtag": hashtag}),
                (f"https://{self.host}/hashtag", {"hashtag": hashtag}),
                (f"https://{self.host}/v1/hashtag", {"hashtag": hashtag}),
                (f"https://{self.host}/hashtagposts/{hashtag}", {}),
                (f"https://{self.host}/hashtag/{hashtag}", {}),
            ]
            last_err = None
            for url, params in candidates:
                try:
                    # TTL mais longo para hashtags (12h)
                    data = self._get_with_backoff(url, params, ttl_seconds=43200)
                    # Log curto: URL usada e chaves do topo
                    msg = data.get("message")
                    status = data.get("status")
                    if msg or status:
                        print(f"RapidAPI OK: {url} -> status={status}, message={msg}")
                    else:
                        print(f"RapidAPI OK: {url} -> keys={list(data.keys())[:4]}")
                    return data
                except Exception as e:
                    last_err = e
                    continue
            # Se nenhuma funcionou, propagar último erro
            raise last_err or RuntimeError("RapidAPI hashtag fetch failed")

    @staticmethod
    def filter_images(data: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Tentar formato api2
        items = data.get("data", {}).get("items", [])
        tag_name = data.get("data", {}).get("additional_data", {}).get("name", "")
        if not items:
            # Tentar formato alternativo: alguns endpoints retornam lista direta
            items = (
                data.get("items")
                or data.get("results")
                or data.get("top")
                or data.get("posts")
                or (data.get("data") if isinstance(data.get("data"), list) else [])
                or []
            )
            tag_name = data.get("hashtag") or data.get("tag") or tag_name
        result: List[Dict[str, Any]] = []
        for item in items:
            is_video = item.get("is_video") or item.get("media_type") == "video"
            if not is_video:
                caption_obj = item.get("caption")
                caption = caption_obj.get("text") if isinstance(caption_obj, dict) else (caption_obj or "")
                code = item.get("code") or item.get("id") or item.get("pk") or ""
                thumb = item.get("thumbnail_url") or item.get("display_url") or item.get("image_url") or ""
                result.append({
                    "prompt": caption,
                    "content_code": code,
                    "thumbnail_url": thumb,
                    "tag": tag_name,
                })
        return result

    def get_user_posts(self, username_or_id: str) -> Dict[str, Any]:
        # Suportar hosts alternativos com endpoint userposts
        if "api2" in self.host:
            # api2 não documenta userposts; manter compatibilidade futura se necessário
            base_url = "https://instagram-scraper-api2.p.rapidapi.com/v1/userposts"
            params = {"username_or_id": username_or_id}
            resp = requests.get(base_url, headers=self.headers, params=params, timeout=30)
            resp.raise_for_status()
            return resp.json()
        else:
            candidates = [
                (f"https://{self.host}/userposts/", {"username_or_id": username_or_id}),
                (f"https://{self.host}/userposts", {"username_or_id": username_or_id}),
            ]
            last_err = None
            for url, params in candidates:
                try:
                    # TTL menor para userposts (2h)
                    data = self._get_with_backoff(url, params, ttl_seconds=7200)
                    msg = data.get("message")
                    status = data.get("status")
                    if msg or status:
                        print(f"RapidAPI OK: {url} -> status={status}, message={msg}")
                    else:
                        print(f"RapidAPI OK: {url} -> keys={list(data.keys())[:4]}")
                    return data
                except Exception as e:
                    last_err = e
                    continue
            raise last_err or RuntimeError("RapidAPI userposts fetch failed")

    def clear_cache(self, predicate: Dict[str, Any] | None = None) -> int:
        """
        Limpa arquivos de cache em disco que correspondam ao predicate.
        predicate pode conter chaves como 'url_contains', 'path', 'older_than_seconds'.
        Retorna quantidade de arquivos removidos.
        """
        removed = 0
        try:
            index = self._index
            # Recarregar índice se vazio
            if not index and self._index_path.exists():
                with open(self._index_path, "r", encoding="utf-8") as f:
                    index = json.load(f)
            for fname, meta in list(index.items()):
                ok = True
                if predicate:
                    url_contains = predicate.get("url_contains")
                    if url_contains and url_contains not in (meta.get("url") or ""):
                        ok = False
                    path_eq = predicate.get("path")
                    if path_eq and path_eq != fname:
                        ok = False
                    older = predicate.get("older_than_seconds")
                    if older and (time.time() - float(meta.get("ts", 0)) < float(older)):
                        ok = False
                if not ok:
                    continue
                try:
                    p = self._cache_dir / fname
                    if p.exists():
                        p.unlink()
                        removed += 1
                        self._index.pop(fname, None)
                except Exception:
                    pass
            # Persistir índice atualizado
            try:
                with open(self._index_path, "w", encoding="utf-8") as idxf:
                    json.dump(self._index, idxf, ensure_ascii=False, indent=2)
            except Exception:
                pass
        except Exception:
            pass
        return removed