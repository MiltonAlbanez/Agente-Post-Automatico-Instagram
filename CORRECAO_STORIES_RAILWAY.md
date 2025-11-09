# 🔧 CORREÇÃO URGENTE - SERVIÇOS STORIES NO RAILWAY

## 🚨 PROBLEMA IDENTIFICADO

Os **3 serviços de Stories** no Railway ainda estão usando configuração antiga:
- ❌ **Comando atual:** `autopost --stories` (processa apenas 1 conta)
- ❌ **Credenciais:** Ambas contas com mesmo `instagram_id`

## ✅ SOLUÇÃO NECESSÁRIA

Atualizar **TODOS os 3 serviços de Stories** para usar:
- ✅ **Novo comando:** `multirun --stories --limit 1`
- ✅ **Credenciais únicas:** Cada conta com seu próprio `instagram_id`

---

## 📋 PASSO A PASSO - CORREÇÃO NO RAILWAY

### 🎯 **SERVIÇOS A CORRIGIR:**

| Serviço | Horário BRT | Horário UTC | Status |
|---------|-------------|-------------|---------|
| **Stories-09h** | 09:00 BRT | 12:00 UTC | ❌ Precisa correção |
| **Stories-15h** | 15:00 BRT | 18:00 UTC | ❌ Precisa correção |
| **Stories-21h** | 21:00 BRT | 00:00 UTC | ❌ Precisa correção |

---

## 🔧 **INSTRUÇÕES DETALHADAS:**

### **PARA CADA SERVIÇO DE STORIES:**

#### **1. Acessar o Serviço**
1. Abra o **Railway Dashboard**
2. Selecione o projeto do Instagram
3. Clique no serviço **Stories-09h** (primeiro)

#### **2. Atualizar Variáveis**
1. Clique em **"Variables"** (lado esquerdo)
2. Procure a variável **`AUTOCMD`**
3. **ALTERE DE:**
   ```
   autopost --stories
   ```
4. **PARA:**
   ```
   multirun --stories --limit 1
   ```
5. Clique **"Save"**

#### **3. Repetir para Outros Serviços**
- Repita os passos 1-2 para **Stories-15h**
- Repita os passos 1-2 para **Stories-21h**

---

## ✅ **VERIFICAÇÃO PÓS-CORREÇÃO**

### **Cada serviço deve ter:**
```
AUTOCMD = multirun --stories --limit 1
```

### **Resultado esperado:**
- ✅ Stories processarão **ambas as contas**
- ✅ **Milton_Albanez**: ID `17841404919106588`
- ✅ **Albanez Assistência Técnica**: ID `17841419226912347`
- ✅ **2 Stories por horário** (1 para cada conta)

---

## 🕐 **CRONOGRAMA CORRIGIDO**

Após as correções, os Stories funcionarão assim:

### **09:00 BRT (12:00 UTC):**
- 📖 Story Milton_Albanez
- 📖 Story Albanez Assistência Técnica

### **15:00 BRT (18:00 UTC):**
- 📖 Story Milton_Albanez  
- 📖 Story Albanez Assistência Técnica

### **21:00 BRT (00:00 UTC):**
- 📖 Story Milton_Albanez
- 📖 Story Albanez Assistência Técnica

**Total:** **6 Stories automáticos por dia** (2 por horário × 3 horários) 🚀

---

## 🧪 **TESTE LOCAL (OPCIONAL)**

Para confirmar que funciona, você pode testar localmente:

```powershell
python src/main.py multirun --stories --limit 1
```

**Resultado esperado:**
- ✅ Carrega 4 contas do accounts.json
- ✅ Processa apenas contas com Stories habilitados
- ✅ Gera Stories para cada conta válida

---

## ⚠️ **IMPORTANTE**

### **NÃO ESQUEÇA:**
- ✅ Atualizar **TODOS os 3 serviços** de Stories
- ✅ Usar exatamente: `multirun --stories --limit 1`
- ✅ Salvar as alterações em cada serviço

### **APÓS AS CORREÇÕES:**
- 🎯 Sistema será **100% automático**
- 🎯 **6 publicações por dia** (3 Feed + 3 Stories)
- 🎯 **Cada conta com credenciais únicas**
- 🎯 **Independente do computador**

---

## 🎉 **RESULTADO FINAL**

**ANTES (PROBLEMA):**
- ❌ Stories processavam apenas 1 conta
- ❌ Credenciais duplicadas
- ❌ Sistema incompleto

**DEPOIS (SOLUÇÃO):**
- ✅ **Stories processam 2 contas**
- ✅ **Credenciais únicas por conta**
- ✅ **Sistema 100% funcional**
- ✅ **Automação completa**

**🚀 PRÓXIMOS STORIES: Hoje mesmo nos horários programados!**