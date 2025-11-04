# Instruções para Configurar Cron Jobs no Railway

## Problema Identificado
O Railway **NÃO** lê configurações de cron do `railway.yaml`. Os cron jobs devem ser configurados na interface web do Railway.

## Solução Baseada na Documentação Oficial

### 1. Configuração Atual Correta
- ✅ `railway.json` configurado com `startCommand` dinâmico
- ✅ Variável `AUTOCMD` permite controlar o comando executado
- ✅ `sleepApplication: true` para economizar recursos

### 2. Como Configurar os Cron Jobs na Interface Railway

#### Serviço Principal (Feed Posts)
**Nome do Serviço:** calm-spirit (atual)
**Variáveis de Ambiente:**
```
AUTOCMD=autopost
```

**Schedules a Configurar na UI:**
- `55 8 * * *` - Preseed matinal (08:55 UTC = 05:55 BRT)
- `0 9 * * *` - Post matinal (09:00 UTC = 06:00 BRT)
- `55 14 * * *` - Preseed meio-dia (14:55 UTC = 11:55 BRT)
- `0 15 * * *` - Post meio-dia (15:00 UTC = 12:00 BRT)
- `55 21 * * *` - Preseed noturno (21:55 UTC = 18:55 BRT)
- `0 22 * * *` - Post noturno (22:00 UTC = 19:00 BRT)
- `30 15 * * *` - Teste 12:30 BRT (15:30 UTC)

#### Serviço Stories (Novo Serviço Necessário)
**Nome do Serviço:** stories-service
**Variáveis de Ambiente:**
```
AUTOCMD=autopost --stories
```

#### Serviço Backup (Cron One-Off)
Para backups diários via cron, use execução pontual (one-off) que termina após completar:

**Nome do Serviço:** backup-cron
**Variáveis de Ambiente:** nenhuma necessária
**Schedules a Configurar na UI:**
- `0 2 * * *` — Backup diário às 02:00 UTC: comando `python scripts/run_oneoff_backup.py --type daily`
- `0 3 * * 0` — Backup completo semanal aos domingos 03:00 UTC: comando `python scripts/run_oneoff_backup.py --type full`

Observações:
- O comando deve iniciar e finalizar (não manter processo ativo).
- Não use `scripts/run_backup_scheduler.py` em cron; ele é um serviço contínuo, não cron.

**Schedules a Configurar na UI:**
- `0 11 * * *` - Preseed stories matinal (11:00 UTC = 08:00 BRT)
- `0 12 * * *` - Stories matinal (12:00 UTC = 09:00 BRT)
- `0 17 * * *` - Preseed stories meio-dia (17:00 UTC = 14:00 BRT)
- `0 18 * * *` - Stories meio-dia (18:00 UTC = 15:00 BRT)
- `0 23 * * *` - Preseed stories noturno (23:00 UTC = 20:00 BRT)
- `0 0 * * *` - Stories noturno (00:00 UTC = 21:00 BRT)

### 3. Passos para Implementar

#### Passo 1: Configurar Serviço Principal
1. Acesse o projeto no Railway
2. Selecione o serviço "calm-spirit"
3. Vá em Settings > Variables
4. Adicione: `AUTOCMD=autopost`
5. Vá em Settings > Cron Schedule
6. Adicione cada horário listado acima

#### Passo 2: Criar Serviço Stories
1. No projeto Railway, clique em "New Service"
2. Conecte ao mesmo repositório GitHub
3. Nome: "stories-service"
4. Em Variables, adicione: `AUTOCMD=autopost --stories`
5. Em Cron Schedule, adicione os horários de stories

#### Passo 3: Criar Serviço Backup Cron
1. No projeto Railway, clique em "New Service"
2. Conecte ao mesmo repositório GitHub
3. Nome: "backup-cron"
4. Em Cron Schedule, adicione os horários e comandos acima

#### Passo 4: Deploy
1. Faça deploy de ambos os serviços
2. Verifique os logs nos horários agendados

### 4. Requisitos Importantes (Documentação Railway)

- ✅ **Execução deve terminar:** O comando deve executar e sair, não ficar rodando
- ✅ **Fechar recursos:** Não deixar conexões de banco abertas
- ✅ **Intervalo mínimo:** 5 minutos entre execuções
- ✅ **Timezone:** Todos os horários são em UTC
- ✅ **Execução única:** Se uma execução anterior ainda estiver rodando, a próxima será pulada

