import os
import uuid
import requests
from urllib.parse import quote
from io import BytesIO


class SupabaseUploader:
    """
    Faz upload de imagens para Supabase Storage via API HTTP.

    Requer variáveis de ambiente:
    - SUPABASE_URL: ex. https://YOUR_REF.supabase.co
    - SUPABASE_SERVICE_KEY: chave service role (Bearer)
    - SUPABASE_BUCKET: nome do bucket

    Retorna URL pública do objeto se o bucket estiver configurado como público
    ou se houver CDN habilitado. Caso contrário, retorna a rota de objeto.
    """

    def __init__(self, url: str, service_key: str, bucket: str):
        if not url or not service_key or not bucket:
            raise ValueError("SupabaseUploader requer url, service_key e bucket")
        self.base = url.rstrip("/")
        self.token = service_key
        self.bucket = bucket
        self._bucket_checked = False

    def _headers(self, content_type: str | None = None) -> dict:
        headers = {
            "Authorization": f"Bearer {self.token}",
            # Alguns ambientes requerem apikey além do Bearer
            "apikey": self.token,
        }
        if content_type:
            headers["Content-Type"] = content_type
        return headers

    def ensure_bucket_exists(self, public: bool = True):
        """Garante que o bucket exista; cria se necessário com visibilidade pública."""
        if self._bucket_checked:
            return
        # Listar buckets e checar por nome
        url_list = f"{self.base}/storage/v1/bucket"
        resp_list = requests.get(url_list, headers=self._headers(), timeout=30)
        if not (200 <= resp_list.status_code < 300):
            resp_list.raise_for_status()
        try:
            buckets = resp_list.json()
        except Exception:
            buckets = []
        exists = any((b.get("name") == self.bucket) for b in buckets) if isinstance(buckets, list) else False
        if not exists:
            # Criar bucket
            url_create = f"{self.base}/storage/v1/bucket"
            payload = {"name": self.bucket, "public": public}
            resp_create = requests.post(url_create, headers=self._headers("application/json"), json=payload, timeout=30)
            resp_create.raise_for_status()
        self._bucket_checked = True

    def _guess_extension(self, content_type: str) -> str:
        ct = (content_type or "").lower()
        if "jpeg" in ct or "jpg" in ct:
            return "jpg"
        if "png" in ct:
            return "png"
        if "webp" in ct:
            return "webp"
        return "bin"

    def upload_from_bytes(self, data: bytes, content_type: str = "image/jpeg", filename: str | None = None) -> str:
        if not filename:
            ext = self._guess_extension(content_type)
            filename = f"auto-{uuid.uuid4().hex}.{ext}"
        # Garante que o bucket exista e seja público
        self.ensure_bucket_exists(public=True)
        # POST para criar novo objeto
        bucket_enc = quote(self.bucket.strip(), safe="")
        file_enc = quote(filename.strip(), safe="")
        url = f"{self.base}/storage/v1/object/{bucket_enc}/{file_enc}"
        headers = self._headers(content_type)
        # Permite sobrescrever caso o nome já exista
        headers["x-upsert"] = "true"
        resp = requests.post(url, headers=headers, data=data, timeout=60)
        resp.raise_for_status()
        # Construir URL pública provável
        public_url = f"{self.base}/storage/v1/object/public/{bucket_enc}/{file_enc}"
        return public_url

    def _to_jpeg_bytes(self, data: bytes) -> bytes:
        """Converte bytes de imagem para JPEG. Se falhar, retorna os bytes originais."""
        try:
            from PIL import Image  # Pillow
            img = Image.open(BytesIO(data))
            # Converter para RGB para garantir compatibilidade com JPEG
            if img.mode not in ("RGB", "L"):
                img = img.convert("RGB")
            buf = BytesIO()
            img.save(buf, format="JPEG", quality=90, optimize=True)
            return buf.getvalue()
        except Exception:
            # Falha na conversão (ex.: Pillow não instalado), usar original
            return data

    def upload_from_url(self, source_image_url: str, timeout: int = 60, force_jpeg: bool = True) -> str:
        r = requests.get(source_image_url, timeout=timeout)
        r.raise_for_status()
        content_type = r.headers.get("Content-Type", "image/jpeg")
        data = r.content
        if force_jpeg:
            converted = self._to_jpeg_bytes(data)
            if converted != data:
                data = converted
                content_type = "image/jpeg"
            else:
                # Mesmo se não converter, preferimos marcar como JPEG apenas quando de fato converteu
                pass
        return self.upload_from_bytes(data, content_type=content_type)