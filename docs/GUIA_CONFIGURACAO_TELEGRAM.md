# 🤖 Guia de Configuração do Telegram - Bot Único

## 📋 Resumo da Decisão

**USAR UM ÚNICO BOT** para todas as funcionalidades do sistema:
- ✅ Notificações de publicação (sistema original)
- ✅ Alertas de performance (sistema avançado)
- ✅ Resumos diários e semanais
- ✅ Alertas de erro

## 🚀 Passo a Passo da Configuração

### 1. Criar o Bot (se ainda não existe)

```
1. Abra o Telegram
2. Procure por @BotFather
3. Digite: /newbot
4. Escolha um nome: "Albanez Automation Bot"
5. Escolha um username: "albanez_automation_bot"
6. Copie o TOKEN gerado
```

### 2. Obter o Chat ID

```
1. Adicione o bot ao seu chat/grupo
2. Envie uma mensagem qualquer para o bot
3. Acesse: https://api.telegram.org/bot<SEU_TOKEN>/getUpdates
4. Procure por "chat":{"id": NÚMERO
5. Copie esse número (seu chat_id)
```

### 3. Configurar o Sistema

#### A. Arquivo de Ambiente (.env)
```env
# Telegram Configuration
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789
```

#### B. Arquivo de Notificações (config/notification_config.json)
```json
{
  "telegram": {
    "enabled": true,
    "bot_token": "123456789:ABCdefGHIjklMNOpqrsTUVwxyz",
    "chat_id": "123456789",
    "alerts": {
      "low_engagement": true,
      "high_performance": true,
      "daily_summary": true,
      "error_alerts": true
    }
  }
}
```

## 🔄 Unificação dos Sistemas

### Tipos de Mensagens que o Bot Enviará:

1. **📱 Publicações** (Sistema Original)
   ```
   ✅ Conteúdo publicado com sucesso!
   📱 Feed: 123456789
   📖 Stories: 987654321
   ```

2. **⚠️ Alertas de Performance** (Sistema Avançado)
   ```
   📊 Albanez Assistência Técnica
   
   ⚠️ ALERTA: Baixo Engagement
   📉 Taxa de engagement: 1.5%
   🎯 Meta mínima: 2.0%
   ```

3. **📈 Resumos Diários**
   ```
   📊 Albanez Assistência Técnica
   
   📈 RESUMO DIÁRIO
   📅 Data: 15/01/2024
   📊 Posts publicados: 3
   ```

4. **🚨 Alertas de Erro**
   ```
   🚨 ERRO NO SISTEMA
   ⚠️ Falha na publicação
   🕐 Horário: 15/01/2024 14:30
   ```

## ✅ Vantagens da Configuração Única

- **Simplicidade**: Um único token para gerenciar
- **Consistência**: Todas as mensagens do mesmo remetente
- **Facilidade**: Configuração em um local
- **Manutenção**: Menos pontos de falha

## 🧪 Teste da Configuração

Execute o teste para verificar se tudo está funcionando:

```bash
python test_advanced_features.py
```

Você deve receber uma mensagem de teste no Telegram confirmando que o sistema está funcionando.

## 🔧 Troubleshooting

### Problema: "Telegram não configurado"
**Solução**: Verifique se o bot_token e chat_id estão corretos nos arquivos de configuração.

### Problema: "Forbidden: bot was blocked by the user"
**Solução**: Desbloqueie o bot no Telegram e envie /start.

### Problema: "Chat not found"
**Solução**: Verifique se o chat_id está correto e se o bot foi adicionado ao chat.

## 📞 Suporte

Se encontrar problemas:
1. Verifique os logs em `/logs/`
2. Execute o teste: `python test_advanced_features.py`
3. Confirme as configurações nos arquivos mencionados

---

**✨ Com essa configuração, você terá um sistema completo de notificações Telegram funcionando perfeitamente!**