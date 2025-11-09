# LTM — Comparação Agente Post 9h vs 12h (Preenchido)

Comparação entre o serviço funcional "Agente Post 9h Auto Insta" e o serviço com falhas "Agente Post 12h Auto Insta 02", com base nas últimas 10 imagens e nos logs de build fornecidos. Inclui plano de correção passo a passo específico para o 12h.

## 1) Identificação e Ambiente
- Nome do serviço:
  - 9h: Agente Post 9h Auto Insta
  - 12h: Agente Post 12h Auto Insta 02
- Ambiente e região:
  - 9h: production — US East (Virginia)
  - 12h: production — US East (Virginia)
- Origem (GitHub/branch, Wait for CI):
  - 9h: Deploy via painel; origem padrão do repositório (Modal Build, compatível)
  - 12h: Nixpacks v1.38.0, "Using Nixpacks"; start detectado; deploy via painel
- Último deploy (tempo e método: CLI/painel):
  - 9h: recente, com logs de publicação
  - 12h: Nov 5, 2025 10:04 PM — painel — "Deployment successful"

## 2) Agendamento e Automação
- Horário/cron (UTC e BRT):
  - 9h: Cron ativo no serviço de aplicação; horário consistente (ex.: 12:00 UTC ≈ 09:00 BRT)
  - 12h: Cron configurado no serviço de banco (Postgres Destino 02) — incorreto; objetivo é 12:00 BRT (15:00 UTC)
- Próxima execução exibida:
  - 9h: Exibe próxima execução diária correta
  - 12h: Não há próxima execução na app; cron atrelado ao DB
- Histórico de execuções (duração média, falhas):
  - 9h: Execuções com publicação concluída, `status: PUBLISHED`, Telegram OK
  - 12h: Sem execuções da app; banco sem tabelas; ausência de logs de publicação

## 3) Deploy/Runtime
- Start Command:
  - 9h: `python -m src.main autopost`
  - 12h: `python railway_scheduler.py` (pelos build logs) — divergente do fluxo de autopost
- Healthcheck Path:
  - 9h: `/health` no serviço de aplicação
  - 12h: Healthcheck HTTP configurado indevidamente no serviço de banco (não aplicável a Postgres)
- Restart Policy e Max Retries:
  - 9h: On Failure, Max Retries 10
  - 12h: On Failure, Max Retries 10 — OK
- Serverless / Teardown:
  - 9h: Desabilitado para app
  - 12h: DB com opções extras (serverless/teardown) não necessárias
- Build Environment (Modal/New) e avisos:
  - 9h: Modal Build Environment ok
  - 12h: Modal Build habilitado com aviso; Nixpacks v1.38.0 — sem problema direto
- Resource Limits (CPU/Mem):
  - 9h: Memória adequada (ex.: 8GB)
  - 12h: Memória 8GB — OK
- Networking (público e interno):
  - 9h: App expõe endpoint `/health` e usa rede interna para DB
  - 12h: Postgres com Public Networking (ex.: `trolley.proxy.rlwy.net`) e Private (`postgres.rlwy.internal`); porta pública indica 5433 — possível mismatch vs 5432

## 4) Variáveis — Aplicação
Estado resumido e diferenças observadas.
- Core:
  - `OPENAI_API_KEY` — 9h: presente | 12h: ausente/indefinido (confirmar)
  - `REPLICATE_TOKEN` — 9h: presente | 12h: ausente
  - `INSTAGRAM_BUSINESS_ACCOUNT_ID` — 9h: presente | 12h: ausente
  - `INSTAGRAM_ACCESS_TOKEN` — 9h: presente | 12h: presente
  - `TELEGRAM_BOT_TOKEN` — 9h: presente | 12h: presente
  - `TELEGRAM_CHAT_ID` — 9h: presente | 12h: presente
- RapidAPI:
  - `RAPIDAPI_KEY`, `RAPIDAPI_HOST`, `RAPIDAPI_ALT_HOSTS`, `RAPIDAPI_RPM` — 9h: configurado | 12h: parcial/ausente
