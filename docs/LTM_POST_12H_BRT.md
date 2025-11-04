# LTM POST 12H BRT

## Sumário Rápido
- Serviço: Feed automático às 12h BRT (UTC-3)
- Agendamento no Railway: 15:00 UTC diariamente
- Comando de execução: `python src/main.py autopost`
- Fallback Standalone: Ativado se `POSTGRES_DSN/DATABASE_URL` ausente ou indisponível
- Testes A/B: Variantes aplicadas via `get_ab_test_config`

## Fluxo de Trabalho
- Carrega ENV e credenciais com fallback para `accounts.json` (Telegram).
- Verifica DB; se falhar, usa Standalone temático.
- Integra tema semanal conforme dia/horário (meio-dia, tom informativo).
- Gera conteúdo (OpenAI), escolhe imagem (Unsplash), aplica AB.
- Upload Supabase → Publica Instagram → Notifica Telegram.
- Loga resultados de A/B e atualiza relatórios.

## Configurações Essenciais
- DB: `POSTGRES_DSN` ou `DATABASE_URL`.
- Supabase: `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`.
- Instagram: `IG_GRAPH_TOKEN`.
- Telegram: tokens via `accounts.json`.
- Conteúdo: `OPENAI_API_KEY`, `UNSPLASH_ACCESS_KEY`, `REPLICATE_API_TOKEN`.

## Passo a Passo
1) Validar ENV/credenciais e acesso ao Supabase/IG.
2) Agendar no Railway: 15:00 UTC diário.
3) Executar: `python src/main.py autopost`.
4) Pipeline e publicação conforme fluxo.
5) Checar Telegram, logs e dashboard A/B.

## Diagrama Simplificado
```
Start → ENV/credenciais → DB?
  ├─ Sim: Conteúdo/AB
  └─ Não: Standalone temático
→ Supabase → Instagram → Telegram → AB logs
```