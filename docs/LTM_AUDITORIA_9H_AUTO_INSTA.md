# Auditoria LTM — Agente Post 9h Auto Insta (Dashboard)

Este documento consolida todas as configurações e evidências visíveis nas 10 capturas do dashboard do serviço "Agente Post 9h Auto Insta". A estrutura prioriza identificação rápida de discrepâncias e serve como base para comparação com o serviço "Agente Post 12h Auto Insta 02".

## Identificação do Serviço
- Nome: `Agente Post 9h Auto Insta`
- Ambiente: `production`
- Região de deploy: `US East (Virginia, USA)`
- Origem (Source): integrado a GitHub (branch `main`); opção "Wait for CI" ativa (imagem de Settings/GitHub)
- Último deploy: "railway up" (completado há 2 semanas) — via CLI

## Agendamento e Automação
- Próxima execução: em 12 horas
- Horário de execução: `12:00 pm (UTC)` (equivalente a `09:00 BRT`)
- Histórico de execuções recentes:
  - 2025-11-05 09:14 — `railway up` (41s, status verde)
  - 2025-11-04 09:04 — `railway up` (41s, status verde)
  - 2025-11-03 09:03 — `railway up` (45s, status verde)
  - 2025-11-02 09:03 — `railway up` (42s, status verde)
  - 2025-11-01 09:04 — `railway up` (39s, status verde)
  - Outras execuções entre 10/16 e 10/31 mostrando tempos entre 33s–46s e execuções longas de correção (ex.: 4h 6m, 8h 31m, 23h 58m) com mensagens "Fix"/"feat" relacionadas a fallback e logs detalhados

## Configurações de Deploy/Runtime
- Start Command (custom): `python -m src.main autopost`
- Healthcheck Path: `/health`
- Restart Policy: `On Failure`, `Max Retries: 10`
- Serverless: desativado
- Teardown: desativado
- Resource Limits:
  - CPU: conforme plano (não explícito na captura; slider indica limite do plano)
  - Memória: `8 GB` (Plan limit: 8 GB)
- Build Environment: `Modal Build Environment (New)` (aviso de compatibilidade)
- Networking:
  - Público: domínio/porta expostos pelo Railway (ex.: `*.proxy.rlwy.net:5432` para Postgres; app exposto via rota padrão do serviço)
  - Privado (internal): `*.railway.internal`

## Variáveis — Serviço de Aplicação (captura anterior com 25 variáveis)
- Presentes (principais):
  - `AUTOCMD`
  - `INSTAGRAM_ACCESS_TOKEN`
  - `INSTAGRAM_BUSINESS_ACCOUNT_ID`
  - `OPENAI_API_KEY`
  - `PYTHONUNBUFFERED`
  - `RAILWAY_ENVIRONMENT`
  - `RAPIDAPI_KEY`, `RAPIDAPI_HOST`, `RAPIDAPI_ALT_HOSTS`, `RAPIDAPI_RPM`
  - `REPLICATE_TOKEN`
  - `SUPABASE_*` (`URL`, `SERVICE_KEY`, `BUCKET`, `ACCESS_TOKEN`, `ANON_KEY`, `PROJECT_REF`, `DB_URL`)
  - `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`
  - `TZ`
- Parâmetros Instagram adicionais (presentes na captura):
  - `INSTAGRAM_MAX_POLLING_CHECKS`, `INSTAGRAM_MAX_RETRIES`, `INSTAGRAM_POLLING_INTERVAL`, `INSTAGRAM_TIMEOUT`

## Variáveis — Serviço de Banco (Postgres)
- Captura mostra 13 variáveis geradas pelo Railway:
  - `DATABASE_PUBLIC_URL`, `DATABASE_URL`
  - `PGDATA`, `PGDATABASE`, `PGHOST`, `PGPASSWORD`, `PGPORT`, `PGUSER`
  - `POSTGRES_DB`, `POSTGRES_PASSWORD`, `POSTGRES_USER`
  - `RAILWAY_DEPLOYMENT_DRAINING_*`, `SSL_CERT_DAYS`

## Arquitetura — Postgres
- Serviço: `Postgres` (deploys via Docker Image; volumes associados)
- Tabelas visíveis: `test_connect...`, `top_trends`
- Botão "Connect" disponível e abas: Deployments, Database, Backups, Variables, Metrics, Settings

## Logs — Execução 9h (exemplo detalhado)
- Boot: `Starting Container`
- Execução automática: `Executando publicação única: python /venv/bin/python src/main.py autopost`
- Aviso: `POSTGRES_DSN/DATABASE_URL não definido. Usando fallback Standalone para garantir publicação.`
- Fallback: `gerando conteúdo (temático)` para garantir postagem no horário
- Conta: `Milton Albanez`
- Tema: `Motivacional`
- Imagem: Unsplash (link com `auto=format` e crop)
- Testes A/B: formatos de conteúdo (Formato Pergunta), estratégias de hashtag (Hashtags Nicho), estilos de imagem (Estilo Minimalista)
- Sistema Temático Semanal: aplicado
- Tema do dia: `Quarta-feira (Motivação, Matriz Eisenhower)`
- Foco: `Ferramenta/Modelo`
- Resultado: status `PUBLISHED`, `telegram_sent: True`, `replicate_sent: 'DISABLED'`, `generated_image_url` em Supabase Storage, `media_id` válido
- Conclusão: `Execução concluída com sucesso`

## Fluxo de Trabalho do Agente (deduzido dos logs + variáveis)
- Gatilho de cron em `12:00 UTC` ➜ inicializa contêiner ➜ roda comando `autopost`
- Valida ambiente (Telegram/Instagram tokens) e storage (Supabase)
- Se `POSTGRES_DSN/DATABASE_URL` ausente ou indisponível ➜ entra em `Standalone Fallback`
- Aplica Sistema Temático Semanal + testes A/B + seleção de imagem (Unsplash)
- Publica via Graph API do Instagram ➜ envia notificação Telegram ➜ registra `media_id` e URL gerada
- Healthcheck `/health` valida após o deploy; política de restart em falhas

## Personalizações e Especiais
- Parâmetros finos do Instagram (`MAX_POLLING_CHECKS`, `MAX_RETRIES`, `POLLING_INTERVAL`, `TIMEOUT`)
- Integração Supabase completa (`URL`, `SERVICE_KEY`, `BUCKET`, etc.)
- Uso de `TZ` alinhado ao BRT através de execução em `12:00 UTC`
- Fallback Standalone: mecanismo explícito para garantir publicação em caso de ausência de DB

## Observações de Risco/Qualidade
- Quando `DATABASE_URL` não está configurado no app, o serviço opera em modo Standalone sem persistir tracking completo — recomendável manter `DATABASE_URL` disponível para evitar perda de telemetria/estado.
- `REPLICATE_TOKEN` pode estar desativado em determinadas execuções (logs mostram `replicate_sent: 'DISABLED'`); confirmar objetivo (texto-only) vs. imagem gerada.
- `Wait for CI` habilitado garante sincronização pós-CI; manter coerência com o fluxo de publicação automatizada.

---

Este documento será usado como referência para comparação com o serviço "Agente Post 12h Auto Insta 02".