# Checklist de Correção — Agente Post 12h Auto Insta 02 (Railway)

Aplicar diretamente no dashboard, seguindo a ordem. Objetivo: restaurar execução diária às 12h BRT (15:00 UTC) com publicação concluída.

## 1) Cron e Start Command (Aplicação)
- Architecture → selecione o serviço de aplicação "Agente Post 12h Auto Insta 02".
- Settings → Deploy → Cron Schedule → definir `0 15 * * *` e `TZ=America/Sao_Paulo`.
- Settings → Deploy → Start Command → `python -m src.main autopost`.
- Remover cron do serviço de Postgres (se presente).

## 2) Healthcheck e Restart
- App: `Healthcheck Path` → `/health`.
- DB: remover `Healthcheck Path` HTTP; manter readiness padrão.
- Restart Policy: On Failure; Max Retries: 10 (confirmar).

## 3) Banco de Dados (Referência e Networking)
- App → Variables → “Add Variable Reference” → apontar `DATABASE_URL` para "Postgres Destino 02".
- Confirmar uso de endpoint interno `postgres.rlwy.internal:5432`.
- Desabilitar Public Networking do Postgres (se não requerido externamente).

## 4) Criar/Validar Schema
- App → Run Command → `python scripts/migrate_db.py`.
- Validar em Database → Data se tabelas foram criadas.

## 5) Variáveis Críticas (Aplicação)
- Definir/validar: `OPENAI_API_KEY`, `REPLICATE_TOKEN`, `INSTAGRAM_BUSINESS_ACCOUNT_ID`, `INSTAGRAM_ACCESS_TOKEN`.
- Definir/validar: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`.
- Definir/validar: `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`.
- Definir: `TZ=America/Sao_Paulo`.
- Padronizar conforme `RAILWAY_ENV_STANDARD.md`.

## 6) Teste Controlado
- App → Run Command → `python -m src.main autopost --dry-run`.
- Ver logs com filtro do serviço: eventos de schedule, início de pipeline, e ausência de erros.

## 7) Validação Final
- Tail de logs no horário agendado; buscar `status: PUBLISHED`.
- Healthcheck `/health` retornando 200.
- Banco com tabelas acessíveis e escritas recentes.

## 8) Observações
- Se persistirem erros de Graph API, revisar `INSTAGRAM_*` e renovar tokens.
- Se o build alterar o Start Command automaticamente (Nixpacks), forçar manualmente no painel.