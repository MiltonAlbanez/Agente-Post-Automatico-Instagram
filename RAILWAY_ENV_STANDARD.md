# Padrão de Ambiente no Railway — Fluxo Padrão e Variáveis

Este documento consolida as variáveis de ambiente e observações operacionais para o fluxo “Padrão” no Railway, cobrindo serviço principal, cron schedules e backup.

## Fluxo Padrão (Serviço Principal)
- Builder: selecione “Padrão”.
- `startCommand` (em `railway.json`):
  - `bash -lc "python railway_cron_diagnostic.py && python cron_lock_system.py cleanup && (python main.py autopost &) && exec gunicorn -w 1 -k gthread -b 0.0.0.0:${PORT:-8000} health_server:app"`
- Healthcheck: `healthcheckPath` para `/healthz`.
- Resultado: diagnóstico inicial, limpeza de locks, `autopost` em background e health server ativo.

## Conjunto Canônico de Variáveis
- Núcleo de execução:
  - `DATABASE_URL` — conexão DB padrão do Railway (preferencial)
  - `POSTGRES_DSN` — alternativa ao `DATABASE_URL`
  - `OPENAI_API_KEY` — geração de conteúdo
  - `INSTAGRAM_BUSINESS_ACCOUNT_ID`, `INSTAGRAM_ACCESS_TOKEN` — Graph API
  - `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` — alertas
  - `REPLICATE_TOKEN` — geração de imagem (opcional)
- Suporte e fallbacks:
  - `RAPIDAPI_KEY`, `RAPIDAPI_HOST`, `RAPIDAPI_ALT_HOSTS` (opcional)
  - `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, `SUPABASE_BUCKET` (opcional)
  - `RAILWAY_ENVIRONMENT` — rótulo (ex.: `production`)
  - `ACCOUNT_NAME_DEFAULT`, `SOURCE_IMAGE_URL_DEFAULT` (fallbacks)
  - `DISABLE_REPLICATE` — `true/false` (opcional)
  - `STORIES_BACKGROUND_TYPE` — `gradient/blurred` (opcional)
  - `WEEKLY_THEMES_ENABLED` — `true/false` (opcional)

Observação: mantenha a mesma lista e valores entre serviços/schedules para consistência operacional.

## Cron Schedules (UI do Railway)
- Configuração somente via interface web.
- Serviços dedicados (exemplos):
  - Feed: horários em UTC equivalentes a 06h, 12h, 19h BRT.
  - Stories: horários em UTC equivalentes a 09h, 15h, 21h BRT.
- Variável opcional por serviço: `AUTOCMD` (ex.: `autopost --stories`). No serviço principal não é necessária.

## Backup Automático
- Serviço separado `backup-cron` com schedules:
  - Diário (02:00 UTC): `python scripts/run_oneoff_backup.py --type daily`
  - Semanal (Domingo 03:00 UTC): `python scripts/run_oneoff_backup.py --type full`
- Retenção e compressão: controladas por `config/backup_config.json`.
- Validação: procurar `Backup concluído:` nos logs do cron.

## Verificações Rápidas
- Telegram: sem `TELEGRAM_*` não há alertas.
- Instagram: sem `INSTAGRAM_*` o post falha.
- Geração: sem `OPENAI_API_KEY` e `REPLICATE_TOKEN`, cai em fallback.
- DB: `DATABASE_URL/POSTGRES_DSN` presentes evitam falhas.
- Health: `/healthz` deve responder 200; `/metrics` e `/status` ajudam diagnóstico.

## Como sincronizar (CLI)
- `railway login`, `railway link` e aplicar variáveis com scripts de bootstrap (se existirem).
- Alternativa: definir manualmente via UI.
- Confirmar que todos os serviços/schedules compartilham o mesmo conjunto de variáveis.

## Boas práticas
- Não versionar segredos em plaintext.
- Usar placeholders em arquivos de referência.
- Manter `.env.example` como contrato de configuração.