### 5. Monitoramento
- Verifique em "Deployments" se as execuções aparecem
- Monitore os logs durante os horários agendados
- Status "Active" indica que ainda está executando
- Status "Exited" indica execução completa

### 6. Troubleshooting
Se os cron jobs não executarem:
1. Verifique se o `startCommand` está correto no railway.json
2. Confirme que as variáveis de ambiente estão definidas
3. Verifique se os schedules estão salvos na UI
4. Monitore os logs para erros de execução

## Template: Monitor Logs

Este template orienta a configuração e análise de monitoramento de logs no Railway com foco em falhas e alertas.

### Localização dos arquivos de log
- Dashboard do Railway: `Service > Logs` (com timestamps)
- CLI: `railway logs --timestamp`
- Exportar logs para arquivo (PowerShell):
  - `powershell -Command "$ts=(Get-Date).ToString('yyyy-MM-dd_HH-mm-ss'); railway logs --timestamp | Out-File -Encoding utf8 backups\\railway_logs_$ts.log"`

### Padrões de mensagens de erro
- `ERROR`, `Traceback`, `Exception`, `Failed`, `Permission denied`
- `Timeout`, `NetworkError`, `HTTPError`, `429 Too Many Requests`
- `telegram` (erros de envio de alertas), `publish`, `instagram`

### Comandos úteis para análise
- Verificar logs recentes com timestamps: `railway logs --timestamp`
- Filtrar erros no Windows: `railway logs --timestamp | findstr /I /C:"ERROR" /C:"Traceback" /C:"Failed" /C:"Timeout"`
- Rodar monitor pontual com alertas: `python monitor_railway_logs.py --recent --alerts`
- Rodar monitor contínuo (polling): `python monitor_railway_logs.py --monitor --interval 30 --alerts`
- Agendador simples: `python log_check_scheduler.py --interval 10 --runs 6 --alerts`

### Exemplo de troubleshooting
1) Confirmar que a job executou no horário esperado (UI): `Service > Deployments`
2) Coletar logs com timestamp e salvar: comando de export acima
3) Filtrar termos críticos: `ERROR`, `Traceback`, `Timeout`, `Failed`
4) Reexecutar verificação e enviar alerta: `python monitor_railway_logs.py --recent --alerts`
5) Validar variáveis e credenciais: `railway variables`, `python test_telegram_integration.py`

---

### Investigação de falha no post automático das 15h (BRT)

1. Verificar o status da última execução
- UI: `Service > Deployments` e confirmar se houve execução às 15:00 BRT (18:00 UTC)
- Observações de status: `Active` (em execução), `Exited` (concluída), `Skipped` (pulado)
- CLI suporte: revisar `railway logs --timestamp` e identificar início/fim da execução

2. Analisar os logs do horário em questão
- Coletar janela entre 14:55 e 15:10 BRT (17:55–18:10 UTC)
- Filtrar termos: `publish`, `instagram`, `ERROR`, `Traceback`, `Timeout`, `Failed`
- Comando prático:
  - `railway logs --timestamp | findstr /I /C:" 18:" /C:"ERROR" /C:"Traceback" /C:"Failed"`
  - Dica: ajuste `18:` conforme UTC do horário alvo

3. Validar as credenciais e permissões
- Telegram: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` presentes (`railway variables`)
- Instagram: validar token/credenciais: `python test_instagram_token.py`
- Permissões de publicação (arquivos e paths acessíveis): `python test_image_upload.py`

4. Checar a conectividade com serviços externos
- Supabase: `python test_supabase_connectivity.py`
- RapidAPI fallback: `python test_rapidapi_fallback.py`
- Webhook/HTTP: revisar códigos `HTTPError` nos logs e latência

5. Verificar o consumo de recursos no momento da execução
- Dashboard do Railway: `Service > Metrics` (CPU, Memória, Rede)
- Histórico local: `python check_performance_db.py` (se aplicável)
- Sinais de throttling/limites: mensagens `429`, `Timeout`, queda de rede

### Ação corretiva sugerida
- Se houver `Timeout` ou `429`: reduzir carga e aumentar intervalos (`INSTAGRAM_POLLING_INTERVAL`, `INSTAGRAM_MAX_RETRIES`)
- Se falha de credenciais: atualizar variáveis e revalidar testes
- Se queda externa: habilitar retries/fallbacks e monitorar novamente
- Após ajustes, reexecutar validação: `python monitor_railway_logs.py --recent --alerts` e confirmar ausência de erros