# 📋 Relatório de Serviços e Horários (Railway) — 2025-11-03

Este relatório consolida os serviços configurados e seus respectivos horários de execução, com a conversão entre BRT (UTC−3) e UTC, incluindo a expressão `cron` quando disponível.

## Fonte dos dados
- `CONFIGURACAO_CRON_RAILWAY.md` (seção “STATUS ATUAL” e tabelas de Stories)
- `railway.yaml.backup` (definições de cron para Stories e preseed)
- Registros auxiliares: `RELATORIO_LTM_VINCULACAO_LOGS_20251030_0107.md`

## Mapeamento de Serviços e Horários

### Serviços de Stories
- Serviço: `Stories-09h`
  - Horário: `09:00 BRT` → `12:00 UTC`
  - Cron: `0 12 * * *`
  - Comando: `autopost --stories`

- Serviço: `Stories-15h`
  - Horário: `15:00 BRT` → `18:00 UTC`
  - Cron: `0 18 * * *`
  - Comando: `autopost --stories`

- Serviço: `Stories-21h`
  - Horário: `21:00 BRT` → `00:00 UTC`
  - Cron: `0 0 * * *`
  - Comando: `autopost --stories`

### Serviços de Feed
- Serviço: `Feed-06h`
  - Horário: `06:00 BRT` → `09:00 UTC`
  - Cron (derivado): `0 9 * * *`
  - Comando: `autopost`

- Serviço: `Feed-12h`
  - Horário: `12:00 BRT` → `15:00 UTC`
  - Cron (derivado): `0 15 * * *`
  - Comando: `autopost`

- Serviço: `Feed-19h`
  - Horário: `19:00 BRT` → `22:00 UTC`
  - Cron (derivado): `0 22 * * *`
  - Comando: `autopost`

## Observações
- No `railway.yaml.backup` constam tarefas de preparação (preseed) antes de alguns horários de Stories:
  - `evening_stories_preseed`: `20:00 BRT` → `23:00 UTC` — Cron: `0 23 * * *` — Comando: `python src/main.py preseed`
  - `midday_stories_preseed`: `14:00 BRT` → `17:00 UTC` — Cron: `0 17 * * *` — Comando: `python src/main.py preseed`
- O arquivo `railway.yaml` atual é minimalista e a configuração de cron é realizada pela UI do Railway (ver `INSTRUCOES_RAILWAY_CRON.md`).
- Logs históricos indicam serviços ativos de Stories com execução nos horários acima; serviços de Feed podem variar em nomenclatura no projeto e devem ser confirmados na UI.

## Status e Próximos Passos
- Status: Serviços de Stories confirmados com cron; horários de Feed derivados da política publicada.
- Próximos passos: Validar nomes exatos dos serviços de Feed na UI do Railway e confirmar cron correspondente.