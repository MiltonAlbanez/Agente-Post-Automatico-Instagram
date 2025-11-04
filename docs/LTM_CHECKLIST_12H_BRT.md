# Checklist Minificado – Serviço 12h BRT

## Pré-execução
- IG token ativo; Supabase acessível.
- `accounts.json` válido; OpenAI/Unsplash chaves setadas.

## Execução
- Cron Railway: 15:00 UTC diário.
- `python src/main.py autopost`.

## Verificação
- Instagram publicado; Telegram alerta.
- AB variante registrada; Supabase ok.

## Ação rápida
- Token IG: renovar se 401.
- Supabase: ajustar credenciais.