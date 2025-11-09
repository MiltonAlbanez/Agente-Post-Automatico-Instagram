# 🚀 CONFIGURAÇÃO CRON RAILWAY - AGENTE POST AUTOMÁTICO

## ✅ ESTRUTURA CORRETA IMPLEMENTADA

**SOLUÇÃO ADOTADA**: Múltiplos serviços conectados ao mesmo repositório GitHub, cada um com configuração individual.

**VANTAGENS**:
- ✅ Cada serviço tem seu próprio cron schedule
- ✅ Todos conectados ao mesmo código GitHub
- ✅ Configurações independentes por tipo de conteúdo
- ✅ Evita conflitos de execução simultânea

---

## 📋 ESTRUTURA DE SERVIÇOS CONFIGURADA

### 🎯 ARQUITETURA ATUAL
```
Repositório GitHub (único)
├── Serviço 1: Feed 06:00 BRT
├── Serviço 2: Feed 12:00 BRT  
├── Serviço 3: Feed 19:00 BRT
├── Serviço 4: Stories 09:00 BRT
├── Serviço 5: Stories 15:00 BRT
└── Serviço 6: Stories 21:00 BRT
```

---

## ⏰ CRONOGRAMAS CORRETOS ESPECIFICADOS

### 📱 FEED POSTS
**Horários BRT**: 06:00, 12:00, 19:00 (todos com preseed)

| Serviço | Horário BRT | Horário UTC | Cron Schedule | Variável AUTOCMD |
|---------|-------------|-------------|---------------|------------------|
| Feed-06h | 06:00 BRT   | 09:00 UTC   | `0 9 * * *`   | `autopost` |
| Feed-12h | 12:00 BRT   | 15:00 UTC   | `0 15 * * *`  | `autopost` |
| Feed-19h | 19:00 BRT   | 22:00 UTC   | `0 22 * * *`  | `autopost` |

### 📖 STORIES
**Horários BRT**: 09:00, 15:00, 21:00 (todos com preseed)

| Serviço | Horário BRT | Horário UTC | Cron Schedule | Variável AUTOCMD |
|---------|-------------|-------------|---------------|------------------|
| Stories-09h | 09:00 BRT   | 12:00 UTC   | `0 12 * * *`  | `autopost --stories` |
| Stories-15h | 15:00 BRT   | 18:00 UTC   | `0 18 * * *`  | `autopost --stories` |
| Stories-21h | 21:00 BRT   | 00:00 UTC   | `0 0 * * *`   | `autopost --stories` |

---

## 🔧 CONFIGURAÇÃO PADRÃO POR SERVIÇO

### Para Serviços de FEED:
**Variáveis de Ambiente**:
```
AUTOCMD = autopost
```

**Cron Schedule**: Um único horário por serviço (conforme tabela acima)

### Para Serviços de STORIES:
**Variáveis de Ambiente**:
```
AUTOCMD = autopost --stories
```

**Cron Schedule**: Um único horário por serviço (conforme tabela acima)

---

## 📝 PROCESSO DE CRIAÇÃO DE NOVOS SERVIÇOS

### 1. Criar Novo Serviço
- No Railway Dashboard → **New Service**
- Selecionar **GitHub Repository**
- Escolher o mesmo repositório do projeto
- Dar nome descritivo (ex: "Feed-06h", "Stories-09h")

### 2. Configurar Variáveis
- Acessar **Variables**
- Adicionar `AUTOCMD` conforme tipo de conteúdo
- Configurar outras variáveis necessárias

### 3. Configurar Cron
- Acessar **Settings** → **Cron**
- Adicionar **um único** cron schedule
- Usar horário UTC correspondente

### 4. Deploy e Monitoramento
- Fazer deploy do serviço
- Monitorar logs para verificar execução
- Testar funcionamento nos horários programados

---

## ✅ VERIFICAÇÃO E MONITORAMENTO

### 🔍 Checklist de Verificação por Serviço:
1. **Deploy Completo**: ✅ Serviço deployado com sucesso
2. **Variável AUTOCMD**: ✅ Configurada corretamente
3. **Cron Schedule**: ✅ Um único horário configurado
4. **Logs**: ✅ Execuções aparecendo nos logs
5. **Timing**: ✅ "Last Run" e "Next Run" corretos

### 📊 Monitoramento Contínuo:
- **Logs de Execução**: Verificar se cada serviço executa no horário correto
- **Status de Saúde**: Monitorar se execuções terminam adequadamente
- **Performance**: Acompanhar tempo de execução de cada job
- **Erros**: Identificar e corrigir falhas rapidamente

---

## ⚠️ REQUISITOS TÉCNICOS RAILWAY

### ✅ Requisitos Atendidos:
- **Execução Única**: Cada serviço executa apenas uma vez por schedule
- **Término Adequado**: Processo termina após completar a tarefa
- **Intervalo Mínimo**: Respeitado intervalo de 5+ minutos entre execuções
- **Horário UTC**: Todos os horários configurados em UTC
- **Sem Serverless**: Modo serverless desabilitado para cron jobs

