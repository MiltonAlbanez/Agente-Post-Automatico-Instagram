#!/usr/bin/env python3
"""
Teste de Carregamento das Variáveis de Ambiente do Telegram
"""

import os
import sys
from pathlib import Path

# Adicionar src ao path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

def test_dotenv_loading():
    """Testar carregamento direto do .env"""
    print("🧪 Testando carregamento direto do .env...")
    
    try:
        from dotenv import load_dotenv
        
        env_path = project_root / ".env"
        if env_path.exists():
            load_dotenv(env_path)
            
            bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
            chat_id = os.getenv("TELEGRAM_CHAT_ID")
            
            print(f"✅ Bot Token: {bot_token[:20] if bot_token else 'None'}...")
            print(f"✅ Chat ID: {chat_id}")
            
            return bot_token and chat_id
        else:
            print("❌ Arquivo .env não encontrado")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao carregar .env: {str(e)}")
        return False

def test_telegram_client():
    """Testar TelegramClient com as variáveis carregadas"""
    print("\n📱 Testando TelegramClient...")
    
    try:
        # Carregar .env primeiro
        from dotenv import load_dotenv
        env_path = project_root / ".env"
        if env_path.exists():
            load_dotenv(env_path)
        
        # Importar e testar TelegramClient
        from services.telegram_client import TelegramClient
        
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        
        if not bot_token or not chat_id:
            print("❌ Credenciais não encontradas")
            return False
            
        client = TelegramClient(bot_token, chat_id)
        
        # Enviar mensagem de teste
        success = client.send_message("🧪 Teste de correção do ambiente Telegram - Sucesso!")
        
        if success:
            print("✅ Mensagem de teste enviada com sucesso!")
            return True
        else:
            print("❌ Falha ao enviar mensagem de teste")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar TelegramClient: {str(e)}")
        return False

def main():
    """Função principal"""
    print("🔧 TESTE DE CORREÇÃO DO TELEGRAM")
    print("=" * 40)
    
    # Teste 1: Carregamento do .env
    env_success = test_dotenv_loading()
    
    # Teste 2: TelegramClient
    client_success = test_telegram_client()
    
    # Resultado final
    print(f"\n📊 RESULTADO DOS TESTES:")
    print(f"Carregamento .env: {'✅ SUCESSO' if env_success else '❌ FALHA'}")
    print(f"TelegramClient: {'✅ SUCESSO' if client_success else '❌ FALHA'}")
    
    if env_success and client_success:
        print("\n🎉 CORREÇÃO DO TELEGRAM CONFIRMADA!")
        print("O sistema agora pode enviar notificações via Telegram.")
    else:
        print("\n⚠️ PROBLEMAS DETECTADOS")
        print("Verifique os logs acima para mais detalhes.")
        
    return env_success and client_success

if __name__ == "__main__":
    main()