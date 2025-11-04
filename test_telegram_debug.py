#!/usr/bin/env python3
"""
🔍 TESTE DE DEBUG TELEGRAM
Investigação completa do problema de notificações não recebidas
"""

import os
import sys
import requests
import json
from datetime import datetime

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from config import load_config
from services.telegram_client import TelegramClient

def test_telegram_api_direct():
    """Teste direto da API do Telegram"""
    print("🔍 TESTE DIRETO DA API TELEGRAM")
    print("=" * 50)
    
    cfg = load_config()
    bot_token = cfg.get("TELEGRAM_BOT_TOKEN")
    chat_id = cfg.get("TELEGRAM_CHAT_ID")
    
    print(f"Bot Token: {bot_token[:20]}..." if bot_token else "❌ Bot Token não encontrado")
    print(f"Chat ID: {chat_id}")
    
    if not bot_token or not chat_id:
        print("❌ ERRO: Credenciais do Telegram não configuradas")
        return False
    
    # Teste 1: getMe (verificar se o bot está ativo)
    print("\n📡 Teste 1: Verificando status do bot...")
    try:
        url = f"https://api.telegram.org/bot{bot_token}/getMe"
        response = requests.get(url, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            bot_info = response.json()
            print(f"✅ Bot ativo: {bot_info['result']['first_name']} (@{bot_info['result']['username']})")
        else:
            print(f"❌ Erro na API: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return False
    
    # Teste 2: Enviar mensagem de teste
    print("\n📤 Teste 2: Enviando mensagem de teste...")
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": f"🧪 TESTE DEBUG - {datetime.now().strftime('%H:%M:%S')}\n\nEste é um teste de conectividade do sistema de notificações.",
            "parse_mode": "HTML"
        }
        
        response = requests.post(url, data=payload, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Mensagem enviada com sucesso!")
            print(f"Message ID: {result['result']['message_id']}")
            return True
        else:
            print(f"❌ Erro ao enviar: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro de envio: {e}")
        return False

def test_telegram_client_class():
    """Teste da classe TelegramClient"""
    print("\n🔧 TESTE DA CLASSE TELEGRAMCLIENT")
    print("=" * 50)
    
    cfg = load_config()
    bot_token = cfg.get("TELEGRAM_BOT_TOKEN")
    chat_id = cfg.get("TELEGRAM_CHAT_ID")
    
    if not bot_token or not chat_id:
        print("❌ ERRO: Credenciais não configuradas")
        return False
    
    try:
        # Instanciar cliente
        client = TelegramClient(bot_token, chat_id)
        print(f"✅ Cliente instanciado")
        print(f"Bot Token: {client.bot_token[:20]}...")
        print(f"Chat ID: {client.chat_id}")
        
        # Enviar mensagem de teste
        print("\n📤 Enviando mensagem via classe...")
        success = client.send_message(f"🔧 TESTE CLASSE - {datetime.now().strftime('%H:%M:%S')}\n\nTeste da classe TelegramClient")
        
        if success:
            print("✅ Mensagem enviada com sucesso via classe!")
            return True
        else:
            print("❌ Falha ao enviar via classe")
            return False
            
    except Exception as e:
        print(f"❌ Erro na classe: {e}")
        return False

def test_chat_permissions():
    """Teste de permissões do chat"""
    print("\n🔐 TESTE DE PERMISSÕES DO CHAT")
    print("=" * 50)
    
    cfg = load_config()
    bot_token = cfg.get("TELEGRAM_BOT_TOKEN")
    chat_id = cfg.get("TELEGRAM_CHAT_ID")
    
    try:
        # Verificar informações do chat
        url = f"https://api.telegram.org/bot{bot_token}/getChat"
        params = {"chat_id": chat_id}
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            chat_info = response.json()['result']
            print(f"✅ Chat encontrado: {chat_info.get('title', 'Chat Privado')}")
            print(f"Tipo: {chat_info.get('type')}")
            
            # Verificar se o bot é membro (para grupos)
            if chat_info.get('type') in ['group', 'supergroup']:
                member_url = f"https://api.telegram.org/bot{bot_token}/getChatMember"
                member_params = {"chat_id": chat_id, "user_id": bot_token.split(':')[0]}
                member_response = requests.get(member_url, params=member_params, timeout=10)
                
                if member_response.status_code == 200:
                    member_info = member_response.json()['result']
                    print(f"Status do bot no grupo: {member_info.get('status')}")
                else:
                    print(f"❌ Erro ao verificar membership: {member_response.text}")
            
            return True
        else:
            print(f"❌ Erro ao acessar chat: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro de permissões: {e}")
        return False

def main():
    print("🔍 DIAGNÓSTICO COMPLETO DO TELEGRAM")
    print("=" * 60)
    print(f"Timestamp: {datetime.now()}")
    print()
    
    # Executar todos os testes
    tests = [
        ("API Direta", test_telegram_api_direct),
        ("Classe TelegramClient", test_telegram_client_class),
        ("Permissões do Chat", test_chat_permissions)
    ]
    
    results = {}
    for test_name, test_func in tests:
        print(f"\n🧪 EXECUTANDO: {test_name}")
        print("-" * 40)
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ ERRO CRÍTICO em {test_name}: {e}")
            results[test_name] = False
    
    # Resumo final
    print("\n📊 RESUMO DOS TESTES")
    print("=" * 50)
    
    all_passed = True
    for test_name, result in results.items():
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print("\n🎯 DIAGNÓSTICO FINAL")
    print("=" * 50)
    
    if all_passed:
        print("✅ TODOS OS TESTES PASSARAM!")
        print("🔍 O problema pode estar em:")
        print("   - Timing das mensagens")
        print("   - Configuração do ambiente Railway")
        print("   - Filtros do Telegram")
    else:
        print("❌ PROBLEMAS IDENTIFICADOS!")
        print("🔧 Verifique:")
        print("   - Credenciais do bot")
        print("   - Permissões do chat")
        print("   - Conectividade de rede")

if __name__ == "__main__":
    main()