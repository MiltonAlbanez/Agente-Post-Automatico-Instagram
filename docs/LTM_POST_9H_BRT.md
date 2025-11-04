# LTM – Serviço 9h BRT (Feed Autopost)

## Objetivo
- Publicar automaticamente um post no feed do Instagram todos os dias às 9h BRT (12:00 UTC), com notificação no Telegram e observabilidade mínima.
- Garantir publicação mesmo sem banco de dados, via fallback Standalone temático.

## Escopo
- Serviço one-off (cron) para `autopost` do feed.
- Integra com OpenAI (conteúdo), Unsplash (imagem temática), Supabase (armazenamento), Instagram Graph API (publicação) e Telegram (notificação).

---

## 1) Descrição Completa do Fluxo de Trabalho (Atual)

- Agendamento no Railway UI aciona um contêiner no horário: 12:00 UTC (9h BRT).
- Comando de entrada: `python src/main.py autopost`.
- Pré-validações e leitura de variáveis de ambiente.
- Tentativa de uso de BD (`POSTGRES_DSN`); se ausente ou falho, ativa fallback Standalone.
- Geração de conteúdo via OpenAI, aplicação de Testes A/B, Sistema Temático Semanal e estilo visual.
- Seleção/geração de imagem temática (Unsplash). Se `disable_replicate`, não usa modelos de imagem externos.
- Upload da imagem para Supabase Storage e obtenção de URL pública.
- Publicação no Instagram (feed) com legenda e mídia.
- Notificação de sucesso/erro via Telegram.
- Encerramento do processo (one-off), sem manter serviço rodando.

---

## 2) Configurações Técnicas Específicas

- Railway (serviço Cron one-off):
  - Horário: `12:00 UTC` (equivale a `9h BRT`).
  - Comando: `python src/main.py autopost`.
  - Tipo: execução única; não usar `railway_scheduler.py` para cron.
- Ambiente (variáveis mínimas):
  - `OPENAI_API_KEY` – chave da OpenAI.
  - `INSTAGRAM_BUSINESS_ACCOUNT_ID` – ID da conta de negócios.
  - `INSTAGRAM_ACCESS_TOKEN` – token de acesso válido.
  - `TELEGRAM_BOT_TOKEN` – token do bot.
  - `TELEGRAM_CHAT_ID` – chat/grupo para notificações.
  - `ACCOUNT_NAME` – nome da conta (ex.: `Milton_Albanez`).
  - Supabase (recomendado): `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, `SUPABASE_BUCKET` (ex.: `instagram-images`).
  - Opcional/Fallbacks: `POSTGRES_DSN` (quando houver BD), `REPLICATE_TOKEN` (se for usar geração de imagem com modelo), `POST_TAGS` (filtro de BD).
- Comportamentos de segurança e execução:
  - Fallback Standalone automático quando BD não está disponível.
  - Desativação de Replicate quando indicado (`disable_replicate=True`).
  - Sem uso de serverless; contêiner deve inicializar, executar e encerrar.

---

## 3) Passo a Passo Detalhado da Postagem

1. Inicialização
   - Contêiner Railway inicia no horário definido (12:00 UTC).
   - Executa `python src/main.py autopost`.
2. Pré‑cheques
   - Leitura de variáveis e validações básicas (tokens, chaves, IDs).
3. Fonte de conteúdo
   - Se `POSTGRES_DSN` presente e acessível: busca 1 item não postado.
   - Se indisponível/erro ou sem itens: ativa fallback Standalone temático.
4. Configuração de conteúdo
   - Testes A/B aplicados automaticamente (formato, hashtags, estilo de imagem).
   - Sistema Temático Semanal: tema e foco pela combinação dia/horário; caso matinal, aplica “cunho espiritual obrigatório” quando configurado.
   - Prompt de conteúdo e legenda: derivados da conta (`accounts.json`) ou do sistema temático.
5. Imagem
   - Seleção de imagem temática via Unsplash (URL 1080x1080)
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

## 4) Requisitos de Sistema e Dependências

- Runtime
  - Python 3.11+; ambiente Railway (Nixpacks) sem serverless.
- Bibliotecas (trecho `requirements.txt` relevante)
  - `openai`, `python-telegram-bot`, `flask` (health server em outros serviços), `psutil`, `replicate` (opcional), `requests`.
- Serviços e módulos internos
  - `src/main.py` – entrypoint com lógica de fallback e roteamento de comando.
  - `src/pipeline/generate_and_publish.py` – pipeline de geração e publicação.
  - `src/services/instagram_client.py` ou `instagram_client_robust.py` – publicação.
  - `src/services/public_uploader.py` e `supabase_uploader.py` – upload.
  - `src/services/openai_client.py` e `replicate_client.py` (opcional) – geração.
  - `src/services/telegram_client.py` – notificações.
  - `src/services/ab_testing_framework.py` – testes A/B.
  - `src/services/weekly_theme_manager.py` – temas semanais.
- Credenciais
  - Tokens de Instagram e Telegram válidos; chave OpenAI ativa; Supabase configurado.

---

## 5) Diagramas

### 5.1 Sequência – Execução 9h BRT (Feed Autopost)

```
Cron (Railway, 12:00 UTC)
      |
      v
