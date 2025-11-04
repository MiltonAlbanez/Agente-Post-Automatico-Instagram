# LTM POST 6H BRT

## Sumário Rápido
- Serviço: Feed automático às 6h BRT (UTC-3)
- Agendamento no Railway: 09:00 UTC diariamente
- Comando de execução: `python src/main.py autopost`
- Fallback Standalone: Ativado se `POSTGRES_DSN/DATABASE_URL` ausente ou indisponível
- Testes A/B: Formato/Hashtags/Estilo de imagem aplicados via `get_ab_test_config`

## Fluxo de Trabalho
- Detecta variáveis de ambiente e credenciais, com fallback para `accounts.json` (Telegram).
- Verifica DB: se indisponível, ativa modo Standalone temático (motivacional por padrão).
- Integra tema semanal; em horários matinais, aplica "cunho espiritual obrigatório".
- Gera conteúdo original (OpenAI), seleciona imagem (Unsplash) conforme tema e AB config.
- Faz upload no Supabase e publica no Instagram; notifica via Telegram.
- Registra variantes A/B e resultados no dashboard/performance.

## Configurações Essenciais
- Banco: `POSTGRES_DSN` ou `DATABASE_URL` (opcional no Standalone).
- Mídia: `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY` (ou `SUPABASE_ANON_KEY` conforme setup).
- Instagram: `IG_GRAPH_TOKEN` (ou variáveis equivalentes usadas pelo `instagram_client.py`).
- Telegram: tokens carregados de `accounts.json` (fallback conforme `diagnostic_system.py`).
- Conteúdo: `OPENAI_API_KEY`, `UNSPLASH_ACCESS_KEY`, `REPLICATE_API_TOKEN`.
- Infra: `railway.yaml`/`Procfile` para cron e comando.

## Passo a Passo Operacional
1) Pré-verificações: variáveis presentes, `accounts.json` válido, Supabase acessível, IG token ativo.
2) Agende no Railway: 09:00 UTC diário para este serviço.
3) Execução: `python src/main.py autopost` (one-off/cron).
4) Pipeline: tema semanal + AB config → gerar conteúdo + imagem → upload Supabase → publicar feed.
5) Notificação: Telegram confirma sucesso; verifique logs e dashboard A/B.

## Requisitos e Dependências
- Python 3.10+ e `requirements.txt` instalado.
- Supabase bucket configurado; Instagram Graph habilitado.
- Conectividade externa (OpenAI/Unsplash) para Standalone enriquecido.

## Diagrama Simplificado
```
Start → Carregar ENV/credenciais → DB OK?
  ├─ Sim: Coletar conteúdo → Aplicar AB → Gerar post
  └─ Não: Standalone temático → OpenAI+Unsplash → Gerar post
→ Upload Supabase → Post Instagram → Notificar Telegram → Logar AB
```

## Notas Específicas do Horário
- 6h (manhã) aplica tom espiritual obrigatório se indicado pelo sistema temático.