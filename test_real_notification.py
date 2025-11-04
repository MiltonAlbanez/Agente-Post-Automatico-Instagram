#!/usr/bin/env python3
"""
🚀 TESTE DE EXECUÇÃO REAL COM NOTIFICAÇÕES
Simula uma execução completa para verificar notificações
"""

import sys
from pathlib import Path
import time
from datetime import datetime

# Garantir que o diretório raiz (que contém 'src') está no PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

from src.config import load_config
from src.services.telegram_client import TelegramClient

def test_real_execution_simulation():
    """Simula uma execução real completa"""
    print("🚀 SIMULAÇÃO DE EXECUÇÃO REAL")
    print("=" * 50)
    
    cfg = load_config()
    telegram_bot_token = cfg.get("TELEGRAM_BOT_TOKEN")
    telegram_chat_id = cfg.get("TELEGRAM_CHAT_ID")
    
    if not telegram_bot_token or not telegram_chat_id:
        print("❌ ERRO: Credenciais não configuradas")
        return False
    
    # Simular início da execução
    print("🔄 Iniciando simulação de execução...")
    
    try:
        # 1. Notificação de início
        print("\n📤 1. Enviando notificação de início...")
        start_result = TelegramClient(telegram_bot_token, telegram_chat_id).send_message(
            f"🚀 EXECUÇÃO INICIADA - {datetime.now().strftime('%H:%M:%S')}\n\n"
            f"Sistema de automação iniciado.\n"
            f"Processando conteúdo..."
        )
        print(f"   Resultado: {'✅ Sucesso' if start_result else '❌ Falha'}")
        
        # Simular processamento
        print("\n⏳ 2. Simulando processamento (5 segundos)...")
        time.sleep(5)
        
        # 2. Notificação de progresso
        print("\n📤 3. Enviando notificação de progresso...")
        progress_result = TelegramClient(telegram_bot_token, telegram_chat_id).send_message(
            f"⚙️ PROCESSAMENTO - {datetime.now().strftime('%H:%M:%S')}\n\n"
            f"✅ Conteúdo gerado\n"
            f"✅ Imagem criada\n"
            f"🔄 Publicando no Instagram..."
        )
        print(f"   Resultado: {'✅ Sucesso' if progress_result else '❌ Falha'}")
        
        # Simular publicação
        print("\n⏳ 4. Simulando publicação (3 segundos)...")
        time.sleep(3)
        
        # 3. Notificação de sucesso
        print("\n📤 5. Enviando notificação de sucesso...")
        success_result = TelegramClient(telegram_bot_token, telegram_chat_id).send_message(
            f"✅ PUBLICAÇÃO CONCLUÍDA - {datetime.now().strftime('%H:%M:%S')}\n\n"
            f"📱 Feed: Publicado com sucesso\n"
            f"📊 Status: PUBLISHED\n"
            f"🎯 Sistema funcionando perfeitamente!"
        )
        print(f"   Resultado: {'✅ Sucesso' if success_result else '❌ Falha'}")
        
        # Resumo
        all_results = [start_result, progress_result, success_result]
        success_count = sum(1 for r in all_results if r)
        
        print(f"\n📊 RESUMO DA SIMULAÇÃO")
        print("=" * 30)
        print(f"Notificações enviadas: {success_count}/3")
        
        if success_count == 3:
            print("✅ TODAS AS NOTIFICAÇÕES FUNCIONARAM!")
            print("🔍 Se não estão chegando no Railway, verifique:")
            print("   - Variáveis de ambiente no Railway")
            print("   - Logs do Railway")
            print("   - Conectividade de rede do Railway")
            return True
        else:
            print("❌ ALGUMAS NOTIFICAÇÕES FALHARAM!")
            return False
            
    except Exception as e:
        print(f"❌ ERRO durante simulação: {e}")
        return False

def test_railway_environment_variables():
    """Testa se as variáveis de ambiente estão corretas"""
    print("\n🔧 VERIFICAÇÃO DE VARIÁVEIS DE AMBIENTE")
    print("=" * 50)
    
    cfg = load_config()
    
    # Verificar variáveis críticas
    critical_vars = {
        "TELEGRAM_BOT_TOKEN": cfg.get("TELEGRAM_BOT_TOKEN"),
        "TELEGRAM_CHAT_ID": cfg.get("TELEGRAM_CHAT_ID"),
        "INSTAGRAM_BUSINESS_ACCOUNT_ID": cfg.get("INSTAGRAM_BUSINESS_ACCOUNT_ID"),
        "INSTAGRAM_ACCESS_TOKEN": cfg.get("INSTAGRAM_ACCESS_TOKEN"),
        "OPENAI_API_KEY": cfg.get("OPENAI_API_KEY"),
        "REPLICATE_TOKEN": cfg.get("REPLICATE_TOKEN")
    }
    
    print("Verificando variáveis críticas:")
    all_configured = True
    
    for var_name, var_value in critical_vars.items():
        if var_value and var_value.strip():
            # Mostrar apenas parte da variável por segurança
            if len(var_value) > 20:
                display_value = f"{var_value[:10]}...{var_value[-5:]}"
            else:
                display_value = f"{var_value[:5]}..."
            print(f"   ✅ {var_name}: {display_value}")
        else:
            print(f"   ❌ {var_name}: NÃO CONFIGURADA")
            all_configured = False
    
    if all_configured:
        print("\n✅ TODAS AS VARIÁVEIS ESTÃO CONFIGURADAS!")
        return True
    else:
        print("\n❌ ALGUMAS VARIÁVEIS NÃO ESTÃO CONFIGURADAS!")
        return False

def main():
    print("🔍 TESTE DE EXECUÇÃO REAL COM NOTIFICAÇÕES")
    print("=" * 60)
    print(f"Timestamp: {datetime.now()}")
    print()
    
    # Executar testes
    env_test = test_railway_environment_variables()
    execution_test = test_real_execution_simulation()
    
    print("\n🎯 CONCLUSÃO FINAL")
    print("=" * 50)
    
    if env_test and execution_test:
        print("✅ SISTEMA FUNCIONANDO PERFEITAMENTE!")
        print("\n📋 PRÓXIMOS PASSOS:")
        print("1. 🚀 Fazer deploy das correções no Railway")
        print("2. 🔍 Monitorar logs do Railway durante próxima execução")
        print("3. 📱 Verificar se notificações chegam no horário agendado")
        print("4. 🛠️ Se ainda não funcionar, verificar conectividade Railway")
    else:
        print("❌ PROBLEMAS IDENTIFICADOS!")
        if not env_test:
            print("🔧 Configurar variáveis de ambiente")
        if not execution_test:
            print("🔧 Verificar conectividade do Telegram")

if __name__ == "__main__":
    main()