Contêiner -> python src/main.py autopost
      |
      v
Pré‑cheques/env -> Testes A/B + Tema Semanal
      |
      +--> BD disponível? ---- Sim ---> Busca item não postado
      |                         Não ---> Fallback Standalone temático
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
[POSTGRES_DSN presente?]
      |-- Não -> Fallback Standalone
      |-- Sim -> Conectar BD
                 |-- Erro -> Fallback Standalone
                 |-- OK -> Buscar conteúdo
                         |-- Vazio -> Fallback Standalone
                         |-- Conteúdo -> Usar BD
```

---

## 6) Checklist de Verificação (Replicação para outros serviços 9h)

- Agendamento
  - [ ] Definir horário `12:00 UTC` para 9h BRT.
  - [ ] Tipo de execução: one-off (cron), não 24/7.
  - [ ] Comando: `python src/main.py autopost`.
- Variáveis de ambiente
  - [ ] `OPENAI_API_KEY` configurada.
  - [ ] `INSTAGRAM_BUSINESS_ACCOUNT_ID` válido.
  - [ ] `INSTAGRAM_ACCESS_TOKEN` válido.
  - [ ] `TELEGRAM_BOT_TOKEN` e `TELEGRAM_CHAT_ID` válidos.
  - [ ] `ACCOUNT_NAME` definido para a conta alvo.
  - [ ] `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, `SUPABASE_BUCKET` configurados.
  - [ ] (Opcional) `POSTGRES_DSN` se houver BD.
  - [ ] (Opcional) `REPLICATE_TOKEN` se for usar geração de imagem.
- Pipeline
  - [ ] Testes A/B ativos (formato/hashtags/estilo).
  - [ ] Sistema Temático Semanal habilitado (`use_weekly_themes=True`).
  - [ ] `disable_replicate=True` se manter apenas Unsplash.
- Observabilidade
  - [ ] Validar logs pós‑execução.
  - [ ] Confirmar IDs (`creation_id`, `media_id`) e `status`.
  - [ ] Verificar notificação no Telegram.
- Segurança
  - [ ] Tokens não placeholders.
  - [ ] Sem segredos em arquivos versionados.

---

## Referências (Arquivos/Rotas)
- `src/main.py` – lógica de fallback e comando `autopost` (inclui `get_random_unsplash_url(theme)`).
- `src/pipeline/generate_and_publish.py` – aplica `get_ab_test_config(account_name)`;
  - Observação (linha ~247): “extra permite merge específico por chamada” – pipeline suporta merge de configurações da chamada com as geradas (A/B, temas, etc.).
- `src/services/ab_testing_framework.py` – imprime variante selecionada e aplica configs.
- `INSTRUCOES_RAILWAY_CRON.md` – padrões de agendamento e comandos.
- `requirements.txt` – dependências principais.
- `railway.json` / `railway.yaml` – exemplos e políticas de deploy.
- `railway_deploy_commands.txt` – comandos úteis de monitoramento.

---

## Notas de Operação
- Não usar `railway_scheduler.py` para jobs de 9h (cron one‑off). O scheduler é para serviços 24/7.
- Fallback Standalone garante publicação mesmo sem BD; preferir manter Supabase operacional para hospedagem de mídia.
- Tokens do Instagram expiram; validar periodicamente.
- Ajustar horário UTC com atenção ao horário de verão se aplicável (BRT usualmente UTC‑3).

---

## Status de Conformidade
- Pronto para replicação em novos serviços 9h, seguindo este checklist e diagrama.
- Compatível com a organização LTM (artefato de operação, com escopo e fluxo documentado).