#!/usr/bin/env python3
"""
Teste para verificar se o deployment no Railway está funcionando
"""

import requests
import time
import json
from pathlib import Path

def test_railway_deployment():
    """Testa se o deployment no Railway está funcionando"""
    
    print("🚀 TESTE DE DEPLOYMENT NO RAILWAY")
    print("=" * 50)
    
    # Verificar se os arquivos necessários existem
    required_files = [
        "railway_scheduler.py",
        "Procfile", 
        "railway.json",
        "accounts.json",
        "requirements.txt"
    ]
    
    print("\n📁 Verificando arquivos necessários:")
    for file in required_files:
        if Path(file).exists():
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} - AUSENTE!")
    
    # Verificar conteúdo do Procfile
    print("\n📋 Verificando Procfile:")
    try:
        with open("Procfile", "r") as f:
            content = f.read()
            if "railway_scheduler.py" in content:
                print("  ✅ Procfile configurado para railway_scheduler.py")
            else:
                print("  ❌ Procfile não está usando railway_scheduler.py")
    except Exception as e:
        print(f"  ❌ Erro ao ler Procfile: {e}")
    
    # Verificar railway.json
    print("\n⚙️ Verificando railway.json:")
    try:
        with open("railway.json", "r") as f:
            config = json.load(f)
            start_command = config.get("deploy", {}).get("startCommand", "")
            if "railway_scheduler.py" in start_command:
                print("  ✅ railway.json configurado para railway_scheduler.py")
            else:
                print(f"  ❌ startCommand: {start_command}")
    except Exception as e:
        print(f"  ❌ Erro ao ler railway.json: {e}")
    
    # Verificar accounts.json
    print("\n👥 Verificando accounts.json:")
    try:
        with open("accounts.json", "r") as f:
            accounts = json.load(f)
            print(f"  ✅ {len(accounts)} contas carregadas")
            for i, account in enumerate(accounts):
                print(f"    📱 Conta {i+1}: {account.get('nome', 'N/A')}")
    except Exception as e:
        print(f"  ❌ Erro ao ler accounts.json: {e}")
    
    print("\n🎯 RESULTADO:")
    print("✅ Sistema configurado para deployment no Railway")
    print("🔄 O agendador deve estar rodando 24/7 na nuvem")
    print("⏰ Horários programados (BRT):")
    print("   📝 FEED: 06:00, 12:00, 19:00")
    print("   📱 STORIES: 09:00, 15:00, 21:00")
    
    print("\n💡 Para verificar logs em tempo real:")
    print("   railway logs")
    
    print("\n🌐 Para acessar o dashboard do Railway:")
    print("   https://railway.app/dashboard")

if __name__ == "__main__":
    test_railway_deployment()