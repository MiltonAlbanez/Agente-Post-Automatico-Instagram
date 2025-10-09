import argparse
from typing import List

from config import load_config
from pipeline.collect import collect_hashtags, collect_userposts
from pipeline.generate_and_publish import generate_and_publish
from services.db import Database
from services.rapidapi_client import RapidAPIClient
import json


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
    parser = argparse.ArgumentParser(description="Agente de Post Automático Instagram")
    sub = parser.add_subparsers(dest="cmd")

    p_collect = sub.add_parser("collect", help="Coletar tendências por hashtags")
    p_collect.add_argument("--hashtags", required=True, help="Lista de hashtags separadas por vírgula")

    p_collect_users = sub.add_parser("collect_users", help="Coletar posts por usuários")
    p_collect_users.add_argument("--users", required=True, help="Lista de usernames separadas por vírgula")

    p_generate = sub.add_parser("generate", help="Gerar descrição, legenda e imagem a partir de URL")
    p_generate.add_argument("--image_url", required=True)
    p_generate.add_argument("--style", required=False)
    # Flags opcionais de Supabase para teste ad-hoc
    p_generate.add_argument("--supabase_url", required=False, help="Override da URL do Supabase")
    p_generate.add_argument("--supabase_service_key", required=False, help="Override da Service Key do Supabase")
    p_generate.add_argument("--supabase_bucket", required=False, help="Override do bucket do Supabase")

    p_unposted = sub.add_parser("unposted", help="Listar itens não postados do banco")
    p_unposted.add_argument("--limit", type=int, default=10)

    p_autopost = sub.add_parser("autopost", help="Gerar e publicar a partir do primeiro item não postado")
    p_autopost.add_argument("--style", required=False)

    p_multirun = sub.add_parser("multirun", help="Executa fluxo para múltiplas contas definidas em accounts.json")
    p_multirun.add_argument("--limit", type=int, default=1, help="Qtde de itens por conta")
    p_multirun.add_argument("--only", type=str, required=False, help="Rodar apenas uma conta pelo nome exato")

    p_clear = sub.add_parser("clear_cache", help="Limpa cache persistente do RapidAPI")
    p_clear.add_argument("--url-contains", dest="url_contains", type=str, default=None, help="Filtrar por texto no URL")
    p_clear.add_argument("--path", dest="path", type=str, default=None, help="Nome de arquivo de cache específico")
    p_clear.add_argument("--older", dest="older", type=int, default=None, help="Remover entradas mais antigas que N segundos")

    args = parser.parse_args()
    if args.cmd == "collect":
        hashtags = [h.strip() for h in args.hashtags.split(",") if h.strip()]
        cmd_collect(hashtags)
    elif args.cmd == "collect_users":
        cfg = load_config()
        users = [u.strip() for u in args.users.split(",") if u.strip()]
        inserted = collect_userposts(cfg["RAPIDAPI_KEY"], cfg["RAPIDAPI_HOST"], cfg["POSTGRES_DSN"], users)
        print(f"Coleta por usuários concluída. Novos itens inseridos: {inserted}")
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
                supabase_url=supa_url,
                supabase_service_key=supa_key,
                supabase_bucket=supa_bkt,
            )
            print("Resultado:", result)
        else:
            cfg = load_config()
            # Carregar prompts da conta Milton_Albanez para teste direto
            acc_milton = None
            try:
                with open("accounts.json", "r", encoding="utf-8") as f:
                    accounts = json.load(f)
                acc_milton = next((a for a in accounts if a.get("nome") == "Milton_Albanez"), None)
            except Exception:
                acc_milton = None
            result = generate_and_publish(
                openai_key=cfg["OPENAI_API_KEY"],
                replicate_token=cfg["REPLICATE_TOKEN"],
                instagram_business_id=cfg["INSTAGRAM_BUSINESS_ACCOUNT_ID"],
                instagram_access_token=cfg["INSTAGRAM_ACCESS_TOKEN"],
                telegram_bot_token=cfg["TELEGRAM_BOT_TOKEN"],
                telegram_chat_id=cfg["TELEGRAM_CHAT_ID"],
                source_image_url=args.image_url,
                caption_style=args.style,
                content_prompt=acc_milton.get("prompt_ia_geracao_conteudo") if acc_milton else None,
                caption_prompt=acc_milton.get("prompt_ia_legenda") if acc_milton else None,
                original_text=None,
            )
            print("Resultado:", result)
    elif args.cmd == "unposted":
        cfg = load_config()
        rows = Database(cfg["POSTGRES_DSN"]).list_unposted(args.limit)
        for r in rows:
            print(r)
    elif args.cmd == "autopost":
        cfg = load_config()
        db = Database(cfg["POSTGRES_DSN"]) 
        rows = db.list_unposted(1)
        if not rows:
            print("Nenhum item não postado disponível.")
            return
        item = rows[0]
        result = generate_and_publish(
            openai_key=cfg["OPENAI_API_KEY"],
            replicate_token=cfg["REPLICATE_TOKEN"],
            instagram_business_id=cfg["INSTAGRAM_BUSINESS_ACCOUNT_ID"],
            instagram_access_token=cfg["INSTAGRAM_ACCESS_TOKEN"],
            telegram_bot_token=cfg["TELEGRAM_BOT_TOKEN"],
            telegram_chat_id=cfg["TELEGRAM_CHAT_ID"],
            source_image_url=item["thumbnail_url"],
            caption_style=args.style,
        )
        print("Resultado:", result)
        if result.get("status") == "PUBLISHED":
            db.mark_posted(item["code"]) 
            print(f"Marcado como postado: {item['code']}")
    elif args.cmd == "multirun":
        cfg = load_config()
        # Ler contas
        with open("accounts.json", "r", encoding="utf-8") as f:
            accounts = json.load(f)
        for acc in accounts:
            nome = acc.get("nome")
            if getattr(args, "only", None) and nome != args.only:
                continue
            print(f"== Processando conta: {nome} ==")
            hashtags = acc.get("hashtags_pesquisa", [])
            users = acc.get("usernames", [])
            inserted = 0
            if hashtags:
                inserted += collect_hashtags(cfg["RAPIDAPI_KEY"], cfg["RAPIDAPI_HOST"], cfg["POSTGRES_DSN"], hashtags)
            if users:
                inserted += collect_userposts(cfg["RAPIDAPI_KEY"], cfg["RAPIDAPI_HOST"], cfg["POSTGRES_DSN"], users)
            print(f"Coleta concluída para {nome}. Novos itens: {inserted}")
            # Após coletar, gerar e publicar do banco filtrado por tags da conta
            db = Database(cfg["POSTGRES_DSN"]) 
            filter_tags = hashtags + users
            rows = db.list_unposted_by_tags(filter_tags, args.limit)

            # Validação: Supabase deve estar completo na conta; Instagram pode usar fallback do .env
            acc_instagram_id = acc.get("instagram_id") or cfg["INSTAGRAM_BUSINESS_ACCOUNT_ID"]
            acc_instagram_token = acc.get("instagram_access_token") or cfg["INSTAGRAM_ACCESS_TOKEN"]
            # Fallback para Supabase via variáveis de ambiente (não versionar segredos em accounts.json)
            acc_supa_url = acc.get("supabase_url") or cfg["SUPABASE_URL"]
            acc_supa_key = acc.get("supabase_service_key") or cfg["SUPABASE_SERVICE_KEY"]
            acc_supa_bucket = acc.get("supabase_bucket") or cfg["SUPABASE_BUCKET"]
            instagram_ok = bool(acc_instagram_id) and bool(acc_instagram_token)
            supabase_ok = bool(acc_supa_url) and bool(acc_supa_key) and bool(acc_supa_bucket)
            if not instagram_ok or not supabase_ok:
                print(
                    f"Dados incompletos para {nome}. Pulando geração/publicação. "
                    f"instagram_ok={instagram_ok}, supabase_ok={supabase_ok}"
                )
                continue
            for item in rows:
                result = generate_and_publish(
                    openai_key=acc.get("openai_api_key", cfg["OPENAI_API_KEY"]),
                    replicate_token=acc.get("replicate_token", cfg["REPLICATE_TOKEN"]),
                    instagram_business_id=acc_instagram_id,
                    instagram_access_token=acc_instagram_token,
                    telegram_bot_token=acc.get("telegram_bot_token", cfg["TELEGRAM_BOT_TOKEN"]),
                    telegram_chat_id=acc.get("telegram_chat_id", cfg["TELEGRAM_CHAT_ID"]),
                    source_image_url=item["thumbnail_url"],
                    caption_style=None,
                    content_prompt=acc.get("prompt_ia_geracao_conteudo"),
                    caption_prompt=acc.get("prompt_ia_legenda"),
                    original_text=item.get("prompt"),
                    disable_replicate=bool(acc.get("disable_replicate", False)),
                    supabase_url=acc_supa_url,
                    supabase_service_key=acc_supa_key,
                    supabase_bucket=acc_supa_bucket,
                )
                print("Resultado:", result)
                if result.get("status") == "PUBLISHED":
                    db.mark_posted(item["code"]) 
                    print(f"Marcado como postado: {item['code']}")
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
    else:
        parser.print_help()


if __name__ == "__main__":
    main()