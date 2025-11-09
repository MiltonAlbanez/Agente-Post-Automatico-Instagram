# Instruções para Configurar Cron Jobs no Railway

## Problema Identificado
O Railway **NÃO** lê configurações de cron do `railway.yaml`. Os cron jobs devem ser configurados na interface web do Railway.

## Solução Baseada na Documentação Oficial

### 1. Configuração Atual Correta
- ✅ `railway.json` configurado com `startCommand` dinâmico
- ✅ Variável `AUTOCMD` permite controlar o comando executado
- ✅ `sleepApplication: true` para economizar recursos

### Entrypoint da Aplicação
- **Arquivo principal**: `src/main.py`
- **Comando base**: usar `AUTOCMD` para definir a ação (`autopost`, `autopost --stories`)
- **Execução**: o processo deve iniciar, executar a tarefa e ENCERRAR ao término (sem manter web servers ou processos em background em jobs de cron).

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

#### Passo 3: Deploy
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