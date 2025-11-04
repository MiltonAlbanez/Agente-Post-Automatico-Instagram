# Guia de Deploy, LTM, Backup e Rollback

## Visão Geral
- Deploy consolidado com inclusão no LTM, health checks e commit no Git.
- Backup automático diário versionado usando `BackupManager`.
- Rollback rápido para restaurar configurações e arquivos.

## 1) Commit em Controle de Versão
- Verifique alterações: `git status`
- Adicione arquivos: `git add -A`
- Commit: `git commit -m "Deploy: LTM + backup diário + rollback + docs"`
- Push (se aplicável): `git push`

## 2) Inclusão no Load Balancer (LTM)
- Configuração em `config/ltm_config.json` com health checks e parâmetros de balanceamento.
- Valide e gere relatório: `python scripts/ltm_register_app.py`
- Conecte os nós `primary` e `secondary` conforme sua infraestrutura.

### Health Check
- Endpoint esperado: `http://localhost:8000/health` (ajuste conforme deploy).
- Status esperado: `200`.

## 3) Backup Completo com Versão
- Use o `BackupManager` para criar backup completo:
  - Comando manual: `python -m src.services.backup_manager --full`
  - Backups são salvos em `backups/AAAAmmdd_HHMMSS/` com ZIP e metadados.

## 4) Backup Automático Diário
- Inicie o agendador: `python scripts/run_backup_scheduler.py`.
- Configure um serviço no Railway ou um cron job para executar continuamente.
- Os backups diários incluem histórico de versões e limpeza de antigos (conforme config).

## 5) Procedimento de Rollback
- Restaurar último backup: `python scripts/rollback.py`
- Restaurar específico: `python scripts/rollback.py --backup backups/20251023_205511`
- Recupera arquivos apagados e configurações do backup.
- Relatórios são salvos em `backups/rollback_report_*.json`.

## 6) Documentação e Auditoria
- Relatórios de LTM gerados em `backups/ltm_register_report_*.json`.
- Mantenha histórico de commit e registros de backup/rollback para auditoria.

## Notas
- Railway cron deve ser configurado via interface web.
- Ajuste endpoints e nós conforme seu ambiente (dev/production).