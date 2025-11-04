# Relatório de Incidente LTM — Posts Instagram não publicados (Railway Cron)

ID: LTM-IG-2025-10-24-01
Data/Hora (BRT): 24/10/2025 12:45
Serviço: Stories 21h / Publicação Instagram (Railway)
Severidade: Alta (S3 — Interrupção parcial de funcionalidade crítica)
Status: Em análise com ações corretivas em curso

## 1. Resumo Executivo
- Sintoma: Posts do Instagram não são publicados nos horários programados, apesar dos cron jobs do Railway executarem.
- Evidência chave: Logs mostram serviço em loop contínuo (não finaliza), o que conflita com o modelo de execução de cron do Railway (jobs devem iniciar, executar tarefa e sair). Quando uma execução anterior permanece “Active”, a próxima é pulada.
- Variáveis críticas: Confirmadas `INSTAGRAM_ACCESS_TOKEN`, `INSTAGRAM_BUSINESS_ACCOUNT_ID`, `OPENAI_API_KEY`. Ausentes (no painel compartilhado): `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `RAPIDAPI_KEY` (pode impactar geração/monitoramento, e notificações).
- Provável causa raiz: Uso de um scheduler 24/7 dentro do serviço configurado como cron (loop que não termina), associado a lacunas de variáveis de notificação, ocasionando ausência de alertas e não publicação confiável.

## 2. Escopo e Impacto
- Serviços afetados: Publicação de Feed/Stories via Graph API; notificações Telegram; coleta/monitoramento.
- Usuários/contas: Múltiplas contas do `accounts.json` com publicação programada.
- Impacto: Conteúdos deixam de ser publicados nos horários; sem alarmes Telegram, reduz visibilidade de falhas.

## 3. Verificação dos Cron Jobs no Railway
- Execução em horários corretos: Logs indicam agendamentos UTC compatíveis com BRT (06:00, 12:00, 19:00). Trecho coletado:
  - "📅 Agendamentos configurados: 09:00 UTC (06:00 BRT), 15:00 UTC (12:00 BRT), 22:00 UTC (19:00 BRT)"
- Logs das últimas execuções: Coleta via CLI (`railway logs -n 200`). Evidência:
  - "🔄 Entrando no loop principal..."
  - "💓 Sistema ativo - Loop #1 ... Loop #181" (serviço permanece ativo)
- Exit code por job:
  - Observação: Railway registra exit code por execução de cron no painel "Cron Runs". Como o serviço não sai, não há exit code consistente exposto via CLI; a execução permanece "Active" e subsequentes são puladas. Evidência requerida via screenshot do painel (ver seção 9).
- Conformidade com docs Railway [Cron Jobs]: Jobs devem executar e sair; execuções são puladas se a anterior não terminou. (Referência: Docs Railway)

## 4. Análise do Fluxo de Publicação no Instagram
- Conexão Graph API: Cliente robusto usa `https://graph.facebook.com/v20.0` com retry/timeout ampliado.
- Validação de credenciais: Em `generate_and_publish` há bloqueio se `INSTAGRAM_ACCESS_TOKEN` inválido (ex.: token não Graph, contém espaços ou "login:").
- Limitações/bloqueios:
  - Tempo de preparação/publicação pode exceder janela; robusto aumenta timeout (120s) e retries (3).
  - Se a mídia não finalizar `FINISHED`, publica falha e notifica.
- Evidências (trechos de código):
  - `src/pipeline/generate_and_publish.py` (linhas ~400–566): valida token, prepara/polling/publica e notifica Telegram para sucesso/falha.
  - `src/services/instagram_client_robust.py` (linhas ~165–183): `media_publish` com retry/timeout 120s.

## 5. Investigação do Sistema de Notificações (Telegram)
- Configuração: Cliente simples, exige `TELEGRAM_BOT_TOKEN` e `TELEGRAM_CHAT_ID`.
- Conectividade: Sem variáveis configuradas no serviço analisado, mensagens não são enviadas; blocos `try/except` no pipeline capturam erros e (após correções) logam.
- Logs: Ferramenta `monitor_railway_logs.py` detecta menções a Telegram; em ausência de variáveis, não há atividade.
- Evidência (trecho):
  - `src/services/telegram_client.py`:
    ```python
    url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
    payload = {"chat_id": self.chat_id, "text": text}
    requests.post(url, data=payload, timeout=30)
    ```

