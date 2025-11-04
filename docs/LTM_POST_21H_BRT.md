# LTM POST 21H BRT

## Sumário Rápido
- Serviço: Feed automático às 21h BRT (UTC-3)
- Agendamento no Railway: 00:00 UTC diariamente (mudança de dia)
- Execução: `python src/main.py autopost`
- Standalone e A/B habilitados.

## Fluxo de Trabalho
- Carrega ENV e credenciais (fallback `accounts.json`).
- Verifica DB; fallback Standalone se falha.
- Tema semanal noturno; tom reflexivo/encerramento.
- Conteúdo (OpenAI), imagem (Unsplash), AB aplicado.
- Upload Supabase → Post IG → Telegram.
- Log A/B.

## Configurações Essenciais
- `POSTGRES_DSN`/`DATABASE_URL`, Supabase, IG, Telegram, OpenAI, Unsplash.

## Passo a Passo
1) Validar ENV.
2) Agendar 00:00 UTC diário (atenção ao rollover de data).
3) Executar e verificar publicação/alertas.

## Diagrama
```
Start → ENV → DB?/Standalone → Tema+AB → Supabase → IG → Telegram → AB
```