- Supabase:
  - `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, `SUPABASE_BUCKET`, `ACCESS_TOKEN`, `ANON_KEY`, `PROJECT_REF`, `DB_URL` — 9h: completo | 12h: parcial/ausente
- Ambiente e controle:
  - `RAILWAY_ENVIRONMENT`, `PYTHONUNBUFFERED`, `TZ` — 9h: consistente (`TZ=America/Sao_Paulo`) | 12h: `TZ` a confirmar
- Instagram (tunings):
  - `INSTAGRAM_MAX_POLLING_CHECKS`, `INSTAGRAM_MAX_RETRIES`, `INSTAGRAM_POLLING_INTERVAL`, `INSTAGRAM_TIMEOUT` — 9h: definidos | 12h: não padronizados
- Outros (fallback/estética):
  - `ACCOUNT_NAME_DEFAULT`, `SOURCE_IMAGE_URL_DEFAULT`, `DISABLE_REPLICATE`, `STORIES_BACKGROUND_TYPE`, `WEEKLY_THEMES_ENABLED` — 9h: definidos | 12h: não padronizados

## 5) Variáveis — Banco (Postgres)
- `DATABASE_URL`/`POSTGRES_DSN` no app — 9h: presente por referência ao serviço de DB | 12h: ausente na app (não referenciado)
- Serviço Postgres (credenciais e variáveis geradas) — 9h: padrão Railway | 12h: 13 variáveis padrão presentes (`PGHOST`, `PGPORT`, `PGUSER`, `POSTGRES_*`, etc.)

## 6) Logs — Padrões Observados
- 9h (referência):
  - Boot/execução de `autopost`, fallback Standalone quando DB ausente, tema do dia, testes A/B, `status: PUBLISHED`, `telegram_sent: True`.
- 12h (build fornecido):
  - Nixpacks v1.38.0; criação de venv e `pip install -r requirements.txt` OK (73.77s)
  - `start │ python railway_scheduler.py` — indica comando de início divergente
  - Sem erros de build; ausência de logs de execução de publicação após deploy
- 12h (observabilidade):
  - Falta de logs da app; cron indevido no DB; banco vazio (sem tabelas)

## 7) Diferenças Críticas e Causas Prováveis
- Variáveis ausentes (Core/Supabase/RapidAPI) no 12h comprometem fluxos externos
- Start Command divergente (`railway_scheduler.py` vs `python -m src.main autopost`)
- Cron e Healthcheck configurados no serviço de DB (em vez da app)
- Banco não referenciado pela app (`DATABASE_URL` ausente por Variable Reference)
- Banco vazio (sem schema), gerando falhas de leitura/escrita
- Possível mismatch de porta pública (5433) vs padrão (5432) — evitar uso público; preferir rede interna

## 8) Plano de Correção Passo a Passo — 12h
- Mover o Cron para o serviço da aplicação 12h:
  - Architecture → selecione a app “Agente Post 12h Auto Insta 02”
  - Settings → Deploy → Cron Schedule → `0 15 * * *` com `TZ=America/Sao_Paulo` (12h BRT)
  - Remover Cron do serviço Postgres
- Ajustar Start Command da app:
  - Settings → Deploy → Start Command → `python -m src.main autopost`
  - Alternativa: manter `railway_scheduler.py` se ele invocar `autopost`, mas padronizar o fluxo principal
- Healthcheck correto:
  - App: `Healthcheck Path` → `/health`
  - DB: remover `Healthcheck Path` HTTP; usar readiness padrão do container
- Referenciar o banco na app (Variable Reference):
  - App → Variables → “Add Variable Reference” → selecione `DATABASE_URL` do “Postgres Destino 02”
  - Preferir endpoint interno `postgres.rlwy.internal:5432`; considerar desabilitar Public Networking do DB se não for necessário
- Criar o schema do banco:
  - Executar `python scripts/migrate_db.py` (Run Command) na app
  - Validar com `scripts/db_inspect.py` ou pelo painel (Database → Data)
- Padronizar variáveis críticas na app:
  - Definir/checar `OPENAI_API_KEY`, `REPLICATE_TOKEN`, `INSTAGRAM_BUSINESS_ACCOUNT_ID`, `INSTAGRAM_ACCESS_TOKEN`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`
  - Setar `TZ=America/Sao_Paulo`
- Validações pós-correção:
  - Tail de logs da app (service filter) e ver eventos de schedule, início de pipeline, e `status: PUBLISHED`
  - Healthcheck respondendo 200 em `/health`
  - Tabelas presentes e acessíveis no DB

---

Documento preenchido com base nas capturas e nos logs; usar o checklist de correção para execução no dashboard.