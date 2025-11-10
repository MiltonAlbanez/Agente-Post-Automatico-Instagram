from typing import Optional
import base64
import os
import logging
import requests

from openai import OpenAI


logger = logging.getLogger(__name__)


class OpenAIClient:
    def __init__(self, api_key: str):
        """Inicializa cliente OpenAI com validação de chave.

        - Tenta usar `api_key` fornecida; se vazia, tenta `OPENAI_API_KEY` do ambiente.
        - Em caso de ausência/placeholder, desativa cliente com motivo e fornece fallbacks controlados.
        """
        key = (api_key or "").strip() or os.getenv("OPENAI_API_KEY", "").strip()
        placeholder_markers = ["YOUR_", "PLACEHOLDER", "EXAMPLE", "TEMP", "REDACTED"]
        if not key or any(m in key for m in placeholder_markers):
            self.client = None
            self._disabled_reason = (
                "OPENAI_API_KEY ausente ou inválido. Configure a variável de ambiente OPENAI_API_KEY "
                "ou passe uma chave válida para o cliente."
            )
            logger.warning(self._disabled_reason)
        else:
            # Cliente OpenAI v1.x
            self.client = OpenAI(api_key=key)
            self._disabled_reason = None

    def describe_image(self, image_url: str, custom_prompt: Optional[str] = None) -> str:
        # Tentar enviar a imagem como data URL base64 para evitar bloqueios do CDN
        def to_data_url(url: str) -> str:
            if url.startswith("data:"):
                return url
            r = requests.get(url, timeout=30)
            r.raise_for_status()
            mime = (r.headers.get("content-type") or "image/jpeg").split(";")[0]
            b64 = base64.b64encode(r.content).decode("ascii")
            return f"data:{mime};base64,{b64}"

        base_text = (
            "Descreva a imagem em português (Brasil). "
            "Se a imagem for abstrata, descreva os elementos e as cores. "
            "Se a imagem for concreta, descreva o objeto e o que ele representa "
            "metaforicamente no contexto de crescimento e alta performance. "
            "Inclua palavras-chave conceituais que conectem a composição visual ao tema de "
            "desenvolvimento, desempenho e evolução."
        )
        prompt_text = custom_prompt or base_text
        content = [
            {
                "type": "text",
                "text": prompt_text,
            },
        ]
        try:
            data_url = to_data_url(image_url)
            content.append({"type": "image_url", "image_url": {"url": data_url}})
        except Exception:
            # Se não for possível baixar a imagem, usar uma instrução genérica
            content[0]["text"] = custom_prompt or (
                "Descreva um visual em português (Brasil). Se a imagem não estiver acessível, "
                "infira um cenário comum e conecte-o conceitualmente a crescimento, alta performance "
                "e evolução, destacando elementos, cores e metáforas relevantes."
            )

        # Fallback controlado se cliente estiver desativado
        if self.client is None:
            base_fallback = (
                custom_prompt
                or "Descreva brevemente elementos visuais, cores e possível contexto de crescimento e performance."
            )
            return f"[OpenAI desativado] {base_fallback}"

        resp = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": content}],
        )
        return resp.choices[0].message.content

    def generate_caption(self, description: str, style: Optional[str] = None) -> str:
        prompt = (
            f"Resuma a seguinte descrição de conteúdo em uma legenda envolvente para Instagram, em português (Brasil). "
            f"Seja conciso, adicione emojis e hashtags relevantes quando apropriado.\n\n{description}"
        )
        if style:
            prompt += f"\nInstruções de estilo: {style}"
        if self.client is None:
            hashtags_hint = " #motivacao #crescimento #performance"
            return (
                f"[OpenAI desativado] Legenda baseada na descrição: {description[:120]}..."
                f"{hashtags_hint}"
            )
        resp = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.choices[0].message.content

    def generate_caption_with_prompt(self, caption_prompt: str) -> str:
        # Usa o prompt fornecido literalmente (já com placeholders processados upstream)
        if self.client is None:
            return f"[OpenAI desativado] {caption_prompt[:200]}"
        resp = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": caption_prompt}],
        )
        return resp.choices[0].message.content

    def generate_content_from_prompt(self, content_prompt: str) -> str:
        """
        Gera conteúdo inicial baseado em um prompt personalizado.
        Este método é usado no novo fluxo texto-primeiro.
        """
        if self.client is None:
            return f"[OpenAI desativado] {content_prompt[:200]}"
        resp = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": content_prompt}],
        )
        return resp.choices[0].message.content