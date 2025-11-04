# Checklist Minificado – Serviço 21h BRT

## Pré-execução
- Validar IG/Supabase; `accounts.json` com Telegram.

## Execução
- Cron: 00:00 UTC diário.
- `python src/main.py autopost`.

## Verificação
- Post IG; Telegram alerta; Supabase ok.
- AB/Standalone registrados nos logs.

## Ação rápida
- Ajustar tokens/keys se falhas; Standalone cobre sem DB.