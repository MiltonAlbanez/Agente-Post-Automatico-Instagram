import time
import requests
from typing import Optional
import logging
from datetime import datetime

class InstagramClientRobust:
    """Cliente Instagram robusto com timeouts aumentados e retry automático"""
    BASE = "https://graph.facebook.com/v20.0"

    def __init__(self, business_account_id: str, access_token: str):
        self.business_account_id = business_account_id
        self.access_token = access_token
        self.logger = logging.getLogger(__name__)

    def _make_request_with_retry(self, method: str, url: str, params: dict, max_retries: int = 3, timeout: int = 120) -> requests.Response:
        """Faz requisição com retry automático para falhas temporárias"""
        for attempt in range(max_retries):
            try:
                if method.upper() == 'POST':
                    resp = requests.post(url, params=params, timeout=timeout)
                else:
                    resp = requests.get(url, params=params, timeout=timeout)
                
                if resp.ok:
                    return resp
                
                if resp.status_code in [429, 500, 502, 503, 504] and attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 30
                    self.logger.warning(f"Erro {resp.status_code}, tentativa {attempt + 1}/{max_retries}. Aguardando {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                
                return resp
                
            except requests.exceptions.Timeout as e:
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 30
                    self.logger.warning(f"Timeout na tentativa {attempt + 1}/{max_retries}. Aguardando {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    raise e
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 30
                    self.logger.warning(f"Erro na tentativa {attempt + 1}/{max_retries}: {e}. Aguardando {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    raise e
        
        return resp

    def publish_complete_robust(self, image_url: str, caption: str) -> dict:
        """Processo completo de publicação com máxima robustez"""
        start_time = datetime.now()
        self.logger.info(f"🚀 Iniciando publicação robusta às {start_time.strftime('%H:%M:%S')}")
        
        try:
            # 1. Preparar mídia
            creation_id = self.prepare_media(image_url, caption)
            
            # 2. Aguardar processamento
            status = self.poll_media_status(creation_id)
            
            if status == "FINISHED":
                # 3. Publicar
                media_id = self.publish_media(creation_id)
                
                # 4. Verificar status final
                final_status = self.poll_published_status(media_id)
                
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                result = {
                    "creation_id": creation_id,
                    "media_id": media_id,
                    "status": final_status,
                    "success": final_status == "PUBLISHED",
                    "duration_seconds": duration
                }
                
                if final_status == "PUBLISHED":
                    self.logger.info(f"🎉 Publicação concluída com sucesso em {duration:.1f}s")
                else:
                    self.logger.error(f"❌ Publicação falhou após {duration:.1f}s: {final_status}")
                
                return result
            else:
                return {
                    "creation_id": creation_id,
                    "status": status,
                    "success": False,
                    "error": f"Media preparation failed with status: {status}"
                }
                
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            self.logger.error(f"❌ Erro na publicação após {duration:.1f}s: {e}")
            return {
                "success": False,
                "error": str(e),
                "duration_seconds": duration
            }

    def prepare_media(self, image_url: str, caption: str) -> str:
        """Prepara mídia com timeout aumentado"""
        url = f"{self.BASE}/{self.business_account_id}/media"
        params = {"image_url": image_url, "caption": caption, "access_token": self.access_token}
        
        resp = self._make_request_with_retry('POST', url, params, timeout=120)
        
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

    def poll_media_status(self, media_id: str, interval_sec: int = 10, max_checks: int = 60) -> str:
        """Verifica status com polling robusto (10 minutos total)"""
        url = f"{self.BASE}/{media_id}"
        params = {"fields": "status_code,status", "access_token": self.access_token}
        
        for check in range(max_checks):
            try:
                resp = self._make_request_with_retry('GET', url, params, timeout=60)
                
                if not resp.ok:
                    if resp.status_code in [429, 500, 502, 503, 504]:
                        time.sleep(interval_sec * 2)
                        continue
                    
                    try:
                        err = resp.json()
                    except Exception:
                        err = resp.text
                    raise RuntimeError(f"poll_media_status failed: HTTP {resp.status_code} -> {err}")
                
                data = resp.json()
                status = data.get("status_code", "")
                
                if status in ("FINISHED", "ERROR"):
                    break
                
                time.sleep(interval_sec)
                
            except Exception as e:
                if check < max_checks - 1:
                    time.sleep(interval_sec * 2)
                    continue
                else:
                    raise e
        
        return status

    def publish_media(self, creation_id: str) -> str:
        """Publica mídia com timeout aumentado"""
        url = f"{self.BASE}/{self.business_account_id}/media_publish"
        params = {"creation_id": creation_id, "access_token": self.access_token}
        
        resp = self._make_request_with_retry('POST', url, params, timeout=120)
        
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

    def poll_published_status(self, media_id: str, interval_sec: int = 10, max_checks: int = 60) -> str:
        """Verifica status de publicação com polling robusto"""
        url = f"{self.BASE}/{media_id}"
        params = {"fields": "id,permalink", "access_token": self.access_token}
        
        for check in range(max_checks):
            try:
                resp = self._make_request_with_retry('GET', url, params, timeout=60)
                
                if resp.ok:
                    data = resp.json()
                    if data.get("permalink"):
                        return "PUBLISHED"
                
                time.sleep(interval_sec)
                
            except Exception as e:
                if check < max_checks - 1:
                    time.sleep(interval_sec * 2)
                    continue
                else:
                    raise e
        
        return "PENDING"
