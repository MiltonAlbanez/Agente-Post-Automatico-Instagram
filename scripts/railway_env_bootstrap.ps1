<#
 Script: scripts/railway_env_bootstrap.ps1
 Objetivo: Padronizar configuração de variáveis no Railway para todo o stack,
           incluindo Supabase, OpenAI, Instagram e Telegram.
 Uso:
   1) Instale o Railway CLI e faça login: `railway login`
   2) Selecione o projeto correto: `railway link`
   3) Execute este script no PowerShell: `./scripts/railway_env_bootstrap.ps1`
   4) Revise os valores e ajuste conforme seu ambiente.
#>

Write-Host "== Configurando variáveis padrão no Railway =="

# === VARIÁVEIS BÁSICAS DO SISTEMA ===
railway variables set RAILWAY_ENVIRONMENT="production"
railway variables set TZ="America/Sao_Paulo"
railway variables set PYTHONUNBUFFERED="1"

# === OPENAI / RAPIDAPI / REPLICATE ===
railway variables set OPENAI_API_KEY="<sua_chave_openai>"
railway variables set RAPIDAPI_KEY="<sua_chave_rapidapi>"
railway variables set RAPIDAPI_HOST="instagram-scraper-api2.p.rapidapi.com"
railway variables set RAPIDAPI_ALT_HOSTS="instagram-scraper.p.rapidapi.com,instagram-scraper-api.p.rapidapi.com,instagram-bulk-scraper-latest.p.rapidapi.com"
railway variables set REPLICATE_TOKEN="<seu_token_replicate>"

# === TELEGRAM ===
railway variables set TELEGRAM_BOT_TOKEN="<seu_token_bot_telegram>"
railway variables set TELEGRAM_CHAT_ID="<seu_chat_id_telegram>"

# === INSTAGRAM (Conta principal) ===
railway variables set INSTAGRAM_BUSINESS_ACCOUNT_ID="<seu_instagram_business_id>"
railway variables set INSTAGRAM_ACCESS_TOKEN="<seu_instagram_access_token>"

# === BANCO DE DADOS ===
# Use POSTGRES_DSN se for banco próprio; Railway geralmente fornece DATABASE_URL automaticamente
railway variables set POSTGRES_DSN="<seu_postgres_dsn_ou_vazio>"

# === SUPABASE ===
railway variables set SUPABASE_URL="<sua_url_supabase>"
railway variables set SUPABASE_SERVICE_KEY="<sua_service_key_supabase>"
railway variables set SUPABASE_BUCKET="instagram-images"

Write-Host "✅ Variáveis padrão aplicadas. Revise e ajuste as credenciais sensíveis."