import time
import requests
from typing import Optional


class InstagramClient:
    # Publicação via Instagram Graph API é feita no domínio do Facebook Graph
    BASE = "https://graph.facebook.com/v20.0"

    def __init__(self, business_account_id: str, access_token: str):
        self.business_account_id = business_account_id
        self.access_token = access_token

    def prepare_media(self, image_url: str, caption: str) -> str:
        url = f"{self.BASE}/{self.business_account_id}/media"
        params = {"image_url": image_url, "caption": caption, "access_token": self.access_token}
        resp = requests.post(url, params=params, timeout=30)
        if not resp.ok:
            try:
                err = resp.json()
            except Exception:
                err = resp.text
            raise RuntimeError(f"prepare_media failed: HTTP {resp.status_code} -> {err}")
        data = resp.json()
        if "id" not in data:
            raise RuntimeError(f"Failed to prepare media: {data}")
        return data["id"]

    def poll_media_status(self, media_id: str, interval_sec: int = 5, max_checks: int = 24) -> str:
        url = f"{self.BASE}/{media_id}"
        params = {"fields": "status_code,status", "access_token": self.access_token}
        status = ""
        for _ in range(max_checks):
            resp = requests.get(url, params=params, timeout=30)
            if not resp.ok:
                try:
                    err = resp.json()
                except Exception:
                    err = resp.text
                raise RuntimeError(f"poll_media_status failed: HTTP {resp.status_code} -> {err}")
            data = resp.json()
            status = data.get("status_code", "")
            if status == "ERROR":
                # Retornar erro com mais contexto se disponível
                status_text = data.get("status", "ERROR")
                return f"ERROR:{status_text}"
            if status in ("FINISHED", "ERROR"):
                break
            time.sleep(interval_sec)
        return status

    def publish_media(self, creation_id: str) -> str:
        url = f"{self.BASE}/{self.business_account_id}/media_publish"
        params = {"creation_id": creation_id, "access_token": self.access_token}
        resp = requests.post(url, params=params, timeout=30)
        if not resp.ok:
            try:
                err = resp.json()
            except Exception:
                err = resp.text
            raise RuntimeError(f"publish_media failed: HTTP {resp.status_code} -> {err}")
        data = resp.json()
        if "id" not in data:
            raise RuntimeError(f"Failed to publish media: {data}")
        return data["id"]

    def poll_published_status(self, media_id: str, interval_sec: int = 5, max_checks: int = 24) -> str:
        url = f"{self.BASE}/{media_id}"
        # Em mídia publicada, o campo status_code não existe; verificar permalink
        params = {"fields": "id,permalink", "access_token": self.access_token}
        last_err = None
        for _ in range(max_checks):
            resp = requests.get(url, params=params, timeout=30)
            if resp.ok:
                data = resp.json()
                if data.get("permalink"):
                    return "PUBLISHED"
                # Se ainda não houver permalink, aguardar
            else:
                try:
                    err = resp.json()
                except Exception:
                    err = resp.text
                last_err = f"poll_published_status failed: HTTP {resp.status_code} -> {err}"
            time.sleep(interval_sec)
        if last_err:
            raise RuntimeError(last_err)
        return "PENDING"