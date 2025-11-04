#!/usr/bin/env python3
"""
Dry-run direto de generate_and_publish para Stories com publicação simulada.

Este script patcha clientes externos (OpenAI, Instagram, Telegram, Uploaders, etc.)
para evitar chamadas reais e valida o fluxo completo com logs por etapa.
"""

import os
import sys
import json
import tempfile
from contextlib import contextmanager

sys.path.append(os.path.join(os.path.dirname(__file__), ''))

from src.pipeline.generate_and_publish import generate_and_publish  # noqa: E402

from unittest.mock import patch


# ====== Fakes ======
class FakeOpenAIClient:
    def __init__(self, key=None):
        self.key = key

    def describe_image(self, url, custom_prompt=None):
        return "Descrição simulada técnica da imagem para validação."

    def generate_content_from_prompt(self, prompt):
        return "Conteúdo curto simulado sobre manutenção residencial e qualidade de serviço."

    def generate_caption(self, description, style=None):
        return "Legenda simulada: serviço disponível hoje. #Qualidade #Atendimento"

    def generate_caption_with_prompt(self, enhanced_prompt):
        return "Legenda simulada via prompt com hashtags dinâmicas. #Serviço #Urgência #Profissional"


class FakeReplicateClient:
    def __init__(self, token=None):
        self.token = token

    def generate_image(self, prompt):
        # Não será chamado pois usamos disable_replicate=True
        return "https://example.com/fake-generated.jpg"


class FakeInstagramClient:
    def __init__(self, business_id, access_token):
        self.business_id = business_id
        self.access_token = access_token

    def prepare_media(self, image_url, caption):
        print(f"[FAKE Instagram] prepare_media url={image_url} caption_len={len(caption)}")
        return "FAKE_CREATION_ID"

    def poll_media_status(self, creation_id):
        print(f"[FAKE Instagram] poll_media_status id={creation_id}")
        return "FINISHED"

    def publish_media(self, creation_id):
        print(f"[FAKE Instagram] publish_media id={creation_id}")
        return "FAKE_MEDIA_ID_123"

    def poll_published_status(self, media_id):
        print(f"[FAKE Instagram] poll_published_status id={media_id}")
        return "PUBLISHED"

    def publish_to_stories_complete(self, stories_image_url):
        print(f"[FAKE Instagram] publish_to_stories_complete url={stories_image_url}")
        return {"success": True, "media_id": "FAKE_STORY_ID_456"}


class FakeTelegramClient:
    def __init__(self, bot_token=None, chat_id=None):
        self.bot_token = bot_token
        self.chat_id = chat_id

    def send_message(self, message):
        print(f"[FAKE Telegram] {message}")
        return True


class FakePublicUploader:
    def upload_from_url(self, url):
        print(f"[FAKE PublicUploader] upload_from_url {url}")
        return "https://example.com/fake-public.jpg"

    def upload_from_file(self, file_path):
        print(f"[FAKE PublicUploader] upload_from_file {file_path}")
        return "https://example.com/fake-public.jpg"


class FakeSupabaseUploader:
    def __init__(self, url, key, bucket):
        self.url = url
        self.key = key
        self.bucket = bucket

    def upload_from_url(self, url, force_jpeg=False):
        print(f"[FAKE SupabaseUploader] upload_from_url {url} force_jpeg={force_jpeg}")
        return "https://example.com/fake-supa.jpg"

    def upload_from_file(self, file_path, force_jpeg=False):
        print(f"[FAKE SupabaseUploader] upload_from_file {file_path} force_jpeg={force_jpeg}")
        return "https://example.com/fake-supa.jpg"


class FakeStoriesImageProcessor:
    def generate_short_catchphrase(self, description, caption):
        return "Serviço técnico disponível hoje!"

    def process_and_save_for_stories_with_text(self, image_url, text=None, background_type="gradient", text_position="auto"):
        # Criar imagem temporária local sem baixar nada
        from PIL import Image, ImageDraw
        fd, tmp_path = tempfile.mkstemp(suffix=".jpg")
        os.close(fd)
        img = Image.new("RGB", (1080, 1920), color=(20, 20, 30))
        draw = ImageDraw.Draw(img)
        draw.text((40, 40), (text or ""), fill=(240, 240, 240))
        img.save(tmp_path, format="JPEG")
        print(f"[FAKE StoriesImageProcessor] saved temp stories image at {tmp_path}")
        return tmp_path

    def cleanup_temp_file(self, file_path):
        try:
            os.remove(file_path)
            print(f"[FAKE StoriesImageProcessor] cleaned {file_path}")
        except Exception:
            pass


class FakeConsistencyManager:
    def compute_image_hash(self, image_url):
        return "FAKEHASH"

    def check_image_duplication(self, image_hash):
        return {"has_duplicate": False}

    def validate_post_quality(self, post_data):
        return {"score": 0.95}

    def register_post(self, post_data, score):
        print(f"[FAKE Consistency] register_post score={score}")


@contextmanager
def dry_run_patches():
    """Context manager aplicando patches nos símbolos usados dentro de generate_and_publish."""
    with patch("src.pipeline.generate_and_publish.OpenAIClient", FakeOpenAIClient), \
         patch("src.pipeline.generate_and_publish.ReplicateClient", FakeReplicateClient), \
         patch("src.pipeline.generate_and_publish.InstagramClient", FakeInstagramClient), \
         patch("src.pipeline.generate_and_publish.TelegramClient", FakeTelegramClient), \
         patch("src.pipeline.generate_and_publish.PublicUploader", FakePublicUploader), \
         patch("src.pipeline.generate_and_publish.SupabaseUploader", FakeSupabaseUploader), \
         patch("src.pipeline.generate_and_publish.StoriesImageProcessor", FakeStoriesImageProcessor), \
         patch("src.pipeline.generate_and_publish.ConsistencyManager", FakeConsistencyManager):
        yield


def main():
    print("=" * 70)
    print("🧪 DRY-RUN: generate_and_publish para Stories (simulado)")
    print("=" * 70)

    params = {
        "openai_key": None,
        "replicate_token": None,
        "instagram_business_id": "FAKE_BUSINESS",
        "instagram_access_token": "DRY_RUN_TOKEN",
        "telegram_bot_token": "FAKE_TELEGRAM_TOKEN",
        "telegram_chat_id": "FAKE_CHAT",
        "source_image_url": "https://picsum.photos/seed/dryrun/1080/1080.jpg",
        "caption_style": "professional",
        "content_prompt": "Crie conteúdo curto sobre manutenção de ar-condicionado em residência.",
        "caption_prompt": "Escreva uma legenda envolvente baseada em {descricao} com CTA.",
        "original_text": None,
        "disable_replicate": True,
        "replicate_prompt": None,
        "account_name": "conta_teste_stories",
        "account_config": {"superior_concepts_enabled": False},
        "publish_to_stories": True,
        "stories_background_type": "gradient",
        "stories_text": "Atendemos hoje! Solicite agendamento pelo WhatsApp.",
        "stories_text_position": "auto",
        "use_weekly_themes": False,
        "force_day_of_week": None,
        "force_time_slot": None,
    }

    with dry_run_patches():
        result = generate_and_publish(**params)

    print("\nResultados:")
    print(json.dumps(result, ensure_ascii=False, indent=2))

    # Salvar relatório
    report_path = os.path.join(os.path.dirname(__file__), "stories_generate_publish_dry_run_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump({"params": params, "result": result}, f, ensure_ascii=False, indent=2)
    print(f"\n📄 Relatório salvo em: {report_path}")


if __name__ == "__main__":
    main()