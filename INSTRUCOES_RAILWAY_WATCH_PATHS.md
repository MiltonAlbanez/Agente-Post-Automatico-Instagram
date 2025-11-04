# Watch Paths no Railway — Padrões recomendados

Este guia lista os padrões de Watch Paths sugeridos para seu serviço no Railway. Use estes padrões na seção **Deploy → Watch Paths** do serviço para disparar deploys somente quando arquivos relevantes forem alterados.

## Como configurar
- Abra o serviço no Railway → Deploy → Watch Paths.
- Selecione **Custom**.
- Cole os padrões abaixo em **Include** e **Exclude** conforme indicado.
- Salve e faça um push para validar se o comportamento está correto.

## Include (arquivos que devem disparar deploy)
```
src/**
accounts.json
requirements*.txt
Procfile
railway_scheduler.py
health_server.py
performance_monitor.py
notification_system.py
```

## Exclude (arquivos que NÃO devem disparar deploy)
```
.env*
**/.env*
tests/**
.github/**
docs/**
**/*.md
**/*.log
.vscode/**
.idea/**
```

## Observações
- Os padrões seguem o estilo **gitignore**.
- `src/**` cobre mudanças de código, inclusive `main.py` e pipelines.
- `accounts.json` precisa disparar deploy quando houver troca de tokens/contas.
- Excluímos `tests/**` e conteúdo de documentação para evitar deploys desnecessários.
- Se você desejar que mudanças em documentação também gerem deploys, remova `**/*.md` do Exclude.

## Start command recomendado
- Para execução 24/7 com agendamento, mantenha o **Start command** como:
```
python railway_scheduler.py
```
- Para execuções manuais ou jobs pontuais, utilize o módulo Python para evitar erros de import:
```
python -m src.main autopost --style "street"
python -m src.main unposted --limit 10
```

## Healthcheck
- O serviço expõe um health server em `health_server.py` (porta via `PORT`).
- Defina `healthcheckPath` como `/health` (já previsto em `railway.json`).

## Dicas de validação
- Após ajustar os Watch Paths, faça um commit alterando um arquivo incluído (ex.: `src/main.py`) e confirme que o deploy foi disparado.
- Em seguida, altere um arquivo excluído (ex.: `docs/README.md`) e confirme que o deploy **não** foi disparado.