### 📌 Entrypoint da Aplicação
- **Arquivo principal**: `src/main.py`
- **Comando base**: utilizar `AUTOCMD` para definir a ação (ex.: `autopost`, `autopost --stories`)
- **Observação**: os serviços de cron devem executar o comando definido em `AUTOCMD` e encerrar após concluir a tarefa.

### 🔐 Lista consolidada de variáveis de ambiente (Railway)
Use esta referência para configurar variáveis no Railway. Valores sensíveis devem ser definidos no ambiente; não mantenha tokens no código.

- `AUTOCMD` — define a ação do job (ex.: `autopost`)
- `OPENAI_API_KEY` — chave da API OpenAI
- `REPLICATE_TOKEN` — token da API Replicate
- `RAPIDAPI_KEY` — chave da RapidAPI
- `RAPIDAPI_HOST` — host principal da API do Instagram via RapidAPI
- `RAPIDAPI_ALT_HOSTS` — hosts alternativos (fallback)
- `TELEGRAM_BOT_TOKEN` — token do bot para notificações
- `TELEGRAM_CHAT_ID` — chat id para notificações
- `INSTAGRAM_BUSINESS_ACCOUNT_ID_MILTON` — ID da conta business (Milton)
- `INSTAGRAM_ACCESS_TOKEN_MILTON` — access token da conta (Milton)
- `INSTAGRAM_BUSINESS_ACCOUNT_ID_ALBANEZ` — ID da conta business (Albanez)
- `INSTAGRAM_ACCESS_TOKEN_ALBANEZ` — access token da conta (Albanez)
- `POSTGRES_DSN` — DSN do banco (opcional; Railway pode injetar)
- `SUPABASE_URL` — URL do projeto Supabase (opcional)
- `SUPABASE_SERVICE_KEY` — chave de serviço do Supabase (opcional)
- `SUPABASE_BUCKET` — bucket de imagens (opcional)
- `RAILWAY_ENVIRONMENT` — ambiente (`production` recomendado)
- `TZ` — timezone (ex.: `America/Sao_Paulo`)
- `PYTHONUNBUFFERED` — `1` para logs sem buffer

Exemplo de configuração rápida (Railway CLI):

```
railway variables set AUTOCMD="autopost"
railway variables set OPENAI_API_KEY="..."
railway variables set REPLICATE_TOKEN="..."
railway variables set RAPIDAPI_KEY="..."
railway variables set RAPIDAPI_HOST="instagram-scraper-api2.p.rapidapi.com"
railway variables set RAPIDAPI_ALT_HOSTS="instagram-scraper.p.rapidapi.com,instagram-scraper-api.p.rapidapi.com,instagram-bulk-scraper-latest.p.rapidapi.com"
railway variables set TELEGRAM_BOT_TOKEN="..."
railway variables set TELEGRAM_CHAT_ID="..."
railway variables set INSTAGRAM_BUSINESS_ACCOUNT_ID_MILTON="..."
railway variables set INSTAGRAM_ACCESS_TOKEN_MILTON="..."
railway variables set INSTAGRAM_BUSINESS_ACCOUNT_ID_ALBANEZ="..."
railway variables set INSTAGRAM_ACCESS_TOKEN_ALBANEZ="..."
railway variables set RAILWAY_ENVIRONMENT="production"
railway variables set TZ="America/Sao_Paulo"
railway variables set PYTHONUNBUFFERED="1"
```

### 🚫 Limitações Conhecidas:
- **Precisão de Tempo**: Pode variar alguns minutos
- **Execução Simultânea**: Evitada com serviços separados
- **Dependências**: Cada serviço é independente

---

## 🎯 VANTAGENS DA ESTRUTURA ATUAL

### ✅ Benefícios Implementados:
- **Isolamento**: Cada horário em serviço separado
- **Escalabilidade**: Fácil adicionar/remover horários
- **Manutenção**: Configuração individual por serviço
- **Monitoramento**: Logs específicos por horário
- **Confiabilidade**: Falha em um serviço não afeta outros

### 🔗 Documentação Railway:
- [Cron Jobs Reference](https://docs.railway.com/reference/cron-jobs)
- [Running Scheduled Jobs](https://docs.railway.com/guides/cron-jobs)
- [Multiple Services Guide](https://docs.railway.com/guides/services)

---

## 📈 STATUS ATUAL

**✅ CONFIGURAÇÃO COMPLETA E OPERACIONAL**

- **6 Serviços Ativos**: Todos conectados ao mesmo repositório GitHub
- **Horários Configurados**: Feed (06h, 12h, 19h) + Stories (09h, 15h, 21h) BRT
- **Automação Funcionando**: Sistema executando conforme programado
- **Monitoramento Ativo**: Logs e performance sendo acompanhados

**🚀 PRÓXIMOS PASSOS**: Monitoramento contínuo e otimizações conforme necessário