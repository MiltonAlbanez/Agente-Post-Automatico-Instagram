import os
import logging
import requests
from typing import Dict, Any


logger = logging.getLogger(__name__)


class ReplicateClient:
    PREDICT_URL = (
        "https://api.replicate.com/v1/models/black-forest-labs/flux-schnell/predictions"
    )

    def __init__(self, token: str):
        """Inicializa cliente Replicate com validação de token.

        - Tenta usar `token` fornecido; se vazio, tenta `REPLICATE_TOKEN` do ambiente.
        - Em caso de ausência/placeholder, levanta erro com mensagem clara para falha controlada.
        """
        tok = (token or "").strip() or os.getenv("REPLICATE_TOKEN", "").strip()
        placeholder_markers = ["YOUR_", "PLACEHOLDER", "EXAMPLE", "TEMP", "REDACTED"]
        if not tok or any(m in tok for m in placeholder_markers):
            msg = (
                "REPLICATE_TOKEN ausente ou inválido. Configure a variável de ambiente REPLICATE_TOKEN "
                "ou forneça um token válido para geração de imagens."
            )
            logger.warning(msg)
            raise ValueError(msg)
        self.headers = {"Authorization": f"Bearer {tok}"}

    def generate_image(self, prompt: str) -> str:
        payload: Dict[str, Any] = {"input": {"prompt": prompt}}
        resp = requests.post(self.PREDICT_URL, headers=self.headers, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        # Some Replicate models are async; handle both immediate and polling cases
        output = data.get("output")
        if isinstance(output, list) and output:
            return output[0]
        # If not immediately available, try polling the prediction URL
        prediction_url = data.get("urls", {}).get("get")
        if prediction_url:
            for _ in range(30):
                r = requests.get(prediction_url, headers=self.headers, timeout=30)
                r.raise_for_status()
                d = r.json()
                o = d.get("output")
                if isinstance(o, list) and o:
                    return o[0]
        raise RuntimeError("Failed to retrieve generated image URL from Replicate")