## 6. Timeline (UTC/BRT)
- 09:42 UTC (06:42 BRT): Serviço inicia, configura cron times e entra em loop.
- 10:12–12:42 UTC: Múltiplos logs "Sistema ativo — Loop #...", nenhuma saída.
- Próximas execuções previstas: 15:00 UTC (12:00 BRT), 22:00 UTC (19:00 BRT).

## 7. Severidade (Matriz LTM)
- Probabilidade: Alta (configuração atual tende a manter serviço ativo e pular execuções).
- Impacto: Alto (publicação automatizada indisponível nos horários programados).
- Classificação: S3 — Requer ação corretiva imediata e curto prazo.

## 8. Causa Raiz e Fatores Contribuintes
- Causa raiz: Serviço configurado como cron executa um scheduler 24/7 (não termina), violando requisito de jobs curtos no Railway cron.
- Contribuintes:
  - Ausência de `TELEGRAM_BOT_TOKEN` e `TELEGRAM_CHAT_ID` impede visibilidade imediata das falhas.
  - Possível ausência de `RAPIDAPI_KEY` pode afetar coleta/geração de conteúdo upstream.

## 9. Evidências Técnicas (a juntar ao ticket)
- Screenshots:
  - [screenshot] Painel Railway > Cron Runs mostrando status/exit code e execuções puladas.
  - [screenshot] Painel Railway > Logs do serviço nas janelas 06:00/12:00/19:00 BRT.
  - [screenshot] Painel Railway > Variables confirmando variáveis presentes/ausentes.
- Trechos de código (referências):
  - `src/pipeline/generate_and_publish.py` — publicação e notificações.
  - `src/services/instagram_client_robust.py` — publish com retry/timeout.
  - `automation/scheduler.py` — loop 24/7, incompatível com cron jobs.
  - `src/services/telegram_client.py` — envio Telegram.
- Diagrama de Fluxo (atual)
  ```
  Cron (Railway) ──► Start Command do Serviço
                      └─► automation/scheduler.py (loop 24/7)
                           ├─► generate_and_publish(...)
                           │    ├─► Instagram Graph API (prepare/publish/poll)
                           │    └─► TelegramClient (sucesso/falha)
                           └─► NÃO FINALIZA ► Próximo cron é pulado
  ```

## 10. Ações já executadas
- Coleta de logs via CLI (`railway logs -n 200`) confirmou loop contínuo.
- Validação de variáveis presentes: `INSTAGRAM_ACCESS_TOKEN`, `INSTAGRAM_BUSINESS_ACCOUNT_ID`, `OPENAI_API_KEY` OK; Telegram/RapidAPI ausentes no painel compartilhado.
- Referência às correções robustas (cliente Instagram e blocos de notificação) já aplicadas no código.

## 11. Ações Recomendadas (Curto Prazo)
1) Ajustar execução para modelo de cron job curto no Railway:
   - Alterar `Start Command` para executar um script que faz UM ciclo de publicação e encerra (ex.: `python -m src.main --post-once` ou script dedicado `run_once.py`).
   - Remover/evitar `automation/scheduler.py` em serviços marcados como cron.
2) Configurar variáveis faltantes no Railway:
   - `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` (notificações e visibilidade).
   - `RAPIDAPI_KEY` (se pipeline o requer para coleta/conteúdo).
3) Redeploy e validação:
   - Executar um job manual (Run Now) e verificar que o processo sai com exit code 0.
   - Confirmar publicação e mensagens Telegram.
4) Evidências:
   - Capturar screenshots de Cron Runs (exit code/status), Logs e Variables.

## 12. Validação Pós-Correção
- Verificar no painel "Cron Runs": status e exit code 0 nas execuções.
- Confirmar mensagens Telegram recebidas nos horários.
- Validar publicação em cada conta do `accounts.json`.

## 13. Riscos e Mitigações
- Risco: Continuação do uso de scheduler 24/7 sob cron ⇒ execuções puladas.
- Mitigação: Segmentar — manter scheduler 24/7 em serviço próprio (não cron), e cron jobs usando scripts de execução única.

## 14. Anexos
- `PROCESSO_REDEPLOY_RAILWAY.md`, `SOLUCAO_IMEDIATA_IMPLEMENTADA.md`, `ANALISE_CORRECAO_PARCIAL_RAILWAY.md` (referências operacionais).
- Scripts de apoio: `monitor_railway_logs.py` (monitor), `test_telegram_*` (debug).

---
Observação LTM: Este relatório segue o template padrão (Resumo, Verificação Cron, Fluxo Instagram, Telegram, Timeline, Severidade, RCA, Evidências, Ações) e evita exposição de credenciais.