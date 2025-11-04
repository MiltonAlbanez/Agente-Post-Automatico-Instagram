# LTM POST 15H BRT

## Sumário Rápido
- Serviço: Feed automático às 15h BRT (UTC-3)
- Agendamento no Railway: 18:00 UTC diariamente
- Comando: `python src/main.py autopost`
- Fallback Standalone e Testes A/B ativos.

## Fluxo de Trabalho
- Carregamento de ENV/credenciais (fallback `accounts.json`).
- Checagem DB; se indisponível, Standalone temático.
- Tema semanal + AB → conteúdo + imagem.
- Upload Supabase → Publicação IG → Telegram.
- Registro A/B.

## Configurações Essenciais
- `POSTGRES_DSN`/`DATABASE_URL`, `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`.
- `IG_GRAPH_TOKEN`, tokens Telegram, `OPENAI_API_KEY`, `UNSPLASH_ACCESS_KEY`.

## Passo a Passo
1) Validar variáveis e serviços.
2) Agendar 18:00 UTC.
3) Executar comando.
4) Verificar publicação e alertas.

## Diagrama
```
Start → ENV → DB OK?/Fallback → Tema+AB → Supabase → IG → Telegram → AB
```