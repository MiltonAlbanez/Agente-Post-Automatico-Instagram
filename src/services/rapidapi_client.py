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
        
        # Rate limiting
        self._rpm_limit = int(os.getenv("RAPIDAPI_RPM", "60"))
        self._req_timestamps: List[float] = []
        
        # Logs directory
        self._logs_dir = project_root / "logs"
        try:
            self._logs_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass

    def _cache_path(self, url: str, params: Dict[str, Any]) -> Path:
        key_str = url + "|" + ",".join([f"{k}={params[k]}" for k in sorted(params.keys())])
        digest = hashlib.sha1(key_str.encode("utf-8")).hexdigest()
        return self._cache_dir / f"{digest}.json"

    def _apply_rate_limit(self) -> None:
        now = time.time()
        # remover timestamps antigos
        self._req_timestamps = [t for t in self._req_timestamps if now - t < 60]
        if len(self._req_timestamps) >= self._rpm_limit:
            # esperar até que o mais antigo saia da janela de 60s
            wait_seconds = 60 - (now - self._req_timestamps[0])
            if wait_seconds > 0:
                time.sleep(wait_seconds)
        self._req_timestamps.append(time.time())

    def _log_usage(self, url: str, status_code: int, params: Dict[str, Any]) -> None:
        try:
            log_path = self._logs_dir / "rapidapi_usage.log"
            with open(log_path, "a", encoding="utf-8") as lf:
                lf.write(json.dumps({
                    "ts": time.time(),
                    "url": url,
                    "status": status_code,
                    "params": params,
                    "host": self.host,
                }) + "\n")
        except Exception:
            pass

    def _get_with_backoff(self, url: str, params: Dict[str, Any], ttl_seconds: int | None = None, headers: Dict[str, str] | None = None) -> Dict[str, Any]:
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
        delay = 0.5
        for attempt in range(3):  # Reduzido de 6 para 3 tentativas
            try:
                # aplicar rate limit antes da requisição
                self._apply_rate_limit()
                headers_to_use = headers or self.headers
                resp = requests.get(url, headers=headers_to_use, params=params, timeout=2)  # Reduzido de 3 para 2 segundos
                if resp.status_code in (429, 500, 502, 503, 504):
                    self._log_usage(url, resp.status_code, params)
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
                # log de sucesso
                self._log_usage(url, resp.status_code, params)
                return data
            except Exception as e:
                if attempt >= 2:  # Ajustado para 3 tentativas (0,1,2)
                    raise e
                time.sleep(delay + random.uniform(0.1, 0.3))  # Delay muito menor
                delay = min(delay * 1.5, 3.0)  # Delay máximo de 3 segundos

    def get_top_by_hashtag(self, hashtag: str) -> Dict[str, Any]:
        # Suportar diferentes APIs/hosts
        if "api2" in self.host:
            base_url = "https://instagram-scraper-api2.p.rapidapi.com/v1/hashtag"
            # Tentar em ordem: 'top' e depois 'recent' se falhar (403/erro)
            attempts = [
                {"hashtag": hashtag, "feed_type": "top"},
                {"hashtag": hashtag, "feed_type": "recent"},
            ]
            last_err = None
            for params in attempts:
                try:
                    # TTL mais longo para hashtags (12h)
                    data = self._get_with_backoff(base_url, params, ttl_seconds=43200)
                    # pequeno log para diagnóstico
                    ft = params.get("feed_type")
                    keys = list(data.keys())[:4]
                    print(f"RapidAPI OK api2: feed_type={ft} -> keys={keys}")
                    return data
                except Exception as e:
                    last_err = e
                    continue
            # Se nenhuma tentativa funcionou, propagar último erro
            raise last_err or RuntimeError("RapidAPI hashtag fetch failed (api2)")
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
            # TTL menor para userposts (2h)
            data = self._get_with_backoff(base_url, params, ttl_seconds=7200)
            return data
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


    def get_post_likers(self, post_id: str | None = None, shortcode: str | None = None) -> Dict[str, Any]:
        """
        Integração com endpoint RapidAPI: GET /get_post_likers.php
        Host principal: instagram-scraper-stable-api.p.rapidapi.com (ou o configurado em RAPIDAPI_HOST)
        Parâmetros aceitos: post_id ou shortcode (pelo menos um obrigatório)
        Usa fallback via RAPIDAPI_ALT_HOSTS se configurado
        """
        if not post_id and not shortcode:
            raise ValueError("Forneça post_id ou shortcode")
        params: Dict[str, Any] = {}
        if post_id:
            params["post_id"] = post_id
        if shortcode:
            params["shortcode"] = shortcode
        # construir lista de hosts: principal + alternativos
        alt_hosts_env = os.getenv("RAPIDAPI_ALT_HOSTS", "")
        alt_hosts = [h.strip() for h in alt_hosts_env.split(",") if h.strip()]
        hosts = [self.host] + alt_hosts
        last_err: Exception | None = None
        for h in hosts:
            url = f"https://{h}/get_post_likers.php"
            # headers devem refletir o host atual
            headers_override = {
                "x-rapidapi-host": h,
                "x-rapidapi-key": self.headers.get("x-rapidapi-key", ""),
            }
            try:
                # TTL curto para likers (30 min)
                data = self._get_with_backoff(url, params, ttl_seconds=1800, headers=headers_override)
                print(f"RapidAPI OK: get_post_likers host={h} -> keys={list(data.keys())[:4]}")
                return data
            except Exception as e:
                last_err = e
                continue
        raise last_err or RuntimeError("RapidAPI get_post_likers falhou em todos os hosts")