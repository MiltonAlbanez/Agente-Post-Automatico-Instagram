# Padrão de Variáveis de Ambiente — Railway (Cron Schedules)

Este documento define o conjunto canônico de variáveis de ambiente que devem existir em TODOS os cron schedules no Railway. Use como referência o schedule "Stories 21h", que está funcionando corretamente.

## Conjunto Canônico (21 variáveis)

- `OPENAI_API_KEY` — chave da OpenAI para geração de conteúdo
- `REPLICATE_TOKEN` — token do Replicate para geração de imagem
- `INSTAGRAM_BUSINESS_ACCOUNT_ID` — ID da conta comercial do Instagram (Graph API)
- `INSTAGRAM_ACCESS_TOKEN` — token de acesso do Instagram (Graph API)
- `TELEGRAM_BOT_TOKEN` — token do bot Telegram para alertas
- `TELEGRAM_CHAT_ID` — ID do chat Telegram para alertas
- `RAPIDAPI_KEY` — chave RapidAPI (scraper opcional)
- `RAPIDAPI_HOST` — host do serviço RapidAPI
- `RAPIDAPI_ALT_HOSTS` — hosts alternativos RapidAPI (fallback)
- `POSTGRES_DSN` — conexão PostgreSQL (ou usar `DATABASE_URL`)
- `DATABASE_URL` — conexão DB padrão do Railway (fallback)
- `SUPABASE_URL` — URL do Supabase Storage (opcional)
- `SUPABASE_SERVICE_KEY` — chave do serviço Supabase (opcional)
- `SUPABASE_BUCKET` — bucket do Supabase (opcional)
- `RAILWAY_ENVIRONMENT` — rótulo do ambiente (ex.: `production`)
- `AUTOCMD` — comando automático principal (ex.: `scheduler`)
- `ACCOUNT_NAME_DEFAULT` — nome de conta padrão (fallback)
- `SOURCE_IMAGE_URL_DEFAULT` — URL de imagem padrão (fallback)
- `DISABLE_REPLICATE` — `true/false` para desativar geração de imagens
- `STORIES_BACKGROUND_TYPE` — `gradient/blurred` (padrão visual dos Stories)
- `WEEKLY_THEMES_ENABLED` — `true/false` para Sistema Temático Semanal

Observação: algumas variáveis são opcionais e servem de fallback. Mantenha-as mesmo que não sejam usadas diretamente em todos os horários para garantir consistência.

## Como Padronizar no Railway

1. Abra o schedule que funciona ("Stories 21h") e **liste todas as variáveis**.
2. Nos demais schedules (Feed 06/12/18/19 e Stories 09/15/00), **replique exatamente os mesmos nomes** e **valores**.
3. Garanta que `INSTAGRAM_BUSINESS_ACCOUNT_ID` e `INSTAGRAM_ACCESS_TOKEN` estão **presentes** e corretos.
4. Garanta que `OPENAI_API_KEY`, `REPLICATE_TOKEN`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` existem em todos os schedules.
5. Se usar armazenamento, mantenha `SUPABASE_*` iguais em todos.
6. Após padronizar, **reinicie** cada serviço/schedule para aplicar.

## Verificações Rápidas

- Telegram: sem `TELEGRAM_*` não há alertas; o job pode funcionar mas não notifica.
- Instagram: sem `INSTAGRAM_*` o post falha com erro de token/ID.
- Geração: sem `OPENAI_API_KEY` e `REPLICATE_TOKEN`, pode cair em fallback (qualidade inferior).
- DB: `POSTGRES_DSN` ou `DATABASE_URL` presentes evitam erros de tracking.

## Dicas

- Evite nomes customizados em português (ex.: `TOKEN_DE_ACESSO_DO_INSTAGRAM`). Padronize para os nomes acima.
- Se um schedule tiver menos variáveis, **adicione as que faltam** mesmo que não sejam usadas diretamente naquele horário.
- Se um schedule tiver variáveis extras não usadas, **mantenha** se não conflitam, ou remova após validar que não há dependências.

## Como sincronizar com Railway (Passo a passo)

1. Instale e autentique-se no Railway CLI:
   - `railway login`
   - `railway link` (selecione o projeto correto)
2. Aplique variáveis padrão com o script:
   - `./scripts/railway_env_bootstrap.ps1`
   - Substitua os placeholders (`<...>`) por suas credenciais reais.
3. Alternativa (manual):
   - Execute os comandos em `railway_env_commands.txt` e `railway_supabase_commands.txt`.
4. Confirme configuração:
   - No painel do Railway, verifique se todos os schedules têm o mesmo conjunto de variáveis e valores.
5. Valide execução:
   - Rode localmente: `python -m src.main generate --image_url "https://images.unsplash.com/photo-1506905925346-21bda4d32df4" --disable_replicate --stories`
   - Em produção, reexecute um schedule e monitore logs/Telegram.
6. Boas práticas de segurança:
   - Não versionar segredos em plaintext.
   - Preferir placeholders em arquivos de referência (ex.: `CREDENCIAIS_PERMANENTES.json`).
   - Atualizar `.env.example` como contrato de configuração.