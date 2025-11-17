import argparse
from typing import List
import os
import time
import sys
import logging

from config import load_config
from pipeline.collect import collect_hashtags, collect_userposts
from pipeline.generate_and_publish import generate_and_publish
from services.db import Database
from services.rapidapi_client import RapidAPIClient
import json
from reports.service_status_report import export_service_status
from reports.ltm_reporter import sign_exports, export_all
from services.backup_manager import BackupManager

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s'
)
logger = logging.getLogger(__name__)


def cmd_collect(hashtags: List[str]):
    cfg = load_config()
    inserted = collect_hashtags(cfg["RAPIDAPI_KEY"], cfg["RAPIDAPI_HOST"], cfg["POSTGRES_DSN"], hashtags)
    print(f"Coleta concluída. Novos itens inseridos: {inserted}")


def cmd_generate(image_url: str, style: str | None = None):
    cfg = load_config()
    result = generate_and_publish(
        openai_key=cfg["OPENAI_API_KEY"],
        replicate_token=cfg["REPLICATE_TOKEN"],
        instagram_business_id=cfg["INSTAGRAM_BUSINESS_ACCOUNT_ID"],
        instagram_access_token=cfg["INSTAGRAM_ACCESS_TOKEN"],
        telegram_bot_token=cfg["TELEGRAM_BOT_TOKEN"],
        telegram_chat_id=cfg["TELEGRAM_CHAT_ID"],
        source_image_url=image_url,
        caption_style=style,
    )
    print("Resultado:", result)


