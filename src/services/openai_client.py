from typing import Optional
import base64
import requests

from openai import OpenAI


class OpenAIClient:
    def __init__(self, api_key: str):
        # Cliente OpenAI v1.x
        self.client = OpenAI(api_key=api_key)

    def describe_image(self, image_url: str) -> str:
        # Tentar enviar a imagem como data URL base64 para evitar bloqueios do CDN
        def to_data_url(url: str) -> str:
            if url.startswith("data:"):
                return url
            r = requests.get(url, timeout=30)
            r.raise_for_status()
            mime = (r.headers.get("content-type") or "image/jpeg").split(";")[0]
            b64 = base64.b64encode(r.content).decode("ascii")
            return f"data:{mime};base64,{b64}"

        content = [
            {
                "type": "text",
                "text": (
                    "Descreva a imagem em português (Brasil). "
                    "Se a imagem for abstrata, descreva os elementos e as cores. "
                    "Se a imagem for concreta, descreva o objeto e o que ele representa "
                    "metaforicamente no contexto de crescimento e alta performance. "
                    "Inclua palavras-chave conceituais que conectem a composição visual ao tema de "
                    "desenvolvimento, desempenho e evolução."
                ),
            },
        ]
        try:
            data_url = to_data_url(image_url)
            content.append({"type": "image_url", "image_url": {"url": data_url}})
        except Exception:
            # Se não for possível baixar a imagem, usar uma instrução genérica
            content[0]["text"] = (
                "Descreva um visual em português (Brasil). Se a imagem não estiver acessível, "
                "infira um cenário comum e conecte-o conceitualmente a crescimento, alta performance "
                "e evolução, destacando elementos, cores e metáforas relevantes."
            )

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
        resp = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.choices[0].message.content

    def generate_caption_with_prompt(self, caption_prompt: str) -> str:
        # Usa o prompt fornecido literalmente (já com placeholders processados upstream)
        resp = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": caption_prompt}],
        )
        return resp.choices[0].message.content