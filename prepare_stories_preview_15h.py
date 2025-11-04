#!/usr/bin/env python3
"""
Gera um preview otimizado para Stories das 15h (BRT), salva localmente
e envia link via Telegram (Supabase ou fallback público) para validação.
"""

import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.stories_image_processor import StoriesImageProcessor
from services.public_uploader import PublicUploader
from services.supabase_uploader import SupabaseUploader
from services.telegram_client import TelegramClient
from config import load_config


def main():
    cfg = load_config()
    # Texto conciso para midday (15h BRT)
    text = "Cresça um pouco hoje. Pequenos passos, grandes mudanças. ✨"
    # Imagem base segura
    image_url = os.getenv("SOURCE_IMAGE_URL_DEFAULT") or cfg.get("SOURCE_IMAGE_URL_DEFAULT") or \
        "https://images.unsplash.com/photo-1506905925346-21bda4d32df4"

    print("=" * 80)
    print("🧪 PREVIEW STORIES 15H (BRT)")
    print("=" * 80)
    print(f"Imagem base: {image_url}")
    print(f"Texto: {text}")

    # Gerar arquivo de saída em backups/
    backups_dir = Path("backups")
    backups_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_name = f"stories_preview_15h_{timestamp}.jpg"
    out_path = backups_dir / out_name

    try:
        proc = StoriesImageProcessor()
        tmp_path = proc.process_and_save_for_stories_with_text(
            image_url=image_url,
            text=text,
            background_type=os.getenv("STORIES_BACKGROUND_TYPE", "gradient"),
            text_position=os.getenv("STORIES_TEXT_POSITION", "auto")
        )

        # Mover tmp para backups
        Path(tmp_path).replace(out_path)
        print(f"✅ Preview gerado: {out_path}")

        # Upload com prioridade Supabase, fallback público
        uploaded_url = None
        supa_url = cfg.get("SUPABASE_URL")
        supa_key = cfg.get("SUPABASE_SERVICE_KEY")
        supa_bkt = cfg.get("SUPABASE_BUCKET")
        try:
            if supa_url and supa_key and supa_bkt:
                uploaded_url = SupabaseUploader(supa_url, supa_key, supa_bkt).upload_from_file(
                    str(out_path), force_jpeg=True
                )
                print(f"📤 Upload Supabase: {uploaded_url}")
            else:
                uploaded_url = PublicUploader().upload_from_file(str(out_path))
                print(f"📤 Upload público: {uploaded_url}")
        except Exception as e:
            print(f"⚠️ Falha no upload: {e}")

        # Enviar para Telegram se configurado
        bot = cfg.get("TELEGRAM_BOT_TOKEN")
        chat = cfg.get("TELEGRAM_CHAT_ID")
        if bot and chat:
            try:
                msg = f"📣 Preview Stories 15h pronto!\n🔗 {uploaded_url or out_path}\n🖼️ {out_name}"
                TelegramClient(bot, chat).send_message(msg)
                print("✅ Notificação Telegram enviada")
            except Exception as e:
                print(f"⚠️ Falha ao notificar Telegram: {e}")
        else:
            print("ℹ️ Telegram não configurado; pulando notificação.")

        # Validar dimensões 1080x1920
        try:
            from PIL import Image
            with Image.open(out_path) as img:
                print(f"📐 Dimensões finais: {img.size}")
                if img.size != (1080, 1920):
                    print("⚠️ Dimensões não são 1080x1920 — verificar processor.")
                else:
                    print("✅ Dimensões corretas (1080x1920)")
        except Exception as e:
            print(f"⚠️ Não foi possível abrir imagem para validar dimensões: {e}")

    except Exception as e:
        print(f"❌ Erro ao preparar preview: {e}")


if __name__ == "__main__":
    main()