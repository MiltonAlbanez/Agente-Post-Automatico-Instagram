# Checklist Minificado – Serviço 15h BRT

## Pré-execução
- Validar ENV essenciais (IG, Supabase, OpenAI, Unsplash).

## Execução
- Cron: 18:00 UTC diário.
- Comando: `python src/main.py autopost`.

## Verificação
- Post no IG; upload Supabase; alerta Telegram.
- Logs A/B/Standalone coerentes.

## Ação rápida
- Corrigir tokens/keys; Standalone assegura publicação sem DB.