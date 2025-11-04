# Checklist Minificado – Serviço 9h BRT

## Pré-execução
- IG token válido; Supabase configurado; `accounts.json` ok.

## Execução
- Cron: 12:00 UTC diário.
- Comando: `python src/main.py autopost`.

## Verificação
- Publicação IG, Telegram alerta, Supabase upload.
- AB variantes/Standalone conforme logs.

## Ação rápida
- Renovar token IG; corrigir Supabase; Standalone cobre sem DB.