# Agente Post Automático Instagram

Automatiza coleta de tendências, geração de imagens conceituais e publicação no Instagram, com coerência entre imagem e legenda.

## Requisitos
- Python 3.11+
- Conta do Instagram (Graph API): `INSTAGRAM_BUSINESS_ACCOUNT_ID`, `INSTAGRAM_ACCESS_TOKEN`
- RapidAPI (Instagram Scraper): `RAPIDAPI_KEY`, `RAPIDAPI_HOST`
- OpenAI: `OPENAI_API_KEY`
- Replicate: `REPLICATE_TOKEN`
- PostgreSQL: `POSTGRES_DSN`
- Supabase Storage (opcional p/ re-hospedar): `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, `SUPABASE_BUCKET`

## Instalação Local
1. Crie e ative venv
   - Windows: `python -m venv .venv && .venv\Scripts\activate`
2. Instale deps: `pip install -r requirements.txt`
3. Configure `.env` com as variáveis (veja Requisitos)
4. Execute um teste: `python src/main.py multirun --limit 1 --only Milton_Albanez`

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

## Licença
Uso pessoal do autor. Ajuste conforme seu contexto.