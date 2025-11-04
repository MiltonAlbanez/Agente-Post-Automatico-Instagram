#!/usr/bin/env python3
"""
Teste de Integração Completa do Telegram
Verifica se ambos os sistemas (original e avançado) estão usando o mesmo bot
"""

import sys
import os
from datetime import datetime
from pathlib import Path

# Adicionar o diretório src ao path
sys.path.append(str(Path(__file__).parent / "src"))

from services.telegram_client import TelegramClient
from services.notification_manager import NotificationManager
from config import load_config

def test_original_telegram_system():
    """Testa o sistema original de Telegram"""
    print("🤖 === TESTE DO SISTEMA ORIGINAL (TelegramClient) ===")
    
    try:
        # Carregar configurações
        cfg = load_config()
        bot_token = cfg["TELEGRAM_BOT_TOKEN"]
        chat_id = cfg["TELEGRAM_CHAT_ID"]
        
        print(f"📱 Bot Token: {bot_token[:10]}...")
        print(f"💬 Chat ID: {chat_id}")
        
        # Criar cliente
        telegram_client = TelegramClient(bot_token, chat_id)
        
        # Enviar mensagem de teste
        test_message = f"""
🧪 **TESTE SISTEMA ORIGINAL**

✅ TelegramClient funcionando
🕐 Horário: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
🎯 Tipo: Sistema de Publicação

Este é um teste do sistema original de notificações.
        """
        
        success = telegram_client.send_message(test_message)
        
        if success:
            print("✅ Sistema original funcionando!")
            return True
        else:
            print("❌ Falha no sistema original")
            return False
            
    except Exception as e:
        print(f"❌ Erro no sistema original: {e}")
        return False

def test_advanced_telegram_system():
    """Testa o sistema avançado de Telegram"""
    print("\n🔔 === TESTE DO SISTEMA AVANÇADO (NotificationManager) ===")
    
    try:
        # Criar notification manager
        notification_manager = NotificationManager()
        
        # Enviar mensagem de teste
        test_message = f"""
🧪 **TESTE SISTEMA AVANÇADO**

✅ NotificationManager funcionando
🕐 Horário: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
🎯 Tipo: Sistema de Monitoramento

Este é um teste do sistema avançado de notificações.
        """
        
        success = notification_manager.send_telegram_message(
            test_message, 
            "Albanez Assistência Técnica"
        )
        
        if success:
            print("✅ Sistema avançado funcionando!")
            return True
        else:
            print("❌ Falha no sistema avançado")
            return False
            
    except Exception as e:
        print(f"❌ Erro no sistema avançado: {e}")
        return False

def test_credentials_consistency():
    """Verifica se ambos os sistemas usam as mesmas credenciais"""
    print("\n🔍 === VERIFICAÇÃO DE CONSISTÊNCIA ===")
    
    try:
        # Sistema original
        cfg = load_config()
        original_token = cfg["TELEGRAM_BOT_TOKEN"]
        original_chat = cfg["TELEGRAM_CHAT_ID"]
        
        # Sistema avançado
        notification_manager = NotificationManager()
        advanced_token = notification_manager.config["telegram"]["bot_token"]
        advanced_chat = notification_manager.config["telegram"]["chat_id"]
        
        print(f"🤖 Token Original: {original_token[:10]}...")
        print(f"🔔 Token Avançado: {advanced_token[:10]}...")
        print(f"💬 Chat Original: {original_chat}")
        print(f"📱 Chat Avançado: {advanced_chat}")
        
        # Verificar se são iguais
        tokens_match = original_token == advanced_token
        chats_match = original_chat == advanced_chat
        
        if tokens_match and chats_match:
            print("✅ Credenciais consistentes entre sistemas!")
            return True
        else:
            print("❌ Credenciais inconsistentes!")
            if not tokens_match:
                print("  - Tokens diferentes")
            if not chats_match:
                print("  - Chat IDs diferentes")
            return False
            
    except Exception as e:
        print(f"❌ Erro na verificação: {e}")
        return False

def test_unified_notification():
    """Testa notificação unificada simulando um cenário real"""
    print("\n🎯 === TESTE DE NOTIFICAÇÃO UNIFICADA ===")
    
    try:
        # Simular publicação bem-sucedida (sistema original)
        cfg = load_config()
        telegram_client = TelegramClient(cfg["TELEGRAM_BOT_TOKEN"], cfg["TELEGRAM_CHAT_ID"])
        
        publication_message = """
✅ **PUBLICAÇÃO REALIZADA**

📱 Feed: Post publicado com sucesso
📖 Stories: Stories publicado
🕐 Horário: {timestamp}
🎯 Conta: Albanez Assistência Técnica
        """.format(timestamp=datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
        
        pub_success = telegram_client.send_message(publication_message)
        
        # Simular alerta de performance (sistema avançado)
        notification_manager = NotificationManager()
        
        performance_message = """
📊 **MONITORAMENTO AUTOMÁTICO**

📈 Sistema de alertas ativo
🔍 Monitorando engagement
⚡ Backup automático funcionando
🎯 Conta: Albanez Assistência Técnica
        """
        
        perf_success = notification_manager.send_telegram_message(
            performance_message,
            "Albanez Assistência Técnica"
        )
        
        if pub_success and perf_success:
            print("✅ Notificação unificada funcionando!")
            print("📱 Ambos os sistemas enviaram mensagens para o mesmo chat")
            return True
        else:
            print("❌ Falha na notificação unificada")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste unificado: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("🚀 === TESTE DE INTEGRAÇÃO TELEGRAM COMPLETO ===")
    print(f"🕐 Iniciado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 60)
    
    # Executar testes
    results = []
    
    results.append(("Sistema Original", test_original_telegram_system()))
    results.append(("Sistema Avançado", test_advanced_telegram_system()))
    results.append(("Consistência", test_credentials_consistency()))
    results.append(("Notificação Unificada", test_unified_notification()))
    
    # Resumo dos resultados
    print("\n" + "=" * 60)
    print("📊 === RESUMO DOS TESTES ===")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name:<20} {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Resultado: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Sistema de Telegram unificado funcionando perfeitamente!")
        print("📱 Ambos os sistemas usam o mesmo bot e chat")
    else:
        print("⚠️ Alguns testes falharam")
        print("🔧 Verifique as configurações e tente novamente")
    
    print("\n" + "=" * 60)
    print("✅ Teste de integração finalizado!")

if __name__ == "__main__":
    main()