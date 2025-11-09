from typing import Dict
import random

from services.openai_client import OpenAIClient
from services.replicate_client import ReplicateClient
from services.instagram_client import InstagramClient
from services.telegram_client import TelegramClient
from services.public_uploader import PublicUploader
from services.supabase_uploader import SupabaseUploader
from services.content_format_manager import ContentFormatManager, get_format_enhanced_prompt
from services.hashtag_manager import HashtagManager
from services.performance_tracker import track_post_performance
from services.ab_testing_framework import get_ab_test_config
from services.visual_quality_manager import VisualQualityManager, get_enhanced_image_prompt
from services.superior_concept_manager import get_superior_concept_prompt
from services.stories_image_processor import StoriesImageProcessor
from services.weekly_theme_manager import WeeklyThemeManager, get_weekly_themed_content, is_morning_spiritual_time


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
    # Prompt de geração de imagem opcional, vindo da conta (override do padrão seguro)
    replicate_prompt: str | None = None,
    # Overrides opcionais de Supabase por conta (multirun)
    supabase_url: str | None = None,
    supabase_service_key: str | None = None,
    supabase_bucket: str | None = None,
    # Nome da conta para tracking de performance
    account_name: str | None = None,
    # Configurações da conta (incluindo conceitos superiores)
    account_config: Dict | None = None,
    # Publicar também no Stories (formato 9:16)
    publish_to_stories: bool = False,
    # Tipo de fundo para Stories ("gradient" ou "blurred")
    stories_background_type: str = "gradient",
    # Texto a ser adicionado nos Stories (opcional)
    stories_text: str | None = None,
    # Posição do texto nos Stories ("top", "center", "bottom")
    stories_text_position: str = "auto",
    # Sistema Temático Semanal
    use_weekly_themes: bool = True,
    force_day_of_week: int | None = None,
    force_time_slot: str | None = None,
):
    # Obter configurações de A/B testing
    ab_config = {}
    if account_name:
        try:
            ab_config = get_ab_test_config(account_name)
            # print(f"Configurações A/B aplicadas: {ab_config}")
        except Exception as e:
            # print(f"Erro ao obter configurações A/B: {e}")
            ab_config = {}
    
    # SISTEMA TEMÁTICO SEMANAL - Integração Principal
    weekly_theme_metadata = {}
    if use_weekly_themes:
        try:
            print("🗓️ Aplicando Sistema Temático Semanal...")
            
            # Obter conteúdo temático baseado no dia e horário
            themed_content_prompt, themed_image_prompt, weekly_theme_metadata = get_weekly_themed_content(
                day_of_week=force_day_of_week,
                time_slot=force_time_slot,
                custom_theme=original_text
            )
            
            # Verificar se é horário matinal com cunho espiritual obrigatório
            if is_morning_spiritual_time() or weekly_theme_metadata.get("spiritual_focus", False):
                print("✨ CUNHO ESPIRITUAL OBRIGATÓRIO aplicado para postagem matinal")
            
            # Sobrescrever prompts se não foram fornecidos explicitamente
            if not content_prompt:
                content_prompt = themed_content_prompt
                print(f"📝 Prompt de conteúdo temático aplicado: {weekly_theme_metadata.get('main_theme', 'N/A')}")
            
            if not replicate_prompt:
                replicate_prompt = themed_image_prompt
                print(f"🎨 Prompt de imagem temático aplicado: {weekly_theme_metadata.get('image_style', 'N/A')}")
            
            print(f"📅 Tema do dia: {weekly_theme_metadata.get('day_name', 'N/A')} - {weekly_theme_metadata.get('time_slot', 'N/A')}")
            print(f"🎯 Foco: {weekly_theme_metadata.get('content_type', 'N/A')}")
            
        except Exception as e:
            print(f"⚠️ Erro no sistema temático semanal: {e}")
            print("Continuando com sistema padrão...")
    
    # Inicializa clientes
    openai = OpenAIClient(openai_key)

    # Primeiro, decidir qual imagem será usada (Replicate ou original re-hospedada)
    generated_image_url = source_image_url
    replicate_error = None
    if not disable_replicate:
        replicate = ReplicateClient(replicate_token)
        
        # Determinar formato de conteúdo para otimizar a imagem
        content_manager = ContentFormatManager()
        
        # Aplicar configurações A/B para formato de conteúdo
        if ab_config.get("force_format"):
            suggested_format = ab_config["force_format"]
        elif original_text:
            analysis = content_manager.get_content_analysis(original_text)
            suggested_format = analysis["suggested_format"]
        else:
            suggested_format = content_manager.get_random_format()
        
        # Sistema inteligente de qualidade visual
        if replicate_prompt:
            # Usar prompt personalizado se fornecido
            safer_image_prompt = replicate_prompt
        else:
            # Usar sistema de qualidade visual aprimorado
            content_theme = "growth and leadership"
            if original_text:
                # Extrair tema do texto original
                theme_keywords = {
                    "crescimento": "growth and development",
                    "liderança": "leadership and influence", 
                    "transformação": "transformation and change",
                    "sucesso": "success and achievement",
                    "inovação": "innovation and creativity",
                    "equipe": "teamwork and collaboration"
                }
                for keyword, theme in theme_keywords.items():
                    if keyword in original_text.lower():
                        content_theme = theme
                        break
            
            # Sistema inteligente de conceitos superiores (baseado nas 3 imagens de referência)
            # Verificar se a conta tem conceitos superiores habilitados
            superior_concepts_enabled = False
            superior_concepts_probability = 0.7  # Padrão
            
            if account_config:
                superior_concepts_enabled = account_config.get("superior_concepts_enabled", False)
                superior_concepts_probability = account_config.get("superior_concepts_probability", 0.7)
            
            use_superior_concepts = superior_concepts_enabled and random.random() < superior_concepts_probability
            
            if use_superior_concepts:
                # Usar sistema de conceitos superiores baseado nas imagens de referência
                safer_image_prompt, quality_metadata = get_superior_concept_prompt(
                    content_theme=content_theme
                )
            else:
                # Usar sistema de qualidade visual aprimorado (sistema anterior)
                safer_image_prompt, quality_metadata = get_enhanced_image_prompt(
                    content_theme=content_theme,
                    current_style="professional",
                    force_high_quality=True  # Sempre priorizar qualidade
                )
        
        # Aprimorar prompt baseado no formato de conteúdo
        safer_image_prompt = content_manager.enhance_replicate_prompt(safer_image_prompt, suggested_format)
        
        # Aplicar configurações A/B para estilo de imagem
        if ab_config.get("image_style"):
            image_style = ab_config["image_style"]
            if image_style == "minimalist":
                safer_image_prompt += " Estilo ultra-minimalista, composição limpa, espaços em branco, elementos geométricos simples."
            elif image_style == "dynamic":
                safer_image_prompt += " Estilo dinâmico com movimento, gradientes vibrantes, elementos em perspectiva, energia visual."
        
        if original_text:
            safer_image_prompt += (
                f" Baseie os elementos visuais no tema descrito: '{original_text}'. "
                "Evite literalidade excessiva; use metáforas visuais diretas ligadas ao tema."
            )
        # Se veio um estilo do CLI, incluir como instrução de estilo
        if caption_style:
            safer_image_prompt += f" Estilo adicional: {caption_style}."
        
        try:
            generated_image_url = replicate.generate_image(prompt=safer_image_prompt)
        except Exception as e:
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
                generated_image_url = hosted_url
            except Exception as sup_err:
                try:
                    hosted_public = PublicUploader().upload_from_url(generated_image_url)
                    generated_image_url = hosted_public
                except Exception as up_err:
                    pass
        else:
            try:
                hosted_public = PublicUploader().upload_from_url(generated_image_url)
                generated_image_url = hosted_public
            except Exception as up_err:
                pass
    except Exception as cfg_err:
        pass

    # NOVO FLUXO: GERAR TEXTO PRIMEIRO, DEPOIS IMAGEM BASEADA NO TEXTO
    
    # Definir variáveis de configuração de conceitos superiores
    superior_concepts_enabled = False
    superior_concepts_probability = 0.7  # Padrão
    
    if account_config:
        superior_concepts_enabled = account_config.get("superior_concepts_enabled", False)
        superior_concepts_probability = account_config.get("superior_concepts_probability", 0.7)
    
    use_superior_concepts = superior_concepts_enabled and random.random() < superior_concepts_probability
    
    # 1. PRIMEIRO: Gerar o conteúdo/texto baseado no tema ou prompt
    if content_prompt:
        # Usar prompt personalizado para gerar conteúdo inicial
        initial_content = openai.generate_content_from_prompt(content_prompt)
    else:
        # Usar descrição básica da imagem original como base
        initial_content = openai.describe_image(
            source_image_url,
            custom_prompt="Descreva brevemente o tema principal desta imagem para criar conteúdo relacionado."
        )
    
    # 2. SEGUNDO: Refinar a imagem baseada no conteúdo gerado
    if not disable_replicate:
        # Analisar o conteúdo para identificar elementos específicos
        content_lower = initial_content.lower()
        
        # Criar prompt de imagem mais específico baseado no conteúdo
        content_based_image_prompt = f"""
        CONTEÚDO A ILUSTRAR: "{initial_content}"
        
        INSTRUÇÕES ESPECÍFICAS DE IMAGEM:
        """
        
        # Adicionar instruções específicas baseadas no conteúdo
        if "geladeira" in content_lower or "refrigerador" in content_lower:
            if "borracha" in content_lower or "vedação" in content_lower:
                content_based_image_prompt += """
        - MOSTRAR: Geladeira com foco na borracha de vedação da porta
        - PROBLEMA VISÍVEL: Borracha ressecada, rachada, suja ou com mofo
        - ÂNGULO: Close-up na porta da geladeira mostrando a vedação danificada
        - CONTEXTO: Cozinha residencial, iluminação que destaque o problema
                """
            else:
                content_based_image_prompt += """
        - MOSTRAR: Geladeira em contexto de manutenção ou problema técnico
        - FOCO: Componentes internos, motor, ou técnico trabalhando
                """
        
        elif "ar-condicionado" in content_lower or "ar condicionado" in content_lower or "split" in content_lower:
            if "sujo" in content_lower or "fungo" in content_lower or "bactéria" in content_lower or "sujeira" in content_lower:
                content_based_image_prompt += """
        - MOSTRAR: Ar-condicionado split com filtros visivelmente sujos
        - PROBLEMA VISÍVEL: Filtros escuros, com acúmulo de poeira, fungos ou mofo
        - ÂNGULO: Ar-condicionado aberto mostrando o interior sujo
        - CONTRASTE: Lado sujo vs lado limpo (antes/depois)
        - AMBIENTE: Parede residencial, foco no equipamento
                """
            else:
                content_based_image_prompt += """
        - MOSTRAR: Ar-condicionado split em contexto de manutenção
        - FOCO: Técnico trabalhando, componentes internos, ou instalação
                """
        
        elif "máquina de lavar" in content_lower or "lavadora" in content_lower:
            content_based_image_prompt += """
        - MOSTRAR: Máquina de lavar em contexto de reparo ou manutenção
        - FOCO: Componentes internos, técnico trabalhando, ou problema específico
            """
        
        elif "elétrica" in content_lower or "eletricista" in content_lower or "instalação" in content_lower:
            content_based_image_prompt += """
        - MOSTRAR: Trabalho elétrico profissional em andamento
        - FOCO: Técnico uniformizado, ferramentas específicas, instalação elétrica
            """
        
        # Adicionar requisitos gerais de qualidade
        content_based_image_prompt += """
        
        QUALIDADE TÉCNICA:
        - Fotografia profissional, alta resolução
        - Iluminação técnica adequada
        - Cores realistas e naturais
        - Foco nítido no problema/serviço
        - Ambiente residencial ou comercial real
        - NUNCA: escritórios, computadores, ambientes corporativos genéricos
        
        OBJETIVO: Mostrar visualmente o problema específico mencionado no conteúdo para gerar urgência e necessidade do serviço técnico.
        """
        
        # Aplicar melhorias do sistema existente
        if use_superior_concepts:
            enhanced_prompt, quality_metadata = get_superior_concept_prompt(content_theme=initial_content)
            content_based_image_prompt = f"{content_based_image_prompt}\n{enhanced_prompt}"
        else:
            enhanced_prompt, quality_metadata = get_enhanced_image_prompt(
                content_theme=initial_content,
                current_style="professional",
                force_high_quality=True
            )
            content_based_image_prompt = f"{content_based_image_prompt}\n{enhanced_prompt}"
        
        print(f"🎨 Gerando imagem baseada no conteúdo: {initial_content[:100]}...")
        try:
            generated_image_url = replicate.generate_image(prompt=content_based_image_prompt)
            print("✅ Imagem gerada com sucesso baseada no conteúdo!")
        except Exception as e:
            print(f"❌ Replicate falhou, usando imagem original. Erro: {e}")
            replicate_error = str(e)
            generated_image_url = source_image_url
    
    # 3. TERCEIRO: Gerar descrição final da imagem gerada (para validação)
    final_description = openai.describe_image(
        generated_image_url,
        custom_prompt="Descreva esta imagem de forma técnica e detalhada."
    )
    
    # Usar o conteúdo inicial como base principal (não a descrição da imagem)
    description = initial_content
    
    # Inicializar variáveis de tracking
    chosen_format = "standard"
    dynamic_hashtags = []
    
    if caption_prompt:
        # Suporte a placeholders {descricao} e {texto_original}
        # Agora {descricao} se refere ao conteúdo gerado, não à descrição da imagem
        prompt_text = caption_prompt.replace("{descricao}", description)
        if original_text:
            prompt_text = prompt_text.replace("{texto_original}", original_text)
        
        # Aplicar variações de formato de conteúdo
        enhanced_prompt, chosen_format = get_format_enhanced_prompt(
            prompt_text, 
            content=original_text or description,
            original_text=original_text
        )
        
        # Integrar hashtags dinâmicas
        hashtag_manager = HashtagManager()
        context_keywords = [original_text] if original_text else []
        
        # Adicionar hashtags temáticas do sistema semanal
        thematic_hashtags = []
        if use_weekly_themes and weekly_theme_metadata.get("hashtag_suggestions"):
            thematic_hashtags = weekly_theme_metadata["hashtag_suggestions"]
        
        # Aplicar configurações A/B para estratégia de hashtags
        hashtag_strategy = ab_config.get("hashtag_strategy", "balanced")
        if hashtag_strategy == "trending":
            dynamic_hashtags = hashtag_manager.generate_trending_hashtags(
                context=chosen_format,
                keywords=context_keywords
            )
        elif hashtag_strategy == "niche":
            dynamic_hashtags = hashtag_manager.generate_niche_hashtags(
                context=chosen_format,
                keywords=context_keywords
            )
        else:
            dynamic_hashtags = hashtag_manager.get_dynamic_hashtags(
                context=chosen_format
            )
        
        # Combinar hashtags dinâmicas com temáticas (priorizar temáticas)
        combined_hashtags = thematic_hashtags + [tag for tag in dynamic_hashtags if tag not in thematic_hashtags]
        dynamic_hashtags = combined_hashtags[:15]  # Limitar a 15 hashtags total
        
        # Adicionar informações sobre hashtags ao prompt
        hashtag_instruction = f"\n\nUSE ESTAS HASHTAGS DINÂMICAS: {' '.join(dynamic_hashtags)}"
        enhanced_prompt += hashtag_instruction
        
        caption = openai.generate_caption_with_prompt(enhanced_prompt)
    else:
        caption = openai.generate_caption(description, caption_style)

    # Preparar e publicar no Instagram
    instagram = InstagramClient(instagram_business_id, instagram_access_token)
    # Validação básica do token do Instagram: evitar credenciais de login equivocadas
    invalid_token_markers = [" ", "@", "login:"]
    if not instagram_access_token or any(m in instagram_access_token for m in invalid_token_markers):
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
            telegram_sent = False
            try:
                if final_status == "PUBLISHED":
                    telegram_sent = TelegramClient(telegram_bot_token, telegram_chat_id).send_message("Instagram content is shared")
                    
                    # Registrar post no sistema de tracking de performance
                    if account_name and media_id:
                        try:
                            # Preparar metadados temáticos para tracking
                            tracking_metadata = {
                                "weekly_theme_system": use_weekly_themes,
                                "day_theme": weekly_theme_metadata.get("main_theme", ""),
                                "time_slot": weekly_theme_metadata.get("time_slot", ""),
                                "content_type": weekly_theme_metadata.get("content_type", ""),
                                "spiritual_focus": weekly_theme_metadata.get("spiritual_focus", False),
                                "is_special_day": weekly_theme_metadata.get("is_special_day", False),
                                "thematic_hashtags_count": len(weekly_theme_metadata.get("hashtag_suggestions", []))
                            }
                            
                            track_post_performance(
                                post_id=media_id,
                                account_name=account_name,
                                content_format=chosen_format,
                                hashtags=dynamic_hashtags,
                                image_style="optimized" if not disable_replicate else "original",
                                custom_metadata=tracking_metadata
                            )
                        except Exception as track_err:
                            pass
                    
                    # PUBLICAÇÃO NO STORIES (se habilitada)
                    stories_result = None
                    if publish_to_stories:
                        try:
                            # 1. Processar imagem para formato 9:16 com texto
                            stories_processor = StoriesImageProcessor()
                            
                            # Determinar texto para Stories
                            if stories_text and stories_text.strip():
                                # Usar texto personalizado fornecido
                                text_for_stories = stories_text
                            else:
                                # Gerar frase curta automaticamente baseada no conteúdo
                                text_for_stories = stories_processor.generate_short_catchphrase(description, caption)
                            
                            # Processar imagem com texto
                            stories_image_path = stories_processor.process_and_save_for_stories_with_text(
                                generated_image_url,
                                text=text_for_stories,
                                background_type=stories_background_type,
                                text_position=stories_text_position
                            )
                            
                            # 2. Re-hospedar imagem processada
                            stories_image_url = generated_image_url  # Fallback
                            try:
                                if supa_url and supa_key and supa_bkt:
                                    stories_image_url = SupabaseUploader(supa_url, supa_key, supa_bkt).upload_from_file(
                                        stories_image_path, force_jpeg=True
                                    )
                                else:
                                    stories_image_url = PublicUploader().upload_from_file(stories_image_path)
                            except Exception as upload_err:
                                pass
                            finally:
                                # Limpar arquivo temporário
                                stories_processor.cleanup_temp_file(stories_image_path)
                            
                            # 3. Publicar no Stories
                            stories_result = instagram.publish_to_stories_complete(stories_image_url)
                            
                            if stories_result.get("success"):
                                TelegramClient(telegram_bot_token, telegram_chat_id).send_message(
                                    f"✅ Conteúdo publicado com sucesso!\n📱 Feed: {media_id}\n📖 Stories: {stories_result.get('media_id')}"
                                )
                            else:
                                TelegramClient(telegram_bot_token, telegram_chat_id).send_message(
                                    f"⚠️ Feed publicado ({media_id}), mas Stories falhou: {stories_result.get('error')}"
                                )
                                
                        except Exception as stories_err:
                            stories_result = {"success": False, "error": str(stories_err)}
                            TelegramClient(telegram_bot_token, telegram_chat_id).send_message(
                                f"⚠️ Feed publicado, mas Stories falhou: {stories_err}"
                            )
                    else:
                        # Mensagem original se Stories não estiver habilitado
                        TelegramClient(telegram_bot_token, telegram_chat_id).send_message("Instagram content is shared")
                        
                else:
                    TelegramClient(telegram_bot_token, telegram_chat_id).send_message(
                        f"Instagram content publish status: {final_status}"
                    )
            except Exception:
                pass
            # Preparar resultado com informações do Stories
            result = {
                "description": description,
                "caption": caption,
                "generated_image_url": generated_image_url,
                "creation_id": creation_id,
                "media_id": media_id,
                "status": final_status,
                "telegram_sent": telegram_sent,
                "replicate_error": replicate_error,
            }
            
            # Adicionar informações do Stories se foi tentado
            if publish_to_stories and 'stories_result' in locals():
                result["stories"] = stories_result
                result["stories_published"] = stories_result.get("success", False) if stories_result else False
            
            return result
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