def main():
    """Função principal do agente de postagem automática"""
    # Obter nome do cron das variáveis de ambiente
    cron_name = os.getenv('CRON_NAME', 'agente_default')
    logger.info(f"🚀 Iniciando agente: {cron_name}")

    # Variáveis de conexão para fechar depois
    conexao_db = None

    try:
        parser = argparse.ArgumentParser(description="Agente de Post Automático Instagram")
        sub = parser.add_subparsers(dest="cmd")

        p_collect = sub.add_parser("collect", help="Coletar tendências por hashtags")
        p_collect.add_argument("--hashtags", required=True, help="Lista de hashtags separadas por vírgula")

        p_collect_users = sub.add_parser("collect_users", help="Coletar posts por usuários")
        p_collect_users.add_argument("--users", required=True, help="Lista de usernames separadas por vírgula")

        p_generate = sub.add_parser("generate", help="Gerar descrição, legenda e imagem a partir de URL")
        p_generate.add_argument("--image_url", required=True)
        p_generate.add_argument("--style", required=False)
        p_generate.add_argument(
            "--disable_replicate",
            "--disable-replicate",
            action="store_true",
            help="Usar imagem original (sem Replicate)"
        )
        # Flags opcionais de Supabase para teste ad-hoc
        p_generate.add_argument("--supabase_url", required=False, help="Override da URL do Supabase")
        p_generate.add_argument("--supabase_service_key", required=False, help="Override da Service Key do Supabase")
        p_generate.add_argument("--supabase_bucket", required=False, help="Override do bucket do Supabase")
        p_generate.add_argument("--account", required=False, help="Nome da conta para usar prompts específicos (padrão: Milton_Albanez)")
        p_generate.add_argument("--stories", action="store_true", help="Publicar como Stories em vez de Feed")

        p_unposted = sub.add_parser("unposted", help="Listar itens não postados do banco")
        p_unposted.add_argument("--limit", type=int, default=10)

        p_preseed = sub.add_parser("preseed", help="Coleta rotineira antes do horário de autopost")
        p_preseed.add_argument("--only", type=str, required=False, help="Rodar apenas uma conta pelo nome exato")

        p_autopost = sub.add_parser("autopost", help="Gerar e publicar a partir do primeiro item não postado")
        p_autopost.add_argument("--style", required=False)
        p_autopost.add_argument("--stories", action="store_true", help="Publicar como Stories em vez de Feed")
        p_autopost.add_argument(
            "--disable_replicate",
            "--no_replicate",
            "--no-replicate",
            action="store_true",
            help="Usar imagem original (sem Replicate)"
        )
        p_autopost.add_argument("--tags", required=False, help="Lista de tags/usernames separadas por vírgula para filtrar o banco")
        p_autopost.add_argument("--replicate_prompt", required=False, help="Override do prompt de geração de imagem (Replicate)")
        # Flags opcionais de Supabase para teste ad-hoc (override das variáveis de ambiente)
        p_autopost.add_argument("--supabase_url", required=False, help="Override da URL do Supabase")
        p_autopost.add_argument("--supabase_service_key", required=False, help="Override da Service Key do Supabase")
        p_autopost.add_argument("--supabase_bucket", required=False, help="Override do bucket do Supabase")

        p_seed = sub.add_parser("seed_demo", help="Inserir um item de teste no banco")
        p_seed.add_argument("--code", required=False, default="trae_code_demo")
        p_seed.add_argument("--url", required=False, default="https://picsum.photos/seed/trae/1024/1024")
        p_seed.add_argument("--tag", required=False, default="demo")
        p_seed.add_argument("--prompt", required=False, default="Teste prompt")

        p_multirun = sub.add_parser("multirun", help="Executa fluxo para múltiplas contas definidas em accounts.json")
        p_multirun.add_argument("--limit", type=int, default=1, help="Qtde de itens por conta")
        p_multirun.add_argument("--only", type=str, required=False, help="Rodar apenas uma conta pelo nome exato")
        p_multirun.add_argument("--stories", action="store_true", help="Publicar como Stories em vez de Feed")

        p_clear = sub.add_parser("clear_cache", help="Limpa cache persistente do RapidAPI")
        p_clear.add_argument("--url-contains", dest="url_contains", type=str, default=None, help="Filtrar por texto no URL")
        p_clear.add_argument("--path", dest="path", type=str, default=None, help="Nome de arquivo de cache específico")
        p_clear.add_argument("--older", dest="older", type=int, default=None, help="Remover entradas mais antigas que N segundos")

        p_standalone = sub.add_parser("standalone", help="Gerar e publicar conteúdo sem depender de APIs externas")
        p_standalone.add_argument("--account", required=False, default="Milton_Albanez", help="Nome da conta")
        p_standalone.add_argument("--content_prompt", required=False, help="Prompt personalizado para conteúdo")
        p_standalone.add_argument("--style", required=False, help="Estilo da legenda")
        p_standalone.add_argument("--stories", action="store_true", help="Publicar como Stories")
        p_standalone.add_argument("--disable_replicate", action="store_true", help="Usar imagem placeholder")
        p_standalone.add_argument("--theme", required=False, help="Tema específico (ex: motivacional, produtividade)")

        # comandos auxiliares de relatório/validação podem ser adicionados futuramente

        args = parser.parse_args()
        if args.cmd == "collect":
            hashtags = [h.strip() for h in args.hashtags.split(",") if h.strip()]
            cmd_collect(hashtags)
            return 0
        elif args.cmd == "collect_users":
            cfg = load_config()
            users = [u.strip() for u in args.users.split(",") if u.strip()]
            inserted = collect_userposts(cfg["RAPIDAPI_KEY"], cfg["RAPIDAPI_HOST"], cfg["POSTGRES_DSN"], users)
            print(f"Coleta por usuários concluída. Novos itens inseridos: {inserted}")
            return 0
        elif args.cmd == "generate":
            # Encaminhar flags Supabase se presentes
            supa_url = getattr(args, "supabase_url", None)
            supa_key = getattr(args, "supabase_service_key", None)
            supa_bkt = getattr(args, "supabase_bucket", None)
            if supa_url or supa_key or supa_bkt:
                cfg = load_config()
                result = generate_and_publish(
                    openai_key=cfg["OPENAI_API_KEY"],
                    replicate_token=cfg["REPLICATE_TOKEN"],
                    instagram_business_id=cfg["INSTAGRAM_BUSINESS_ACCOUNT_ID"],
                    instagram_access_token=cfg["INSTAGRAM_ACCESS_TOKEN"],
                    telegram_bot_token=cfg["TELEGRAM_BOT_TOKEN"],
                    telegram_chat_id=cfg["TELEGRAM_CHAT_ID"],
                    source_image_url=args.image_url,
                    caption_style=args.style,
                    disable_replicate=getattr(args, "disable_replicate", False),
                    supabase_url=supa_url,
                    supabase_service_key=supa_key,
                    supabase_bucket=supa_bkt,
                    # Suporte para Stories
                    publish_to_stories=getattr(args, "stories", False),
                    stories_text_position="auto" if getattr(args, "stories", False) else None,
                )
                print("Resultado:", result)
            else:
                cfg = load_config()
                # Carregar prompts da conta especificada (padrão: Milton_Albanez)
                account_name = getattr(args, "account", "Milton_Albanez")
                selected_account = None
                try:
                    with open("accounts.json", "r", encoding="utf-8") as f:
                        accounts = json.load(f)
                    selected_account = next((a for a in accounts if a.get("nome") == account_name), None)
                    if not selected_account:
                        print(f"⚠️ Conta '{account_name}' não encontrada. Usando configuração padrão.")
                except Exception as e:
                    print(f"⚠️ Erro ao carregar accounts.json: {e}")
                    selected_account = None
                # Usar credenciais específicas da conta se disponíveis
                acc_instagram_id = selected_account.get("instagram_id") if selected_account else cfg["INSTAGRAM_BUSINESS_ACCOUNT_ID"]
                acc_instagram_token = selected_account.get("instagram_access_token") if selected_account else cfg["INSTAGRAM_ACCESS_TOKEN"]
                
                # Fallback para credenciais temporárias - usar credenciais do .env
                if acc_instagram_id == "TEMPORARIO_USAR_CREDENCIAIS_MILTON":
                    acc_instagram_id = cfg["INSTAGRAM_BUSINESS_ACCOUNT_ID"]
                if acc_instagram_token == "TEMPORARIO_USAR_CREDENCIAIS_MILTON":
                    acc_instagram_token = cfg["INSTAGRAM_ACCESS_TOKEN"]
                
                result = generate_and_publish(
                    openai_key=cfg["OPENAI_API_KEY"],
                    replicate_token=cfg["REPLICATE_TOKEN"],
                    instagram_business_id=acc_instagram_id,
                    instagram_access_token=acc_instagram_token,
                    telegram_bot_token=cfg["TELEGRAM_BOT_TOKEN"],
                    telegram_chat_id=cfg["TELEGRAM_CHAT_ID"],
                    source_image_url=args.image_url,
                    caption_style=args.style,
                    content_prompt=selected_account.get("prompt_ia_geracao_conteudo") if selected_account else None,
                    caption_prompt=selected_account.get("prompt_ia_legenda") if selected_account else None,
                    replicate_prompt=selected_account.get("prompt_ia_replicate") if selected_account else None,
                    original_text=None,
                    disable_replicate=getattr(args, "disable_replicate", False),
                    account_name=account_name if selected_account else None,
                    account_config=selected_account,
                    # Suporte para Stories
                    publish_to_stories=getattr(args, "stories", False),
                    stories_text_position="auto" if getattr(args, "stories", False) else None,
                )
                print("Resultado:", result)
            return 0
        elif args.cmd == "unposted":
            cfg = load_config()
            rows = Database(cfg["POSTGRES_DSN"]).list_unposted(args.limit)
            for r in rows:
                print(r)
            return 0
        elif args.cmd == "seed_demo":
            cfg = load_config()
            conexao_db = Database(cfg["POSTGRES_DSN"])
            item = {
                "prompt": args.prompt,
                "thumbnail_url": args.url,
                "content_code": args.code,
                "tag": args.tag,
            }
            conexao_db.insert_trend(item)
            return 0
        elif args.cmd == "preseed":
            cfg = load_config()
            # Ler contas
            try:
                with open("accounts.json", "r", encoding="utf-8") as f:
                    accounts = json.load(f)
            except Exception as e:
                print(f"ERRO ao ler accounts.json: {e}")
                return 1
            target_name = getattr(args, "only", None) or os.environ.get("ACCOUNT_NAME", "Milton_Albanez")
            acc = next((a for a in accounts if a.get("nome") == target_name), None)
            if not acc:
                print(f"Conta '{target_name}' não encontrada em accounts.json")
                return 1
            hashtags = acc.get("hashtags_pesquisa", [])
            users = acc.get("usernames", [])
            inserted = 0
            if hashtags:
                inserted += collect_hashtags(cfg["RAPIDAPI_KEY"], cfg["RAPIDAPI_HOST"], cfg["POSTGRES_DSN"], hashtags)
            if users:
                inserted += collect_userposts(cfg["RAPIDAPI_KEY"], cfg["RAPIDAPI_HOST"], cfg["POSTGRES_DSN"], users)
            print(f"Preseed concluído para {target_name}. Novos itens inseridos: {inserted}")
            try:
                conexao_db = Database(cfg["POSTGRES_DSN"])
                filter_tags = hashtags + users
                rows = conexao_db.list_unposted_by_tags(filter_tags, 50)
                print(f"Itens não postados disponíveis para {target_name}: {len(rows)}")
            except Exception as e:
                print(f"Aviso: não foi possível listar não postados por tags: {e}")
            return 0
        elif args.cmd == "autopost":
            cfg = load_config()
            rows = []
            db_available = bool(cfg.get("POSTGRES_DSN"))
            if db_available:
                try:
                    conexao_db = Database(cfg["POSTGRES_DSN"])
                    tags_arg = getattr(args, "tags", None) or os.environ.get("POST_TAGS")
                    if tags_arg:
                        tags = [t.strip() for t in tags_arg.split(",") if t.strip()]
                        rows = conexao_db.list_unposted_by_tags(tags, 1)
                    else:
                        rows = conexao_db.list_unposted(1)
                except Exception as e:
                    print(f"⚠️ Erro ao conectar/consultar o banco: {e}. Ativando fallback Standalone.")
                    rows = []
            else:
                print("⚠️ Aviso: POSTGRES_DSN/DATABASE_URL não definido. Usando fallback Standalone para garantir publicação.")

            if not rows:
                acc_name = os.environ.get("ACCOUNT_NAME", "Milton_Albanez")
                acc = None
                try:
                    with open("accounts.json", "r", encoding="utf-8") as f:
                        accounts = json.load(f)
                    acc = next((a for a in accounts if a.get("nome") == acc_name), None)
                except Exception as e:
                    print(f"⚠️ Erro ao carregar accounts.json: {e}")
                fallback_theme = "motivacional"
                theme_images = {
                    "motivacional": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?ixlib=rb-4.0.3&auto=format&fit=crop&w=1080&h=1080&q=80",
                    "produtividade": "https://images.unsplash.com/photo-1484480974693-6ca0a78fb36b?ixlib=rb-4.0.3&auto=format&fit=crop&w=1080&h=1080&q=80",
                    "lideranca": "https://images.unsplash.com/photo-1552664730-d307ca884978?ixlib=rb-4.0.3&auto=format&fit=crop&w=1080&h=1080&q=80",
                    "mindset": "https://images.unsplash.com/photo-1499209974431-9dddcece7f88?ixlib=rb-4.0.3&auto=format&fit=crop&w=1080&h=1080&q=80",
                    "negocios": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?ixlib=rb-4.0.3&auto=format&fit=crop&w=1080&h=1080&q=80",
                }
                source_image_url = theme_images.get(fallback_theme, theme_images["motivacional"])
                acc_content_prompt = acc.get("prompt_ia_geracao_conteudo") if acc else None
                acc_caption_prompt = acc.get("prompt_ia_legenda") if acc else None
                acc_replicate_prompt = acc.get("prompt_ia_replicate") if acc else None
                try:
                    result = generate_and_publish(
                        openai_key=cfg["OPENAI_API_KEY"],
                        replicate_token=cfg["REPLICATE_TOKEN"],
                        instagram_business_id=cfg["INSTAGRAM_BUSINESS_ACCOUNT_ID"],
                        instagram_access_token=cfg["INSTAGRAM_ACCESS_TOKEN"],
                        telegram_bot_token=cfg["TELEGRAM_BOT_TOKEN"],
                        telegram_chat_id=cfg["TELEGRAM_CHAT_ID"],
                        source_image_url=source_image_url,
                        caption_style=getattr(args, "style", None),
                        content_prompt=acc_content_prompt,
                        caption_prompt=acc_caption_prompt,
                        original_text=None,
                        disable_replicate=True,
                        replicate_prompt=acc_replicate_prompt,
                        supabase_url=getattr(args, "supabase_url", None),
                        supabase_service_key=getattr(args, "supabase_service_key", None),
                        supabase_bucket=getattr(args, "supabase_bucket", None),
                        account_name=acc_name if acc else None,
                        account_config=acc,
                        publish_to_stories=getattr(args, "stories", False),
                        stories_text_position="auto" if getattr(args, "stories", False) else None,
                        use_weekly_themes=True,
                    )
                    print("Resultado:", result)
                except Exception as e:
                    print(f"❌ Erro no fallback Standalone: {e}")
                return 0

            item = rows[0]
            acc_content_prompt = None
            acc_caption_prompt = None
            acc_replicate_prompt = None
            acc_name = os.environ.get("ACCOUNT_NAME", "Milton_Albanez")
            try:
                with open("accounts.json", "r", encoding="utf-8") as f:
                    accounts = json.load(f)
                acc = next((a for a in accounts if a.get("nome") == acc_name), None)
                if acc:
                    acc_content_prompt = acc.get("prompt_ia_geracao_conteudo")
                    acc_caption_prompt = acc.get("prompt_ia_legenda")
                    acc_replicate_prompt = acc.get("prompt_ia_replicate")
            except Exception:
                pass
            try:
                result = generate_and_publish(
                    openai_key=cfg["OPENAI_API_KEY"],
                    replicate_token=cfg["REPLICATE_TOKEN"],
                    instagram_business_id=cfg["INSTAGRAM_BUSINESS_ACCOUNT_ID"],
                    instagram_access_token=cfg["INSTAGRAM_ACCESS_TOKEN"],
                    telegram_bot_token=cfg["TELEGRAM_BOT_TOKEN"],
                    telegram_chat_id=cfg["TELEGRAM_CHAT_ID"],
                    source_image_url=item["thumbnail_url"],
                    caption_style=args.style,
                    content_prompt=acc_content_prompt,
                    caption_prompt=acc_caption_prompt,
                    original_text=item.get("prompt"),
                    disable_replicate=getattr(args, "disable_replicate", False),
                    replicate_prompt=(getattr(args, "replicate_prompt", None) or acc_replicate_prompt),
                    supabase_url=getattr(args, "supabase_url", None),
                    supabase_service_key=getattr(args, "supabase_service_key", None),
                    supabase_bucket=getattr(args, "supabase_bucket", None),
                    account_name=acc_name if acc else None,
                    account_config=acc,
                    publish_to_stories=getattr(args, "stories", False),
                    stories_text_position="auto" if getattr(args, "stories", False) else None,
                )
                print("Resultado:", result)
                if result.get("status") == "PUBLISHED":
                    try:
                        if db_available and conexao_db:
                            conexao_db.mark_posted(item["code"])
                            print(f"Marcado como postado: {item['code']}")
                    except Exception:
                        pass
            except Exception as e:
                print(f"❌ Erro na publicação: {e}")
            return 0
        
        elif args.cmd == "multirun":
            cfg = load_config()
            is_stories_mode = getattr(args, "stories", False)
            try:
                with open("accounts.json", "r", encoding="utf-8") as f:
                    accounts = json.load(f)
            except Exception as e:
                print(f"❌ ERRO ao carregar accounts.json: {e}")
                return 0
            for acc in accounts:
                nome = acc.get("nome")
                if getattr(args, "only", None) and nome != args.only:
                    continue
                hashtags = acc.get("hashtags_pesquisa", [])
                users = acc.get("usernames", [])
                rapidapi_failed = False
                try:
                    if hashtags:
                        collect_hashtags(cfg["RAPIDAPI_KEY"], cfg["RAPIDAPI_HOST"], cfg["POSTGRES_DSN"], hashtags)
                except Exception:
                    rapidapi_failed = True
                try:
                    if users and not rapidapi_failed:
                        collect_userposts(cfg["RAPIDAPI_KEY"], cfg["RAPIDAPI_HOST"], cfg["POSTGRES_DSN"], users)
                except Exception:
                    rapidapi_failed = True
                rows = []
                try:
                    db = Database(cfg["POSTGRES_DSN"]) 
                    filter_tags = hashtags + users
                    rows = db.list_unposted_by_tags(filter_tags, args.limit)
                except Exception:
                    rapidapi_failed = True
                if len(rows) == 0:
                    import random
                    themes = ["motivacional", "produtividade", "lideranca", "mindset", "negocios"]
                    theme_images = {
                        "motivacional": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?ixlib=rb-4.0.3&auto=format&fit=crop&w=1080&h=1080&q=80",
                        "produtividade": "https://images.unsplash.com/photo-1484480974693-6ca0a78fb36b?ixlib=rb-4.0.3&auto=format&fit=crop&w=1080&h=1080&q=80",
                        "lideranca": "https://images.unsplash.com/photo-1552664730-d307ca884978?ixlib=rb-4.0.3&auto=format&fit=crop&w=1080&h=1080&q=80",
                        "mindset": "https://images.unsplash.com/photo-1499209974431-9dddcece7f88?ixlib=rb-4.0.3&auto=format&fit=crop&w=1080&h=1080&q=80",
                        "negocios": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?ixlib=rb-4.0.3&auto=format&fit=crop&w=1080&h=1080&q=80",
                    }
                    t = random.choice(themes)
                    fallback_image = theme_images.get(t, theme_images["motivacional"]) 
                    rows = [{
                        "thumbnail_url": fallback_image,
                        "code": f"fallback_{t}_{int(time.time())}",
                        "prompt": f"Conteúdo temático sobre {t}"
                    }]
                acc_instagram_id = acc.get("instagram_id") or cfg["INSTAGRAM_BUSINESS_ACCOUNT_ID"]
                acc_instagram_token = acc.get("instagram_access_token") or cfg["INSTAGRAM_ACCESS_TOKEN"]
                acc_supa_url = acc.get("supabase_url") or cfg.get("SUPABASE_URL")
                acc_supa_key = acc.get("supabase_service_key") or cfg.get("SUPABASE_SERVICE_KEY")
                acc_supa_bucket = acc.get("supabase_bucket") or cfg.get("SUPABASE_BUCKET")
                for item in rows:
                    try:
                        result = generate_and_publish(
                            openai_key=acc.get("openai_api_key", cfg["OPENAI_API_KEY"]),
                            replicate_token=acc.get("replicate_token", cfg["REPLICATE_TOKEN"]),
                            instagram_business_id=acc_instagram_id,
                            instagram_access_token=acc_instagram_token,
                            telegram_bot_token=acc.get("telegram_bot_token", cfg["TELEGRAM_BOT_TOKEN"]),
                            telegram_chat_id=acc.get("telegram_chat_id", cfg["TELEGRAM_CHAT_ID"]),
                            source_image_url=item["thumbnail_url"],
                            caption_style=getattr(args, "style", None),
                            content_prompt=acc.get("prompt_ia_geracao_conteudo"),
                            caption_prompt=acc.get("prompt_ia_legenda"),
                            original_text=item.get("prompt"),
                            disable_replicate=bool(acc.get("disable_replicate", False)),
                            replicate_prompt=acc.get("prompt_ia_replicate"),
                            supabase_url=acc_supa_url,
                            supabase_service_key=acc_supa_key,
                            supabase_bucket=acc_supa_bucket,
                            account_name=nome,
                            account_config=acc,
                            publish_to_stories=is_stories_mode,
                            stories_text_position="auto" if is_stories_mode else None,
                        )
                        print(f"✅ RESULTADO para {nome}: {result}")
                        if result.get("status") == "PUBLISHED":
                            try:
                                db.mark_posted(item.get("code", ""))
                                print(f"✅ Marcado como postado: {item.get('code', '')}")
                            except Exception:
                                pass
                    except Exception as e:
                        print(f"❌ ERRO ao processar item para {nome}: {e}")
                        continue
            return 0
        elif args.cmd == "clear_cache":
            cfg = load_config()
            client = RapidAPIClient(cfg["RAPIDAPI_KEY"], cfg["RAPIDAPI_HOST"])
            predicate = {}
            if getattr(args, "url_contains", None):
                predicate["url_contains"] = args.url_contains
            if getattr(args, "path", None):
                predicate["path"] = args.path
            if getattr(args, "older", None) is not None:
                predicate["older_than_seconds"] = args.older
            removed = client.clear_cache(predicate or None)
            print(f"Cache removido: {removed} arquivos")
            return 0
        elif args.cmd == "standalone":
            print("🚀 MODO STANDALONE - Geração de conteúdo independente")
            print("=" * 60)
            cfg = load_config()
            account_name = args.account
            selected_account = None
            try:
                with open("accounts.json", "r", encoding="utf-8") as f:
                    accounts = json.load(f)
                selected_account = next((a for a in accounts if a.get("nome") == account_name), None)
                if not selected_account:
                    print(f"⚠️ Conta '{account_name}' não encontrada. Usando configuração padrão.")
            except Exception as e:
                print(f"⚠️ Erro ao carregar accounts.json: {e}")
            content_prompt = args.content_prompt
            if not content_prompt and args.theme:
                theme_prompts = {
                    "motivacional": "Crie uma mensagem motivacional inspiradora sobre superação, crescimento pessoal e conquista de objetivos",
                    "produtividade": "Compartilhe uma dica prática e valiosa sobre produtividade, organização ou gestão de tempo",
                    "lideranca": "Desenvolva um insight sobre liderança, gestão de equipes ou desenvolvimento profissional",
                    "mindset": "Explore conceitos de mindset de crescimento, mentalidade positiva e desenvolvimento mental",
                    "negocios": "Apresente uma estratégia ou insight sobre empreendedorismo, negócios ou inovação"
                }
                content_prompt = theme_prompts.get(args.theme.lower(), "Crie conteúdo valioso e inspirador sobre desenvolvimento pessoal e profissional")
            theme_images = {
                "motivacional": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?ixlib=rb-4.0.3&auto=format&fit=crop&w=1080&h=1080&q=80",
                "produtividade": "https://images.unsplash.com/photo-1484480974693-6ca0a78fb36b?ixlib=rb-4.0.3&auto=format&fit=crop&w=1080&h=1080&q=80",
                "lideranca": "https://images.unsplash.com/photo-1552664730-d307ca884978?ixlib=rb-4.0.3&auto=format&fit=crop&w=1080&h=1080&q=80",
                "mindset": "https://images.unsplash.com/photo-1499209974431-9dddcece7f88?ixlib=rb-4.0.3&auto=format&fit=crop&w=1080&h=1080&q=80",
                "negocios": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?ixlib=rb-4.0.3&auto=format&fit=crop&w=1080&h=1080&q=80"
            }
            theme = args.theme.lower() if args.theme else "motivacional"
            source_image_url = theme_images.get(theme, theme_images["motivacional"])
            print(f"🎯 Conta: {account_name}")
            print(f"🎨 Tema: {theme.title()}")
            print(f"📝 Prompt: {content_prompt[:100]}..." if content_prompt and len(content_prompt) > 100 else f"📝 Prompt: {content_prompt}")
            print(f"🖼️ Imagem: {source_image_url}")
            print()
            try:
                acc_instagram_id = selected_account.get("instagram_id") if selected_account else cfg["INSTAGRAM_BUSINESS_ACCOUNT_ID"]
                acc_instagram_token = selected_account.get("instagram_access_token") if selected_account else cfg["INSTAGRAM_ACCESS_TOKEN"]
                result = generate_and_publish(
                    openai_key=cfg["OPENAI_API_KEY"],
                    replicate_token=cfg.get("REPLICATE_TOKEN", ""),
                    instagram_business_id=acc_instagram_id,
                    instagram_access_token=acc_instagram_token,
                    telegram_bot_token=cfg["TELEGRAM_BOT_TOKEN"],
                    telegram_chat_id=cfg["TELEGRAM_CHAT_ID"],
                    source_image_url=source_image_url,
                    content_prompt=content_prompt,
                    caption_style=args.style,
                    account_name=account_name,
                    account_config=selected_account,
                    disable_replicate=args.disable_replicate,
                    publish_to_stories=args.stories,
                    use_weekly_themes=True
                )
                print()
                print("✅ CONTEÚDO GERADO E PUBLICADO COM SUCESSO!")
                print(f"📊 Resultado: {result}")
                print()
                print("🎉 Modo standalone funcionando perfeitamente!")
                print("💡 Benefícios:")
                print("   • Independente de APIs externas")
                print("   • Conteúdo 100% original")
                print("   • Sistema temático automático")
                print("   • Sem limitações de rate limit")
            except Exception as e:
                print(f"❌ Erro no modo standalone: {e}")
                print("🔧 Verifique as configurações básicas (Instagram, OpenAI, Telegram)")
            return 0

        else:
            parser.print_help()
            return 0
        logger.info(f"✅ Agente {cron_name} concluído com sucesso!")
        return 0
    except Exception as e:
        logger.error(f"❌ Erro no agente {cron_name}: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        logger.info(f"🧹 Limpando recursos do agente {cron_name}...")
        try:
            if conexao_db:
                try:
                    conexao_db.close()
                    logger.info("  ✓ Conexão DB fechada")
                except Exception as e:
                    logger.warning(f"  ⚠️  Erro ao fechar DB: {e}")
        except Exception:
            pass

        # Fechar quaisquer outros objetos com método close presentes no escopo
        try:
            for name, obj in list(locals().items()):
                if hasattr(obj, "close") and callable(getattr(obj, "close")):
                    try:
                        obj.close()
                        logger.info(f"  ✓ Recurso '{name}' fechado")
                    except Exception as e:
                        logger.warning(f"  ⚠️  Erro ao fechar recurso '{name}': {e}")
        except Exception:
            pass

        logger.info(f"🏁 Finalizando agente {cron_name}")


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)