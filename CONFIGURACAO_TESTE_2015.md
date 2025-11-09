# 🧪 CONFIGURAÇÃO TESTE 20:15 - RAILWAY

## 📋 Guia de Configuração Manual

### 1. **Acesso ao Dashboard**
1. Abra o Railway Dashboard no navegador
2. Selecione o projeto "Agente_Post_Auto_Insta"
3. Localize o serviço "teste 20:15"

### 2. **Configuração de Variáveis (Variables)**

#### **Variáveis Obrigatórias** ⚠️

```bash
# Comando de execução
AUTOCMD = autopost

# Instagram (OBRIGATÓRIAS)
INSTAGRAM_BUSINESS_ACCOUNT_ID = [SEU_ID_AQUI]
INSTAGRAM_ACCESS_TOKEN = [SEU_TOKEN_AQUI]

# APIs (OBRIGATÓRIAS)
OPENAI_API_KEY = [SUA_CHAVE_OPENAI]
RAPIDAPI_KEY = [SUA_CHAVE_RAPIDAPI]
RAPIDAPI_HOST = instagram-scraper-api2.p.rapidapi.com
REPLICATE_TOKEN = [SEU_TOKEN_REPLICATE]
```

#### **Variáveis Opcionais** ℹ️

```bash
# Telegram (para notificações)
TELEGRAM_BOT_TOKEN = [SEU_TOKEN_TELEGRAM]
TELEGRAM_CHAT_ID = [SEU_CHAT_ID]

# Supabase (para re-hospedagem de imagens)
SUPABASE_URL = [SUA_URL_SUPABASE]
SUPABASE_SERVICE_KEY = [SUA_CHAVE_SUPABASE]
SUPABASE_BUCKET = [SEU_BUCKET]

# RapidAPI (fallback)
RAPIDAPI_ALT_HOSTS = instagram-scraper.p.rapidapi.com,instagram-scraper-api.p.rapidapi.com
```

### 3. **Configuração do Cron Schedule**

```bash
15 23 * * *
```
*Executa diariamente às 20:15 BRT (23:15 UTC)*

### 4. **Passos de Configuração**

1. **Variables Section:**
   - Clique em "Variables" no serviço
   - Adicione cada variável usando o formato: `NOME = VALOR`
   - Clique em "Add" para cada variável

2. **Cron Schedule Section:**
   - Clique em "Settings" ou "Cron"
   - Adicione: `15 23 * * *`
   - Salve a configuração

### 5. **Verificação**

#### **Checklist de Configuração:**
- [ ] AUTOCMD = autopost
- [ ] INSTAGRAM_BUSINESS_ACCOUNT_ID configurado
- [ ] INSTAGRAM_ACCESS_TOKEN configurado
- [ ] OPENAI_API_KEY configurado
- [ ] RAPIDAPI_KEY configurado
- [ ] REPLICATE_TOKEN configurado
- [ ] Cron schedule: 15 23 * * *

#### **Variáveis Opcionais:**
- [ ] TELEGRAM_BOT_TOKEN (recomendado)
- [ ] TELEGRAM_CHAT_ID (recomendado)
- [ ] SUPABASE_URL (opcional)
- [ ] SUPABASE_SERVICE_KEY (opcional)
- [ ] SUPABASE_BUCKET (opcional)

### 6. **Teste Manual**

Para testar imediatamente sem esperar o cron:
1. Vá para o serviço "teste 20:15"
2. Clique em "Deploy" ou "Trigger Deploy"
3. Monitore os logs na aba "Logs"

### 7. **Logs Esperados**

```
✅ Configuração carregada
✅ Todas as variáveis necessárias estão configuradas
🎯 INICIANDO GERAÇÃO E PUBLICAÇÃO
📝 PROCESSANDO ITEM 1/1
✅ RESULTADO: {"status": "PUBLISHED"}
```

### 8. **Solução de Problemas**

#### **Erro de Credenciais:**
- Verifique se todas as variáveis obrigatórias estão preenchidas
- Confirme se os tokens não expiraram

#### **Erro de Banco:**
- O Railway fornece DATABASE_URL automaticamente
- Não é necessário configurar POSTGRES_DSN

#### **Erro de API:**
- Verifique se as chaves estão corretas
- Confirme se há créditos nas APIs (OpenAI, Replicate)

### 9. **Monitoramento**

- **Logs em tempo real:** Aba "Logs" do serviço
- **Métricas:** Aba "Metrics" do serviço
- **Deployments:** Aba "Deployments" para histórico

---

## 🎯 Resultado Esperado

Após a configuração, o sistema irá:
1. Executar automaticamente às 20:15 BRT
2. Buscar conteúdo não postado no banco
3. Gerar descrição e legenda com IA
4. Criar imagem com Replicate
5. Publicar no Instagram
6. Enviar notificação no Telegram (se configurado)

**Status:** ✅ Pronto para teste