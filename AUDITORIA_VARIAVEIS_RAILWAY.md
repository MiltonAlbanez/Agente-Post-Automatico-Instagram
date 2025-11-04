# Auditoria de Variáveis (Railway)

Data: 2025-10-24
Serviço: Stories 21h

## Resultado da Verificação no Painel
- Presentes:
  - `INSTAGRAM_ACCESS_TOKEN` (mascarado no painel)
  - `INSTAGRAM_BUSINESS_ACCOUNT_ID` (mascarado no painel)
  - `OPENAI_API_KEY` (mascarado no painel)
- Ausentes (no painel):
  - `TELEGRAM_BOT_TOKEN`
  - `TELEGRAM_CHAT_ID`
  - `RAPIDAPI_KEY`

Observação: Os três itens ausentes existem no arquivo local `CREDENCIAIS_PERMANENTES.json` e podem ser restaurados com segurança.

## Evidências e Prints (Checklist)
Para registro formal, capture prints no painel Railway:
- Aba `Variables` do serviço "Stories 21h" mostrando:
  - Presença de `INSTAGRAM_ACCESS_TOKEN`, `INSTAGRAM_BUSINESS_ACCOUNT_ID`, `OPENAI_API_KEY` (usar ícone de olho com valores ocultos)
  - Ausência de `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `RAPIDAPI_KEY`
- Aba `Cron Runs` (se aplicável) mostrando horários e status das execuções recentes.
- Aba `Deployments` para confirmar sucesso de deploy após ajustes.

Armazene os prints em `docs/railway/prints/2025-10-24/` com nomes:
- `variables_presentes.png`
- `variables_ausentes.png`
- `cron_runs.png`
- `deployments.png`

## Registro Detalhado das Configurações Atuais
- Fonte de verdade local: `CREDENCIAIS_PERMANENTES.json`
- Carregamento pelo código: `src/config.py` via `dotenv` + `os.getenv`
- Scripts de verificação:
  - `railway_realtime_variable_check.py` (diagnóstico em tempo real)
  - `final_system_verification.py` / `system_integrity_verification.py` (verificação ampla)

## Ação Recomendada
- Popular os três itens ausentes diretamente no painel Railway OU usar `railway variables set`:
  - `railway variables set TELEGRAM_BOT_TOKEN="<valor>"`
  - `railway variables set TELEGRAM_CHAT_ID="<valor>"`
  - `railway variables set RAPIDAPI_KEY="<valor>"`
- Confirmar em seguida com um print atualizado e anexar a esta auditoria.