#!/usr/bin/env python3
"""
🔍 TESTE DE NOTIFICAÇÕES NO PIPELINE
Simula o contexto do pipeline para testar notificações
"""

import sys
from pathlib import Path
from datetime import datetime

# Garantir que o diretório raiz (que contém 'src') está no PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

from src.config import load_config
from src.services.telegram_client import TelegramClient

def test_telegram_in_pipeline_context():
    """Testa notificações no contexto do pipeline"""
    print("🔍 TESTE DE NOTIFICAÇÕES NO PIPELINE")
    print("=" * 50)
    
    cfg = load_config()
    telegram_bot_token = cfg.get("TELEGRAM_BOT_TOKEN")
    telegram_chat_id = cfg.get("TELEGRAM_CHAT_ID")
    
    if not telegram_bot_token or not telegram_chat_id:
        print("❌ ERRO: Credenciais do Telegram não configuradas")
        return False
    
    print(f"Bot Token: {telegram_bot_token[:20]}...")
    print(f"Chat ID: {telegram_chat_id}")
    
    # Simular diferentes cenários de notificação
    test_scenarios = [
        {
            "name": "Publicação com sucesso (sem Stories)",
            "message": "Instagram content is shared",
            "expected": True
        },
        {
            "name": "Publicação com sucesso (com Stories)",
            "message": "✅ Conteúdo publicado com sucesso!\n📱 Feed: 12345\n📖 Stories: 67890",
            "expected": True
        },
        {
            "name": "Falha na publicação",
            "message": "Instagram content publish status: ERROR",
            "expected": True
        },
        {
            "name": "Erro geral",
            "message": "Instagram publish error: Teste de erro",
            "expected": True
        },
        {
            "name": "Stories falhou",
            "message": "⚠️ Feed publicado (12345), mas Stories falhou: Erro de teste",
            "expected": True
        }
    ]
    
    results = {}
    
    for scenario in test_scenarios:
        print(f"\n📤 Testando: {scenario['name']}")
        print("-" * 40)
        
        try:
            # Simular o contexto exato do pipeline
            telegram_sent = TelegramClient(telegram_bot_token, telegram_chat_id).send_message(
                f"🧪 TESTE PIPELINE - {datetime.now().strftime('%H:%M:%S')}\n\n{scenario['message']}"
            )
            
            if telegram_sent:
                print(f"✅ Sucesso: {scenario['name']}")
                results[scenario['name']] = True
            else:
                print(f"❌ Falha: {scenario['name']}")
                results[scenario['name']] = False
                
        except Exception as e:
            print(f"❌ ERRO em {scenario['name']}: {e}")
            results[scenario['name']] = False
    
    # Resumo
    print("\n📊 RESUMO DOS TESTES")
    print("=" * 50)
    
    success_count = sum(1 for result in results.values() if result)
    total_count = len(results)
    
    for scenario_name, result in results.items():
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{scenario_name}: {status}")
    
    print(f"\n🎯 RESULTADO FINAL: {success_count}/{total_count} testes passaram")
    
    if success_count == total_count:
        print("✅ TODOS OS CENÁRIOS DE NOTIFICAÇÃO FUNCIONAM!")
        return True
    else:
        print("❌ ALGUNS CENÁRIOS FALHARAM!")
        return False

def test_telegram_with_exception_handling():
    """Testa o comportamento com tratamento de exceções"""
    print("\n🛡️ TESTE DE TRATAMENTO DE EXCEÇÕES")
    print("=" * 50)
    
    cfg = load_config()
    telegram_bot_token = cfg.get("TELEGRAM_BOT_TOKEN")
    telegram_chat_id = cfg.get("TELEGRAM_CHAT_ID")
    
    # Simular o bloco try/except do pipeline
    try:
        telegram_sent = TelegramClient(telegram_bot_token, telegram_chat_id).send_message(
            f"🛡️ TESTE EXCEÇÕES - {datetime.now().strftime('%H:%M:%S')}\n\nTestando tratamento de exceções no pipeline"
        )
        
        if telegram_sent:
            print("✅ Notificação enviada com sucesso no contexto try/except")
            return True
        else:
            print("❌ Falha ao enviar notificação no contexto try/except")
            return False
            
    except Exception as telegram_err:
        print(f"⚠️ ERRO ao enviar notificação Telegram: {telegram_err}")
        print("🔍 Este é o tipo de erro que estava sendo silenciado!")
        return False

def main():
    print("🔍 DIAGNÓSTICO DE NOTIFICAÇÕES NO PIPELINE")
    print("=" * 60)
    print(f"Timestamp: {datetime.now()}")
    print()
    
    # Executar testes
    test1_result = test_telegram_in_pipeline_context()
    test2_result = test_telegram_with_exception_handling()
    
    print("\n🎯 CONCLUSÃO FINAL")
    print("=" * 50)
    
    if test1_result and test2_result:
        print("✅ NOTIFICAÇÕES FUNCIONAM PERFEITAMENTE!")
        print("🔍 Se não estão chegando, o problema pode ser:")
        print("   - Configuração do ambiente Railway")
        print("   - Timing das execuções")
        print("   - Logs não sendo capturados")
    else:
        print("❌ PROBLEMAS IDENTIFICADOS NAS NOTIFICAÇÕES!")
        print("🔧 Verifique os logs de erro acima")

if __name__ == "__main__":
    main()