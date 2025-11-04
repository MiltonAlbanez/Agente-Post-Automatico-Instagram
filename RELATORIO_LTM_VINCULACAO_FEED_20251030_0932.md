# 📋 Relatório LTM: Vinculação de Serviços Post Feed e Coleta de Logs (2025-10-30 09:32 UTC)

## Objetivo
- Confirmar existência dos serviços "Post Feed 6h", "Post Feed 12h" e "Post Feed 19:00" conforme UI do Railway.
- Vincular a CLI aos serviços exatos da UI e coletar trechos curtos de logs com timestamps, evitando travamentos de stream contínuo.

## Ações Executadas
- `railway service "Post Feed 6h"` → vinculado com sucesso.
- `railway logs | Select-Object -First 160` → coleta curta realizada.
- `railway service "Post Feed 12h"` → vinculado com sucesso.
- `railway logs | Select-Object -First 160` → coleta curta realizada.
- `railway service "Post Feed 19:00"` → vinculado com sucesso.
- `railway logs | Select-Object -First 160` → coleta curta realizada.

## Evidências de Logs (trechos)

### Post Feed 6h
```
[2025-10-29 00:05:37] 💓 Sistema ativo - Loop #901
[2025-10-29 00:05:37] 📊 Jobs agendados: 3
[2025-10-29 00:05:37] ⏰ Próxima execução: 2025-10-29 09:00:00
[2025-10-29 01:05:37] 💓 Sistema ativo - Loop #961
[2025-10-29 01:05:37] ⏰ Próxima execução: 2025-10-29 09:00:00
```

### Post Feed 12h
```
[2025-10-28 00:00:59] 💓 Sistema ativo - Loop #12061
[2025-10-28 00:00:59] 📊 Jobs agendados: 3
[2025-10-28 00:00:59] ⏰ Próxima execução: 2025-10-28 09:00:00
[2025-10-28 03:00:59] 💓 Sistema ativo - Loop #12241
[2025-10-28 03:00:59] ⏰ Próxima execução: 2025-10-28 09:00:00
```

### Post Feed 19:00
```
Starting Container
python: can't open file '/app/railway_automation_teste.py': [Errno 2] No such file or directory
Starting Container
python: can't open file '/app/railway_automation_teste.py': [Errno 2] No such file or directory
```

## Interpretação
- "Post Feed 6h" e "Post Feed 12h": logs mostram o scheduler interno ativo, com próxima execução prevista em UTC; serviços existem e estão operacionais.
- "Post Feed 19:00": erro claro de comando/entrypoint do serviço apontando para arquivo inexistente (`/app/railway_automation_teste.py`). Isso explica falha nos posts de feed das 19h BRT.

## Confirmação no Codebase
- `railway_scheduler.py` define os horários em UTC equivalentes: 09:00, 15:00, 21:00, 22:00 (Feed) e 12:00, 18:00, 00:00 (Stories).
- `Procfile` contém `scheduler: python railway_scheduler.py` confirmando execução 24/7 nos serviços com loop.
- Documentos `CONFIGURACAO_CRON_RAILWAY.md` e `INSTRUCOES_FINAIS_CORRECAO.md` listam os mesmos seis horários, com recomendação de usar apenas o scheduler interno.

## Próximos Passos Recomendados
- Corrigir comando do serviço "Post Feed 19:00" no Railway:
  - Opção A (Cron isolado): `python src/main.py multirun --limit 1` com variáveis corretas.
  - Opção B (preferida): desativar Cron e usar apenas o scheduler interno 24/7 via `railway_scheduler.py`, evitando duplicidade e inconsistência.
- Padronizar nomes usados na CLI com os nomes exatos da UI: `"Post Feed 6h"`, `"Post Feed 12h"`, `"Post Feed 19:00"`.
- Executar nova verificação com `python monitor_railway_logs.py --recent --alerts` após correção.

## Timestamp
- Relatório gerado em: 2025-10-30 09:32 (UTC)