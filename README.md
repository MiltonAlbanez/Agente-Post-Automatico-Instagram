# Agente Post Automático Instagram

Automatiza coleta de tendências, geração de imagens conceituais e publicação no Instagram, com coerência entre imagem e legenda.

## Requisitos
- Python 3.11+
- Conta do Instagram (Graph API): `INSTAGRAM_BUSINESS_ACCOUNT_ID`, `INSTAGRAM_ACCESS_TOKEN`
- RapidAPI (Instagram Scraper): `RAPIDAPI_KEY`, `RAPIDAPI_HOST`
- OpenAI: `OPENAI_API_KEY`
- Replicate: `REPLICATE_TOKEN`
- PostgreSQL: `POSTGRES_DSN`
  - No Railway, pode usar `DATABASE_URL` (fallback automático)
- Supabase Storage (opcional p/ re-hospedar): `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, `SUPABASE_BUCKET`

## Instalação Local
1. Crie e ative venv
   - Windows: `python -m venv .venv && .venv\Scripts\activate`
2. Instale deps: `pip install -r requirements.txt`
3. Configure `.env` com as variáveis (veja Requisitos)
4. Execute um teste: `python src/main.py multirun --limit 1 --only Milton_Albanez`

### Exemplo de `.env`
```
# Instagram Graph API
INSTAGRAM_BUSINESS_ACCOUNT_ID=xxxxxxxxxxxxxxxx
INSTAGRAM_ACCESS_TOKEN=EAAB...long_token

# Telegram (opcional)
TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
TELEGRAM_CHAT_ID=123456789

# RapidAPI
RAPIDAPI_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
RAPIDAPI_HOST=instagram-scraper-api2.p.rapidapi.com

# OpenAI e Replicate
OPENAI_API_KEY=sk-xxxxx
REPLICATE_TOKEN=r8_xxxxx

# Banco de Dados
POSTGRES_DSN=postgresql://usuario:senha@host:5432/dbname
# Railway fallback automático
# DATABASE_URL=postgresql://usuario:senha@host:5432/dbname

# Supabase Storage (opcional)
SUPABASE_URL=https://SEU_REF.supabase.co
SUPABASE_SERVICE_KEY=service_role_key
SUPABASE_BUCKET=instagram-images
```

## Estrutura
- `accounts.json`: define contas, hashtags/usernames, prompts e flags.
- `src/services/*`: clientes (Instagram, Replicate, RapidAPI, Supabase, OpenAI).
- `src/pipeline/*`: fluxo de coleta e geração/publicação.
- `src/main.py`: CLI com comandos `collect`, `collect_users`, `generate`, `multirun`, `clear_cache`.

## Agendamento Local (Windows)
- Use `scripts/run_multirun.ps1` com agendador do Windows; PC precisa estar ligado (sem hibernação).

## Deploy no Railway
1. Link ao projeto: `railway link -p <PROJECT_ID>`
2. Configure Variables com os segredos dos Requisitos.
   - Banco: defina `POSTGRES_DSN` ou use `DATABASE_URL` do add-on PostgreSQL
3. Faça deploy: `railway up`
4. Procfile já define `worker: python src/main.py multirun --limit 1 --only Milton_Albanez`.
5. Cron Job (UTC): 
   - Command: `python src/main.py multirun --limit 1 --only Milton_Albanez`
   - Ajuste horário conforme sua timezone (ex.: 09:00 UTC ≈ 06:00 BRT).

## Dicas e Observações
- RapidAPI pode retornar 429; ajuste limite/horários e diversifique hashtags.
- Tokens do Instagram expiram; mantenha renovação.
- Logs: veja `logs/` localmente ou o dashboard do Railway.
- `accounts.json` não deve conter segredos; Supabase usa fallback de variáveis de ambiente.

## Comandos úteis
- Coleta por hashtags: `python src/main.py collect --hashtags empreendedorismo,pnl`
- Coleta por usuários: `python src/main.py collect_users --users milton_albanez`
- Gerar a partir de URL: `python src/main.py generate --image_url <url>`
- Limpar cache RapidAPI: `python src/main.py clear_cache --older 3600`
 - Listar não postados (Railway - Windows): `railway run python src/main.py unposted --limit 10`
 - Publicar primeiro não postado (Railway - Windows): `railway run python src/main.py autopost --style "isometric, minimalista"`
 - Dica: defina variáveis úteis via CLI (sem disparar deploy):
   `railway variables --set "ACCOUNT_NAME=Milton_Albanez" --set "LIMIT=1" --set "STYLE=isometric, minimalista" --skip-deploys`

## Licença
Uso pessoal do autor. Ajuste conforme seu contexto.