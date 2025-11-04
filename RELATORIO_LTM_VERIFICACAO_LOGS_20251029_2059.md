# Relatório LTM — Verificação Detalhada de Logs (Ontem ↔ Hoje)

Data/Hora (BRT): 2025-10-29 20:59
Responsável: Assistente Trae AI

## Objetivo
- Auditar falhas nos horários programados (21h, 6h, 9h, 12h, 15h, 19h) entre ontem e hoje.
- Monitorar em tempo real a execução das 21h de hoje.
- Executar `instagram-bot/diagnostic_system.py` e consolidar evidências no LTM.

## Sumário Executivo
- Monitoramento em tempo real inicializado às 20:52:45 BRT para capturar a execução das 21h.
- Não há registros de deployments hoje (29/10) para o serviço atualmente vinculado (CLI mostra Service: "Stories 9h").
- Diagnóstico de sistema: Telegram OK, HTTP OK, PostgreSQL OK via DSN (SELECT 1).
- Conexão Instagram: token válido e permissões OK; RapidAPI falhando (403 — não subscrito).
- Verificação do agendador: relatório indica `railway_configuration: false` — provável falta/misconfiguração de Cron/serviço correto para os horários de hoje.
- Permissões e uploads locais: OK; alerta de módulo SupabaseUploader ausente (não bloqueante para Feed local).

## Linha do Tempo e Evidências

### 29/10 (Hoje)
- 20:52:45 — Monitoramento contínuo iniciado: `python monitor_railway_logs.py --monitor --interval 10 --alerts`.
- 20:55:37 — Verificação de logs recentes: `python monitor_railway_logs.py --recent --alerts` (execução longa; captura inicial registrada).
- 20:58:11 — Teste Instagram token: OK
  - Conta: `@milton_albanez` (ID: 17841404919106588)
  - Expira: 2025-12-06
  - Resultado: `Todos os testes passaram! Token parece estar funcionando.`
- 20:58:11 — RapidAPI: FALHA (HTTP 403: "You are not subscribed to this API.")
- 20:59:31 — Verificação do agendador: `scheduler_verification_report_20251029_205931.json`
  - `tests.railway_configuration = false`
  - Recomendação: "Verificar a configuração do Railway para garantir que todos os horários estejam configurados corretamente"
- 20:59:40–20:59:50 — Teste de upload de imagem: OK
  - 3 uploads bem-sucedidos; tempo médio 0.81s; relatório `supabase_image_upload_test_20251029_205950.json`
- 20:59:50 — Status do Railway via CLI: `Project: Agente_Post_Auto_Insta`, `Environment: production`, `Service: Stories 9h`
- 20:59:55 — Deployments (CLI): sem registros de hoje; último sucesso: 24/10 14:27:50 BRT

### 28/10 (Ontem)
- Sem falhas reportadas pelo usuário; execuções automáticas teriam ocorrido em 21h, 6h e 12h conforme histórico.

### 27/10
- `scheduler_verification_report_20251027_214400.json`: `railway_configuration = false`

## Timestamps de Falhas de Hoje (ausência de execução)
- 06:00 BRT — ausência de execução (sem deployment hoje)
- 09:00 BRT — ausência de execução
- 12:00 BRT — ausência de execução
- 15:00 BRT — ausência de execução
- 19:00 BRT — ausência de execução

Observação: A ausência é inferida a partir de `railway deployment list` sem registros de hoje e status de serviço vinculado diferente do alvo.

## Mensagens de Erro Completas
- RapidAPI: `HTTP 403 — {"message":"You are not subscribed to this API."}`
- Agendador (teste): `generate_and_publish() missing 7 required positional arguments: 'openai_key', 'replicate_token', 'instagram_business_id', 'instagram_access_token', 'telegram_bot_token', 'telegram_chat_id', and 'source_image_url'`

## Contexto do Sistema no Momento das Falhas
- CLI vinculada a `Service: Stories 9h` (não ao Feed 06h/21h).
- `railway_configuration: false` nos relatórios de verificação (27/10 e 29/10).
- Diagnóstico de ambiente OK: `TIMEZONE=America/Sao_Paulo`, Telegram OK, Postgres OK via DSN.
- Token Instagram válido; RapidAPI não subscrito.

## Verificações Solicitadas
- Conexão com a API do Instagram: OK (token válido, permissões de leitura OK).
- Status do agendador de tarefas: PARCIAL/INCORRETO (sem execuções hoje; `railway_configuration=false`).
- Permissões de acesso: OK para arquivos e upload local.
- Consumo de recursos do sistema: Recomendado checar UI `Service > Metrics` (CPU/Mem/Net) no Railway; CLI não disponibiliza métricas.

## Causas Prováveis
- Serviço incorreto vinculado na CLI e/ou Cron no serviço errado.
- Ausência/misconfiguração dos Cron commands para hoje nos serviços de Feed e Stories.
- Dependência de RapidAPI ocasiona falha em chamadas secundárias (não bloqueante para Feed, mas afeta integrações).

## Correções Propostas (Padrão LTM)
- Ajuste de Cron por serviço:
  - Feed 06h/21h: `python src/main.py multirun --limit 1`
  - Stories 09h/15h/21h: `python src/main.py multirun --stories --limit 1`
  - Alternativa robusta para Feed até DB/ambiente estabilizar: `python src/main.py standalone --theme motivacional --disable_replicate`
- Vincular CLI ao serviço correto antes de alterações e análise de logs:
  - `railway service "<nome exato do serviço alvo>"`
- Variáveis críticas por serviço:
  - Definir `AUTOCMD` conforme função (Feed vs Stories) se a lógica local utiliza essa variável.
  - Confirmar `TIMEZONE`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `POSTGRES_DSN`/`DATABASE_URL`.
- RapidAPI:
  - Assinar o plano ou desativar temporariamente o uso (se houver flag). Tratar `HTTP 403` com fallback interno.
- Testes e funções auxiliares:
  - Corrigir chamada `generate_and_publish(...)` nos testes para usar configuração do projeto (evitar parâmetros posicionais ausentes).

## Ações Imediatas Executadas
- Monitoramento contínuo habilitado para capturar a execução das 21h de hoje.
- Diagnóstico completo de ambiente executado com sucesso (HTTP/Telegram/Postgres OK).
- Testes de Instagram e upload executados; falha RapidAPI documentada.
- Relatórios de verificação do agendador coletados e analisados.

## Próximos Passos
- Confirmar execução das 21h no próximo tick e anexar evidências de logs (prints/timestamps) a este relatório.
- Ajustar Cron e/ou serviço alvo conforme correções propostas.
- Validar novamente com `python monitor_railway_logs.py --recent --alerts` após ajuste.
- Checar `Service > Metrics` (UI Railway) para consumo de recursos durante as janelas alvo.

---
Este relatório segue o padrão LTM para auditoria e referência futura, com timestamps, mensagens, contexto e correções propostas.