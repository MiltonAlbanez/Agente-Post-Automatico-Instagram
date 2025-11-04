# VARIÁVEIS AUSENTES NO RAILWAY
## Lista Completa das Variáveis Críticas que Precisam ser Adicionadas

### 🚨 VARIÁVEIS CRÍTICAS AUSENTES (IMPEDEM FUNCIONAMENTO)

#### 1. OPENAI_API_KEY
- **Função**: Comunicação com API da OpenAI para geração de conteúdo
- **Criticidade**: CRÍTICA - Sistema não funciona sem ela
- **Formato**: `sk-proj-...` (chave da OpenAI)
- **Onde obter**: Dashboard da OpenAI (https://platform.openai.com/api-keys)

#### 2. RAPIDAPI_KEY
- **Função**: Acesso às APIs do RapidAPI para coleta de dados
- **Criticidade**: CRÍTICA - Coleta de dados falha sem ela
- **Formato**: String alfanumérica longa
- **Onde obter**: Dashboard do RapidAPI

#### 3. TELEGRAM_BOT_TOKEN
- **Função**: Envio de notificações via Telegram
- **Criticidade**: ALTA - Notificações silenciosamente falham
- **Formato**: `1234567890:AAF...` (token do bot)
- **Onde obter**: @BotFather no Telegram

#### 4. TELEGRAM_CHAT_ID
- **Função**: ID do chat para receber notificações
- **Criticidade**: ALTA - Notificações não chegam ao destino
- **Formato**: Número (ex: `-1001234567890`)
- **Onde obter**: Enviar mensagem para o bot e usar API do Telegram

### 📋 INSTRUÇÕES PARA ADICIONAR NO RAILWAY

#### Passo 1: Acessar o Painel Railway
1. Acesse https://railway.app/
2. Faça login na sua conta
3. Selecione o projeto "Histórias 21h"
4. Vá para a aba "Variables"

#### Passo 2: Adicionar Cada Variável
Para cada variável listada acima:

1. Clique em "New Variable"
2. Digite o nome EXATO da variável (em inglês)
3. Cole o valor correspondente
4. Clique em "Add"

#### Passo 3: Verificar Configuração Final
Após adicionar todas as variáveis, você deve ter:

**VARIÁVEIS EXISTENTES (renomeadas):**
- `INSTAGRAM_ACCESS_TOKEN` (renomeado de TOKEN_DE_ACESSO_DO_INSTAGRAM)
- `INSTAGRAM_BUSINESS_ACCOUNT_ID` (renomeado de ID_DA_CONTA_COMERCIAL_DO_INSTAGRAM)
- `POSTGRES_DSN` (mantido)
- `DATABASE_URL` (mantido)
- `SUPABASE_URL` (mantido)
- `SUPABASE_SERVICE_KEY` (mantido)
- `SUPABASE_BUCKET` (mantido)

**VARIÁVEIS NOVAS (adicionadas):**
- `OPENAI_API_KEY`
- `RAPIDAPI_KEY`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

### 🔍 VARIÁVEIS OPCIONAIS (RECOMENDADAS)

#### RAPIDAPI_HOST
- **Função**: Host específico para APIs do RapidAPI
- **Criticidade**: MÉDIA - Pode usar valor padrão
- **Valor sugerido**: Verificar documentação da API específica

#### SUPABASE_ANON_KEY
- **Função**: Chave anônima do Supabase para operações públicas
- **Criticidade**: BAIXA - Usado em contextos específicos
- **Onde obter**: Dashboard do Supabase

#### RAILWAY_ENVIRONMENT
- **Função**: Identificação do ambiente Railway
- **Criticidade**: BAIXA - Usado para logs e debugging
- **Valor sugerido**: `production`

#### AUTOCMD
- **Função**: Comando automático para inicialização
- **Criticidade**: BAIXA - Sistema funciona sem ela
- **Valor sugerido**: Verificar necessidade específica

### ⚠️ IMPORTANTE: ORDEM DE EXECUÇÃO

1. **PRIMEIRO**: Renomear variáveis existentes (conforme GUIA_CORRECAO_IMEDIATA_RAILWAY.md)
2. **SEGUNDO**: Adicionar as 4 variáveis críticas listadas acima
3. **TERCEIRO**: Fazer redeploy da aplicação
4. **QUARTO**: Executar script de verificação

### 🎯 RESULTADO ESPERADO

Após adicionar todas as variáveis:
- ✅ Sistema sairá do modo "automatic fallback"
- ✅ Notificações Telegram funcionarão
- ✅ Geração de conteúdo OpenAI funcionará
- ✅ Coleta de dados RapidAPI funcionará
- ✅ Logs mostrarão execuções reais, não simulações

### 📞 SUPORTE

Se alguma variável não estiver funcionando após a configuração:
1. Verifique se o nome está EXATAMENTE como listado (case-sensitive)
2. Verifique se não há espaços extras no início/fim do valor
3. Execute o script de verificação pós-correção
4. Consulte os logs do Railway para erros específicos

---
**Gerado em**: 23/10/2024 21:45
**Baseado na análise**: railway_discrepancy_analysis_20251023_213448.json