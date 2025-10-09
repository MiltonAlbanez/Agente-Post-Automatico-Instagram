from typing import Dict

from services.openai_client import OpenAIClient
from services.replicate_client import ReplicateClient
from services.instagram_client import InstagramClient
from services.telegram_client import TelegramClient
from services.public_uploader import PublicUploader
from services.supabase_uploader import SupabaseUploader


def generate_and_publish(
    openai_key: str,
    replicate_token: str,
    instagram_business_id: str,
    instagram_access_token: str,
    telegram_bot_token: str,
    telegram_chat_id: str,
    source_image_url: str,
    caption_style: str | None = None,
    content_prompt: str | None = None,
    caption_prompt: str | None = None,
    original_text: str | None = None,
    disable_replicate: bool = False,
    # Overrides opcionais de Supabase por conta (multirun)
    supabase_url: str | None = None,
    supabase_service_key: str | None = None,
    supabase_bucket: str | None = None,
):
    # Inicializa clientes
    openai = OpenAIClient(openai_key)

    # Primeiro, decidir qual imagem será usada (Replicate ou original re-hospedada)
    generated_image_url = source_image_url
    replicate_error = None
    if not disable_replicate:
        replicate = ReplicateClient(replicate_token)
        base_prompt = content_prompt or "Renderização isométrica 3D altamente detalhada."
        try:
            generated_image_url = replicate.generate_image(prompt=f"{base_prompt} {description}")
        except Exception as e:
            print(f"Replicate falhou, usando imagem original. Erro: {e}")
            replicate_error = str(e)
            generated_image_url = source_image_url
    else:
        replicate_error = "DISABLED"

    # Sempre re-hospedar a imagem final (gerada ou original) no Supabase como JPEG, com fallback público
    try:
        # Preferir overrides fornecidos pela chamada; senão, carregar de config
        supa_url = supabase_url
        supa_key = supabase_service_key
        supa_bkt = supabase_bucket
        if not (supa_url and supa_key and supa_bkt):
            from config import load_config
            cfg = load_config()
            supa_url = supa_url or cfg.get("SUPABASE_URL")
            supa_key = supa_key or cfg.get("SUPABASE_SERVICE_KEY")
            supa_bkt = supa_bkt or cfg.get("SUPABASE_BUCKET")
        if supa_url and supa_key and supa_bkt:
            try:
                hosted_url = SupabaseUploader(supa_url, supa_key, supa_bkt).upload_from_url(
                    generated_image_url, force_jpeg=True
                )
                print(f"Imagem re-hosted via Supabase: {hosted_url}")
                generated_image_url = hosted_url
            except Exception as sup_err:
                print(f"Supabase upload falhou: {sup_err}")
                try:
                    hosted_public = PublicUploader().upload_from_url(generated_image_url)
                    print(f"Imagem re-hosted via público: {hosted_public}")
                    generated_image_url = hosted_public
                except Exception as up_err:
                    print(f"Fallback de upload público falhou: {up_err}")
        else:
            print("Supabase não configurado. Usando re-host público.")
            try:
                hosted_public = PublicUploader().upload_from_url(generated_image_url)
                print(f"Imagem re-hosted via público: {hosted_public}")
                generated_image_url = hosted_public
            except Exception as up_err:
                print(f"Fallback de upload público falhou: {up_err}")
    except Exception as cfg_err:
        print(f"Erro carregando/avaliando config Supabase: {cfg_err}")

    # Descrever a imagem final e gerar a legenda com base nela
    description = openai.describe_image(generated_image_url)
    if caption_prompt:
        # Suporte a placeholders {descricao} e {texto_original}
        prompt_text = caption_prompt.replace("{descricao}", description)
        if original_text:
            prompt_text = prompt_text.replace("{texto_original}", original_text)
        # Quando o prompt for definido pela conta, usar literal
        caption = openai.generate_caption_with_prompt(prompt_text)
    else:
        caption = openai.generate_caption(description, caption_style)

    # Preparar e publicar no Instagram
    instagram = InstagramClient(instagram_business_id, instagram_access_token)
    # Validação básica do token do Instagram: evitar credenciais de login equivocadas
    invalid_token_markers = [" ", "@", "login:"]
    if any(m in instagram_access_token for m in invalid_token_markers) or not instagram_access_token:
        return {
            "description": description,
            "caption": caption,
            "generated_image_url": generated_image_url,
            "status": "ERROR",
            "error": "INSTAGRAM_ACCESS_TOKEN inválido. Use um token da Graph API (EAA...).",
            "replicate_error": replicate_error,
        }
    try:
        creation_id = instagram.prepare_media(generated_image_url, caption)
        status = instagram.poll_media_status(creation_id)
        if status == "FINISHED":
            media_id = instagram.publish_media(creation_id)
            final_status = instagram.poll_published_status(media_id)
            try:
                if final_status == "PUBLISHED":
                    TelegramClient(telegram_bot_token, telegram_chat_id).send_message("Instagram content is shared")
                else:
                    TelegramClient(telegram_bot_token, telegram_chat_id).send_message(
                        f"Instagram content publish status: {final_status}"
                    )
            except Exception:
                pass
            return {
                "description": description,
                "caption": caption,
                "generated_image_url": generated_image_url,
                "creation_id": creation_id,
                "media_id": media_id,
                "status": final_status,
                "replicate_error": replicate_error,
            }
        else:
            try:
                TelegramClient(telegram_bot_token, telegram_chat_id).send_message(
                    f"Instagram content failed with status: {status}"
                )
            except Exception:
                pass
            return {
                "description": description,
                "caption": caption,
                "generated_image_url": generated_image_url,
                "creation_id": creation_id,
                "status": status,
                "replicate_error": replicate_error,
            }
    except Exception as e:
        # Erro ao preparar/publicar no Instagram
        try:
            TelegramClient(telegram_bot_token, telegram_chat_id).send_message(
                f"Instagram publish error: {e}"
            )
        except Exception:
            pass
        return {
            "description": description,
            "caption": caption,
            "generated_image_url": generated_image_url,
            "status": "ERROR",
            "error": str(e),
            "replicate_error": replicate_error,
        }