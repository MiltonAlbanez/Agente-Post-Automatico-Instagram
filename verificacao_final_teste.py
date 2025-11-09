#!/usr/bin/env python3
"""
🎯 VERIFICAÇÃO FINAL - TESTE 20:15
Verifica se todas as configurações estão corretas para o teste
"""

import subprocess
import json

def verificar_configuracao_final():
    print("🎯 VERIFICAÇÃO FINAL - SERVIÇO TESTE 20:15")
    print("=" * 60)
    
    try:
        # Obter variáveis do Railway
        result = subprocess.run(['railway', 'variables', '--json'], 
                              capture_output=True, text=True, check=True, shell=True)
        vars_railway = json.loads(result.stdout)
        
        print("✅ Conectado ao Railway com sucesso")
        print(f"📋 Serviço: {vars_railway.get('RAILWAY_SERVICE_NAME', 'N/A')}")
        print(f"🏗️ Projeto: {vars_railway.get('RAILWAY_PROJECT_NAME', 'N/A')}")
        print()
        
        # Verificar variáveis obrigatórias
        obrigatorias = {
            'AUTOCMD': 'autopost',
            'INSTAGRAM_BUSINESS_ACCOUNT_ID': True,
            'INSTAGRAM_ACCESS_TOKEN': True,
            'OPENAI_API_KEY': True,
            'RAPIDAPI_KEY': True,
            'RAPIDAPI_HOST': True,
            'REPLICATE_TOKEN': True
        }
        
        print("🔍 VERIFICAÇÃO DE VARIÁVEIS OBRIGATÓRIAS:")
        print("-" * 50)
        
        todas_ok = True
        for var, esperado in obrigatorias.items():
            valor = vars_railway.get(var, '')
            
            if var == 'AUTOCMD':
                if valor == esperado:
                    print(f"  ✅ {var}: {valor} (correto)")
                else:
                    print(f"  ❌ {var}: {valor} (esperado: {esperado})")
                    todas_ok = False
            else:
                # Verificar se é um valor real (não placeholder)
                is_placeholder = (not valor or 
                                valor.strip() == '' or 
                                valor.startswith('[') or 
                                valor in ['[SEU_TOKEN]', '[SUA_CHAVE]', '[SEU_ID]', '[SUA_URL]', '[SEU_BUCKET]', '[SEU_CHAT_ID]'])
                
                if not is_placeholder:
                    # Mascarar valor sensível
                    if len(valor) > 20:
                        valor_masked = valor[:10] + "..." + valor[-6:]
                    else:
                        valor_masked = valor[:8] + "..."
                    print(f"  ✅ {var}: {valor_masked}")
                else:
                    if valor.startswith('['):
                        print(f"  ⚠️ {var}: {valor} (placeholder - precisa ser substituído)")
                    else:
                        print(f"  ❌ {var}: NÃO CONFIGURADO")
                    todas_ok = False
        
        print()
        print("🔍 VERIFICAÇÃO DE VARIÁVEIS OPCIONAIS:")
        print("-" * 50)
        
        opcionais = ['TELEGRAM_BOT_TOKEN', 'TELEGRAM_CHAT_ID', 'SUPABASE_URL', 'SUPABASE_SERVICE_KEY', 'SUPABASE_BUCKET']
        opcionais_ok = 0
        
        for var in opcionais:
            valor = vars_railway.get(var, '')
            # Verificar se é um valor real (não placeholder)
            is_placeholder = (not valor or 
                            valor.strip() == '' or 
                            valor.startswith('[') or 
                            valor in ['[SEU_TOKEN]', '[SUA_CHAVE]', '[SEU_ID]', '[SUA_URL]', '[SEU_BUCKET]', '[SEU_CHAT_ID]'])
            
            if not is_placeholder:
                if len(valor) > 20:
                    valor_masked = valor[:10] + "..." + valor[-6:]
                else:
                    valor_masked = valor[:8] + "..."
                print(f"  ✅ {var}: {valor_masked}")
                opcionais_ok += 1
            else:
                if valor.startswith('['):
                    print(f"  ⚠️ {var}: {valor} (placeholder - opcional)")
                else:
                    print(f"  ⚠️ {var}: NÃO CONFIGURADO (opcional)")
        
        print()
        print("🎯 RESUMO FINAL:")
        print("=" * 60)
        
        if todas_ok:
            print("🟢 STATUS: CONFIGURAÇÃO COMPLETA E CORRETA!")
            print("✅ Todas as variáveis obrigatórias estão configuradas")
            print(f"ℹ️ Variáveis opcionais: {opcionais_ok}/{len(opcionais)} configuradas")
            print()
            print("🚀 PRÓXIMOS PASSOS:")
            print("1. ✅ Configurar Cron Schedule: 15 23 * * *")
            print("2. ✅ Aguardar execução automática às 23:15")
            print("3. ✅ Ou fazer deploy manual para teste imediato")
            print("4. ✅ Monitorar logs no Railway Dashboard")
            print()
            print("🎉 TUDO PRONTO PARA O TESTE!")
        else:
            print("🟡 STATUS: CONFIGURAÇÃO INCOMPLETA")
            print("❌ Algumas variáveis obrigatórias estão faltando")
            print("📝 Verifique as variáveis marcadas com ❌ acima")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao executar comando Railway: {e}")
    except json.JSONDecodeError as e:
        print(f"❌ Erro ao processar resposta JSON: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    verificar_configuracao_final()