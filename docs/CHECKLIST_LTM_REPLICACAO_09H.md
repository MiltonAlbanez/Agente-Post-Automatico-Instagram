# CHECKLIST LTM — Replicação do Post Stories 09:00 BRT (Railway)

Objetivo: replicar a configuração comprovadamente bem-sucedida do Post Stories das 09:00 BRT para outras contas e serviços no Railway, assegurando consistência técnica, conformidade com documentação LTM, e monitoramento confiável.

## 1) Identificação do Horário e Conversão

- Horário alvo: 09:00 BRT (UTC−03)
- Conversão para UTC: 12:00 UTC
- Expressão cron (UTC): `0 12 * * *`

## 2) Comandos Essenciais (Railway CLI)

- Definir variáveis obrigatórias por serviço:
  - `railway variables set OPENAI_API_KEY=<chave>`
  - `railway variables set RAPIDAPI_KEY=<chave>`
  - `railway variables set INSTAGRAM_ACCESS_TOKEN=<token>`
  - `railway variables set INSTAGRAM_BUSINESS_ACCOUNT_ID=<id>`
  - `railway variables set TELEGRAM_BOT_TOKEN=<token>`
  - `railway variables set TELEGRAM_CHAT_ID=<id>`
  - `railway variables set SUPABASE_URL=<url>`
  - `railway variables set SUPABASE_SERVICE_KEY=<key>`

- Definir variáveis opcionais (recomendadas):
  - `railway variables set ENVIRONMENT=railway`
  - `railway variables set DISABLE_REPLICATE=true`
  - `railway variables set WEEKLY_THEMES_ENABLED=true`
  - `railway variables set STORIES_BACKGROUND_TYPE=gradient`
  - `railway variables set STORIES_TEXT_POSITION=auto`

- Agendar execução (cron em UTC):
  - `railway cron add "0 12 * * *" -- command "python railway_scheduler.py"`

## 3) Template de Replicação (Estrutura)

Preencha e salve o arquivo `railway_env_template_replicacao_09h.json` (gerado neste repositório) para cada serviço/conta.

Campos principais:

- ENV (obrigatório): chaves de integração (OpenAI, Instagram, Telegram, Supabase) e flags de execução.
- SLOTS: definição dos horários e parâmetros por slot (ex.: `stories_09_brt`).
- ACCOUNTS: identificação por conta (nome, `instagram_business_account_id`, `instagram_access_token`, `telegram_chat_id`).

## 4) Aplicação do Checklist (Passo a Passo)

- Verificar conta-alvo e presença em `accounts.json`.
- Preencher `railway_env_template_replicacao_09h.json` com valores da conta.
- Configurar variáveis obrigatórias no serviço do Railway (ver seção 2).
- Ajustar flags opcionais para Stories (background, posição de texto, temas semanais).
- Criar/validar o cron `0 12 * * *` com comando `python railway_scheduler.py`.
- Validar localmente com variáveis mínimas (OPENAI_API_KEY e RAPIDAPI_KEY) para boot do scheduler.
- Subir logs e ativar monitoramento contínuo com `monitor_railway_logs.py --monitor --interval 30 --alerts`.

## 5) Evidências e Validações

- Confirmar no log:
  - Ambiente: `ENVIRONMENT=railway`
  - Variáveis OK: sem erros de `OPENAI_API_KEY` ou `RAPIDAPI_KEY` ausentes.
  - Contas carregadas: leitura de `accounts.json` com 1+ contas.
  - Jobs agendados: 7 agendamentos (FEED e STORIES) incluindo `stories_09_brt`.
  - Entrada em loop principal com próxima execução às 12:00 UTC.
  - Publicação bem-sucedida das Stories e notificação Telegram.

- Em caso de falha:
  - Revisar variáveis obrigatórias no Railway (tokens/ids).
  - Verificar flags opcionais de Stories (background, posicionamento de texto, temas semanais).
  - Checar acessos (Instagram API, Supabase, Telegram) e renovação de tokens.

## 6) Documentação LTM (Conformidade)

- Aderência à documentação: `RAILWAY_ENV_STANDARD.md`, `INSTRUCOES_DEPLOY_RAILWAY.md`, `CONFIGURACAO_CRON_RAILWAY.md`.
- Auditoria: `AUDITORIA_VARIAVEIS_RAILWAY.md`, `AUDITORIA_CHAT_LTM.md`.

## 7) Fatores Críticos de Sucesso

- Variáveis obrigatórias válidas e ativas (OpenAI, Instagram, Telegram, Supabase).
- Conversão correta de BRT→UTC e agendamento cron em UTC.
- Flags adequadas para Stories (background/posição de texto/temas).
- Monitoramento contínuo de logs com alertas.

## 8) Recomendações de Replicação

- Criar um serviço por conta no Railway com isolamento de variáveis.
- Reutilizar `railway_env_template_replicacao_09h.json` por conta/serviço.
- Testar localmente com variáveis mínimas antes de ativar cron no Railway.
- Adotar notificações Telegram para confirmar sucesso de cada publicação.

## 9) Pós-Replicação (Verificação)

- Rodar `railway_scheduler.py` e confirmar agendamentos e loop.
- Validar execução das 12:00 UTC no primeiro dia útil pós-configuração.
- Conferir Stories publicadas e registro de sucesso em logs + Telegram.

---

### Anexo A — Comandos úteis (Railway)

```
# Set de variáveis obrigatórias (exemplos)
railway variables set OPENAI_API_KEY=sk-...
railway variables set RAPIDAPI_KEY=xxxx
railway variables set INSTAGRAM_ACCESS_TOKEN=EAA...
railway variables set INSTAGRAM_BUSINESS_ACCOUNT_ID=1784...
railway variables set TELEGRAM_BOT_TOKEN=12345:ABC...
railway variables set TELEGRAM_CHAT_ID=-1001234567890
railway variables set SUPABASE_URL=https://xxxxx.supabase.co
railway variables set SUPABASE_SERVICE_KEY=eyJhbGci...

# Opcionais recomendados
railway variables set ENVIRONMENT=railway
railway variables set DISABLE_REPLICATE=true
railway variables set WEEKLY_THEMES_ENABLED=true
railway variables set STORIES_BACKGROUND_TYPE=gradient
railway variables set STORIES_TEXT_POSITION=auto

# Cron em UTC (09:00 BRT → 12:00 UTC)
railway cron add "0 12 * * *" -- command "python railway_scheduler.py"
```