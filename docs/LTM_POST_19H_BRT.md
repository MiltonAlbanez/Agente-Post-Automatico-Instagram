# LTM – Serviço 19h BRT (Feed Autopost)

## Objetivo
- Publicar automaticamente um post no feed do Instagram todos os dias às 19h BRT (22:00 UTC), com notificação no Telegram e observabilidade mínima.
- Garantir publicação mesmo sem banco de dados, via fallback Standalone temático noturno.

## Escopo
- Serviço one-off (cron) para `autopost` do feed às 19h.
- Integra com OpenAI (conteúdo), Unsplash (imagem temática), Supabase (armazenamento), Instagram Graph API (publicação) e Telegram (notificação).

---

## 1) Fluxo de Trabalho (Atual)

- Agendamento no Railway UI aciona um contêiner no horário: 22:00 UTC (19h BRT).
- Comando de entrada: `python -m src.main autopost` (padronizado via módulo para evitar erros de caminho).
- Pré-validações e leitura de variáveis de ambiente.
- Tentativa de uso de BD (`POSTGRES_DSN`/`DATABASE_URL`); se ausente ou falho, ativa fallback Standalone.
- Geração de conteúdo via OpenAI, aplicação de Testes A/B, Tema Semanal noturno e estilo visual.
- Seleção/geração de imagem temática (Unsplash). Se `disable_replicate`, não usa modelos de imagem externos.
- Upload da imagem para Supabase Storage e obtenção de URL pública.
- Publicação no Instagram (feed) com legenda e mídia.
- Notificação de sucesso/erro via Telegram.
- Encerramento do processo (one-off), sem manter serviço rodando.

---

## 2) Configurações Técnicas Específicas

- Railway (serviço Cron one-off):
  - Horário: `22:00 UTC` (equivale a `19h BRT`).
  - Comando: `python -m src.main autopost`.
  - Tipo: execução única; não usar `railway_scheduler.py` para cron.
- Ambiente (variáveis mínimas):
  - `OPENAI_API_KEY` – chave da OpenAI. Evitar chaves com sufixo `\n`.
  - `INSTAGRAM_BUSINESS_ACCOUNT_ID` – ID da conta de negócios.
  - `INSTAGRAM_ACCESS_TOKEN` – token de acesso válido.
  - `INSTAGRAM_MAX_RETRIES` – recomendado `3`.
  - `INSTAGRAM_TIMEOUT` – recomendado `120`.
  - `TELEGRAM_BOT_TOKEN` – token do bot.
  - `TELEGRAM_CHAT_ID` – chat/grupo para notificações.
  ̀- `ACCOUNT_NAME` – nome da conta (ex.: `Milton_Albanez`).
  - Supabase: `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, `SUPABASE_BUCKET`.
  - Opcional/Fallbacks: `POSTGRES_DSN` (quando houver BD), `REPLICATE_TOKEN` (se for usar geração de imagem).
- Comportamentos de segurança e execução:
  - Fallback Standalone automático quando BD não está disponível.
  - Desativação de Replicate quando indicado (`disable_replicate=True`).
  - Sem uso de serverless; contêiner deve inicializar, executar e encerrar.

---

## 3) Passo a Passo Detalhado da Postagem

1. Inicialização
   - Contêiner Railway inicia no horário definido (22:00 UTC).
   - Executa `python -m src.main autopost`.
2. Pré‑cheques
   - Leitura de variáveis e validações básicas (tokens, chaves, IDs).
3. Fonte de conteúdo
   - Se BD presente e acessível: busca 1 item não postado.
   - Se indisponível/erro ou sem itens: ativa fallback Standalone temático (noite/engajamento).
4. Configuração de conteúdo
   - Testes A/B aplicados automaticamente (formato, hashtags, estilo de imagem).
   - Tema Semanal noturno: foco em engajamento.
   - Prompt de conteúdo e legenda: derivados da conta (`accounts.json`) ou do sistema temático.
5. Imagem
   - Seleção de imagem temática via Unsplash (URL 1080x1080).
   - Se `disable_replicate=True`, não usa modelos de geração de imagem.
6. Upload
   - Envia imagem ao Supabase Storage; obtém URL pública para publicação.
7. Publicação
   - Chama cliente Instagram para criar mídia e publicar no feed.
8. Notificação
   - Envia resultado ao Telegram (sucesso/erro), incluindo IDs de criação/mídia.
9. Encerramento
   - Processo termina; não mantém serviço executando após conclusão.

---

## 4) Checklist de Verificação

- Agendamento
  - [ ] Definir horário `22:00 UTC` para 19h BRT.
  - [ ] Tipo de execução: one-off (cron), não 24/7.
  - [ ] Comando: `python -m src.main autopost`.
- Variáveis de ambiente
  - [ ] `OPENAI_API_KEY` configurada (sem sufixo `\n`).
  - [ ] `INSTAGRAM_BUSINESS_ACCOUNT_ID` válido.
  - [ ] `INSTAGRAM_ACCESS_TOKEN` válido.
  - [ ] `INSTAGRAM_MAX_RETRIES=3` e `INSTAGRAM_TIMEOUT=120`.
  - [ ] `TELEGRAM_BOT_TOKEN` e `TELEGRAM_CHAT_ID` válidos.
  - [ ] `ACCOUNT_NAME` definido para a conta alvo.
  - [ ] `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, `SUPABASE_BUCKET` configurados.
  - [ ] (Opcional) `POSTGRES_DSN` se houver BD.
  - [ ] (Opcional) `REPLICATE_TOKEN` se for usar geração de imagem.
