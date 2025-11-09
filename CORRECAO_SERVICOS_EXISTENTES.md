# Correção dos 5 serviços existentes (Railway)

Este guia aplica as correções usando a configuração gerada em `railway_cron_config.json`.

Para cada serviço no Railway Dashboard, ajuste o Cron (em UTC), o Start Command e as variáveis de ambiente conforme abaixo.

- Serviço: `Agente Post 6h Auto Insta 05`
  - Cron (UTC): `0 9 * * *`  — equivale a 06:00 BRT
  - Start Command: `python railway_cron_diagnostic.py && python cron_lock_system.py cleanup && python main.py autopost`
  - Variáveis:
    - `CRON_NAME=post_6h`
    - `CRON_LOCK_TIMEOUT_MIN=30`
    - `TZ=America/Sao_Paulo`

- Serviço: `Agente Post 12h Auto Insta 02`
  - Cron (UTC): `0 15 * * *` — equivale a 12:00 BRT
  - Start Command: `python railway_cron_diagnostic.py && python cron_lock_system.py cleanup && python main.py autopost`
  - Variáveis:
    - `CRON_NAME=post_12h`
    - `CRON_LOCK_TIMEOUT_MIN=30`
    - `TZ=America/Sao_Paulo`

- Serviço: `Agente Post 15h Auto Insta 01`
  - Cron (UTC): `0 18 * * *` — equivale a 15:00 BRT
  - Start Command: `python railway_cron_diagnostic.py && python cron_lock_system.py cleanup && python main.py autopost`
  - Variáveis:
    - `CRON_NAME=post_15h`
    - `CRON_LOCK_TIMEOUT_MIN=30`
    - `TZ=America/Sao_Paulo`

- Serviço: `Agente Post 19h Auto Insta 03`
  - Cron (UTC): `0 22 * * *` — equivale a 19:00 BRT
  - Start Command: `python railway_cron_diagnostic.py && python cron_lock_system.py cleanup && python main.py autopost`
  - Variáveis:
    - `CRON_NAME=post_19h`
    - `CRON_LOCK_TIMEOUT_MIN=30`
    - `TZ=America/Sao_Paulo`

- Serviço: `Agente Post 21h Auto Insta 04`
  - Cron (UTC): `0 0 * * *` — equivale a 21:00 BRT (UTC do dia seguinte)
  - Start Command: `python railway_cron_diagnostic.py && python cron_lock_system.py cleanup && python main.py autopost`
  - Variáveis:
    - `CRON_NAME=post_21h`
    - `CRON_LOCK_TIMEOUT_MIN=30`
    - `TZ=America/Sao_Paulo`

Notas:
- Se o dashboard estiver em UTC, use os cron acima; em BRT, os horários correspondentes são 06h, 12h, 15h, 19h e 21h.
- `railway_cron_diagnostic.py` valida variáveis críticas antes da execução.
- `cron_lock_system.py cleanup` remove locks antigos, e o wrapper `main.py` aplica lock via `CRON_NAME`.