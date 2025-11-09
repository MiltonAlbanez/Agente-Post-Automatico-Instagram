# 🚀 Instruções de Deploy no Railway — Fluxo Padrão Atual

Este guia documenta o fluxo “Padrão” adotado no Railway para evitar dúvidas futuras no LTM. Inclui builder, `startCommand`, healthcheck, variáveis de ambiente e configuração de cron/backup.

## Visão Geral
- Builder: selecione “Padrão” no Railway.
- Comando de inicialização (`railway.json > deploy.startCommand`):
  - `bash -lc "python railway_cron_diagnostic.py && python cron_lock_system.py cleanup && (python main.py autopost &) && exec gunicorn -w 1 -k gthread -b 0.0.0.0:${PORT:-8000} health_server:app"`
- Healthcheck: `healthcheckPath` definido para `/healthz`.
- Serviços: diagnóstico inicial, limpeza de locks, `autopost` em segundo plano e servidor de saúde (`gunicorn` + `health_server:app`).

## Passo a Passo de Deploy
- 1) Confirmar builder “Padrão” e `requirements.txt` com dependências de runtime (ex.: `gunicorn`, `flask`, `psycopg[binary]`).
- 2) Garantir que o `railway.json` está presente com o `startCommand` acima e `healthcheckPath=/healthz`.
- 3) Definir variáveis de ambiente no serviço principal (veja “Padrão de Ambiente” abaixo):
  - Banco: `DATABASE_URL` (preferencial) ou `POSTGRES_DSN`.
  - APIs: `OPENAI_API_KEY`, `INSTAGRAM_*`, `TELEGRAM_*`, `REPLICATE_TOKEN` (se usar geração de imagem).
- 4) Deploy e validação:
  - Verificar em `Deployments` que o build e start concluíram.
  - Acessar `/healthz` e `/health` do serviço para confirmar saúde.
  - Conferir logs do diagnóstico inicial e execução do `autopost`.

## Health Server e Endpoints
- `health_server:app` expõe:
  - `/healthz` (healthcheck), `/health`, `/status`, `/metrics` e `/health/dependencies`.
- O `railway.json` já usa `/healthz` como healthcheck do serviço.

## Cron Jobs e Agendamento (UI do Railway)
- Cron jobs são configurados exclusivamente na interface web do Railway (não via arquivo).
- Padrões comuns:
  - Feed: horários em UTC refletindo 06h, 12h, 19h BRT.
  - Stories: horários em UTC refletindo 09h, 15h, 21h BRT.
- Variável opcional `AUTOCMD` pode ser usada em serviços adicionais para controlar execuções específicas (ex.: `autopost --stories`). No serviço principal, o `startCommand` já aciona `autopost` em segundo plano.

## Backup Automático (Cron One-Off)
- Crie um serviço dedicado `backup-cron` e configure os schedules na UI:
  - Diário: `0 2 * * *` com comando `python scripts/run_oneoff_backup.py --type daily`.
  - Semanal: `0 3 * * 0` com comando `python scripts/run_oneoff_backup.py --type full`.
- Saída esperada: linha `Backup concluído: <caminho>` nos logs do job.
- Os backups são gravados em `backups/` com política de retenção definida em `config/backup_config.json`.

## Padrão de Ambiente (resumo)
- Mínimo recomendado por serviço/schedule:
  - `DATABASE_URL` ou `POSTGRES_DSN`, `OPENAI_API_KEY`, `INSTAGRAM_BUSINESS_ACCOUNT_ID`, `INSTAGRAM_ACCESS_TOKEN`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `REPLICATE_TOKEN` (se aplicável).
- Para a lista completa e padronização entre schedules, consulte `RAILWAY_ENV_STANDARD.md`.

## Checklist de Validação Pós-Deploy
- `railway.json` com `startCommand` e `healthcheckPath` corretos.
- Builder “Padrão” selecionado no Railway.
- Variáveis de ambiente presentes e válidas.
- `/healthz` respondendo 200; `/metrics` e `/status` acessíveis.
- Logs mostram diagnóstico, limpeza de locks e `autopost` iniciado.
- Serviço `backup-cron` existe e está com schedules e comandos corretos.

## Troubleshooting Rápido
- Healthcheck falhando: validar dependências (`requirements.txt`) e variáveis obrigatórias.
- Falhas de DB: confirmar `DATABASE_URL/POSTGRES_DSN` e acesso de rede.
- Rate limit 429: consultar análise em `railway_environment_diagnosis.py` e ajustar cadence.
- Backup ausente: revisar serviço `backup-cron` e horários na UI; verificar logs por `Backup concluído:`.

## Observações
- Removemos referências ao NIXPACKS; o Railway “Padrão” é a base.
- Mantenha apenas uma fonte de verdade para o comando de inicialização (`railway.json`).