- Observabilidade
  - [ ] Validar logs pós‑execução.
  - [ ] Confirmar IDs (`creation_id`, `media_id`) e `status`.
  - [ ] Verificar notificação no Telegram.
- Segurança
  - [ ] Tokens não placeholders.
  - [ ] Sem segredos em arquivos versionados.

---

## 5) Diagramas

### 5.1 Sequência – Execução 19h BRT (Feed Autopost)

```
Cron (Railway, 22:00 UTC)
      |
      v
Contêiner -> python -m src.main autopost
      |
      v
Pré‑cheques/env -> Testes A/B + Tema Semanal
      |
      +--> BD disponível? ---- Sim ---> Busca item não postado
      |                         Não ---> Fallback Standalone temático (noite)
      |
      v
Conteúdo (OpenAI) + Imagem (Unsplash)
      |
      v
Upload (Supabase Storage) -> URL pública
      |
      v
Publicação (Instagram Graph API)
      |
      v
Notificação (Telegram)
      |
      v
Encerrar (one-off)
```

### 5.2 Fluxo de Decisão – Fallback

```
[BD/POSTGRES_DSN presente?]
      |-- Não -> Fallback Standalone
      |-- Sim -> Conectar BD
                 |-- Erro -> Fallback Standalone
                 |-- OK -> Buscar conteúdo
                         |-- Vazio -> Fallback Standalone
                         |-- Conteúdo -> Usar BD
```

---

## 6) Notas de Operação
- Não usar `railway_scheduler.py` para jobs de 19h (cron one‑off). O scheduler é para serviços 24/7.
- Evitar variáveis com sufixo `\n` no nome; criar as versões corretas sem sufixo.
- Fallback Standalone garante publicação mesmo sem BD; preferir manter Supabase operacional para hospedagem de mídia.
- Tokens do Instagram expiram; validar periodicamente.
- Ajustar horário UTC com atenção ao horário de verão se aplicável (BRT usualmente UTC‑3).

---

## 7) Histórico de Versões
- 2025-11-03: Padronização do comando (`python -m src.main autopost`),
  inclusão de checklist completo e nota sobre variáveis com sufixo `\n`.