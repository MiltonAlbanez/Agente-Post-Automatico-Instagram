# Correção do serviço Post Feed 19:00 – Padronização para Scheduler 24/7

Data: 2025-10-30

Objetivo: eliminar erro de entrypoint e alinhar todos os serviços de Feed ao scheduler interno 24/7.

Mudanças aplicadas no repositório:
- Atualizado `Procfile` para `scheduler: python railway_scheduler.py`.
- Atualizado `railway.json` para `startCommand: "python railway_scheduler.py"`.

Racional:
- Logs do serviço "Post Feed 19:00" mostravam `python: can't open file '/app/railway_automation_teste.py'`, indicando comando incorreto ou fonte divergente.
- Os serviços "Post Feed 6h" e "Post Feed 12h" operam sob um scheduler contínuo com jobs agendados, portanto a padronização evita duplicidade e inconsistências com Cron.

Passos para concluir a correção (no Railway):
1. Garantir que o serviço "Post Feed 19:00" esteja vinculado ao repositório atual.
2. Validar que o serviço usa o comando do repositório (`Procfile`/`railway.json`) – Start Command deve ser `python railway_scheduler.py`.
3. Remover qualquer Cron associado ao serviço, se existir, para evitar conflito com o loop 24/7.
4. Executar redeploy do serviço e verificar logs.

Validação pós-redeploy:
- Logs esperados ao iniciar: mensagens de configuração de agendamentos (Feed 09:00/15:00/21:00/22:00 UTC) e stories (12:00/18:00/00:00 UTC).
- Presença de mensagens: "💓 Sistema ativo", "📋 Jobs agendados", "⏰ Próxima execução".
- Ausência do erro anterior: `can't open file '/app/railway_automation_teste.py'`.

Ações complementares:
- Padronizar nomes na CLI conforme UI: "Post Feed 6h", "Post Feed 12h", "Post Feed 19:00".
- Reativar monitoramento com `python monitor_railway_logs.py --monitor --interval 10 --alerts` e revisar alertas recentes.