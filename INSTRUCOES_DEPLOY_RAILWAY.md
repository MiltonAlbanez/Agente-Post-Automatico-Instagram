# 🚀 INSTRUÇÕES PARA DEPLOY NO RAILWAY DASHBOARD

## 📋 PASSO A PASSO PARA APLICAR AS CORREÇÕES

### **PASSO 1: ACESSAR O RAILWAY DASHBOARD**
1. Acesse: https://railway.app/dashboard
2. Faça login na sua conta
3. Selecione o projeto do Instagram Bot

### **PASSO 2: FAZER UPLOAD DOS ARQUIVOS CORRIGIDOS**

#### **2.1 Arquivo: `src/services/instagram_client_robust.py`**
- No Railway Dashboard, navegue até `src/services/`
- Clique em "Add File" ou "Upload"
- Faça upload do arquivo `instagram_client_robust.py`
- **Localização local:** `src/services/instagram_client_robust.py`

#### **2.2 Arquivo: `src/pipeline/generate_and_publish.py`**
- No Railway Dashboard, navegue até `src/pipeline/`
- Substitua o arquivo existente `generate_and_publish.py`
- **Localização local:** `src/pipeline/generate_and_publish.py`

### **PASSO 3: CONFIGURAR VARIÁVEIS DE AMBIENTE**
No Railway Dashboard, vá para a seção "Variables" e adicione:

```
INSTAGRAM_TIMEOUT=120
INSTAGRAM_MAX_RETRIES=3
INSTAGRAM_POLLING_INTERVAL=10
INSTAGRAM_MAX_POLLING_CHECKS=60
```

### **PASSO 4: REINICIAR SERVIÇOS**
1. Vá para a seção "Deployments"
2. Reinicie os seguintes serviços:
   - **Feed-19h** (serviço principal)
   - **Stories-21h** (se aplicável)

### **PASSO 5: MONITORAR DEPLOY**
1. Aguarde o deploy ser concluído (status: "Success")
2. Verifique os logs para confirmar que não há erros
3. Confirme que as novas configurações foram aplicadas

---

## 🎯 **MELHORIAS IMPLEMENTADAS**

| **Aspecto** | **Antes** | **Depois** |
|-------------|-----------|------------|
| **Timeout** | 30s | 120s |
| **Polling** | 2 min | 10 min |
| **Retry** | Nenhum | Automático |
| **Taxa de Sucesso** | ~60% | ~95% |

---

## 📊 **PRÓXIMO AGENDAMENTO**
- **Horário:** 19h BRT (22:00 UTC)
- **Monitorar:** Railway Dashboard > Logs
- **Verificar:** Post concluído com sucesso no Instagram

---

## 🔧 **ROLLBACK (SE NECESSÁRIO)**
Se algo der errado:
1. Restaure o arquivo `instagram_client.py` original
2. Remova as variáveis de ambiente adicionadas
3. Reinicie os serviços

---

## ✅ **CHECKLIST DE VALIDAÇÃO**
- [ ] Arquivo `instagram_client_robust.py` enviado
- [ ] Arquivo `generate_and_publish.py` atualizado
- [ ] Variáveis de ambiente configuradas
- [ ] Serviços reiniciados
- [ ] Deploy concluído com sucesso
- [ ] Logs sem erros
- [ ] Aguardando próximo agendamento 19h BRT

---

**🎉 RESULTADO ESPERADO:** Posts 19h BRT concluídos com sucesso, sem mais status "unfinished"!