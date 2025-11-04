# Checklist Minificado – Serviço 19h BRT

## Pré-execução
- IG token; Supabase credenciais; `accounts.json` OK.

## Execução
- Cron: 22:00 UTC diário.
- Comando: `python -m src.main autopost`.

## Verificação
- Publicação IG e alerta Telegram.
- Supabase ok; variantes A/B registradas.

## Ação rápida
- Ver `SOLUCAO_FEED_19H_BRT.md` se engajamento.
- Corrigir variáveis com sufixo `\n` (usar nomes sem sufixo).