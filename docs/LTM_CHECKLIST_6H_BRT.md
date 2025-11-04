# Checklist Minificado – Serviço 6h BRT

## Pré-execução
- Confirmar `IG_GRAPH_TOKEN` e acesso ao Supabase.
- `accounts.json` com tokens Telegram válidos.
- `OPENAI_API_KEY` e `UNSPLASH_ACCESS_KEY` configurados.

## Execução
- Cron Railway: 09:00 UTC diário.
- Comando: `python src/main.py autopost`.

## Verificação
- Post publicado no Instagram.
- Upload no Supabase ok.
- Alerta no Telegram recebido.
- Logs indicam AB aplicado ou Standalone ativado.

## Ação rápida
- IG falhou: revalidar token.
- Supabase erro: checar URL/KEY e bucket.
- Sem DB: Standalone cobre publicação.