#!/usr/bin/env python3
"""
Script para testar as credenciais de todas as contas no accounts.json
"""

import requests
import json
import sys
import os
from datetime import datetime

def test_account_credentials(account_name, account_data):
    """Testa as credenciais de uma conta específica"""
    print(f"\n🔄 == TESTANDO CONTA: {account_name} ==")
    print("-" * 50)
    
    # Verificar se as credenciais estão presentes
    instagram_id = account_data.get("instagram_id")
    access_token = account_data.get("instagram_access_token")
    
    if not instagram_id:
        print(f"❌ ERRO: instagram_id não encontrado para {account_name}")
        return False
        
    if not access_token:
        print(f"❌ ERRO: instagram_access_token não encontrado para {account_name}")
        return False
    
    print(f"📱 Instagram ID: {instagram_id}")
    print(f"🔑 Token (primeiros 20 chars): {access_token[:20]}...")
    
    # Teste: Verificar informações básicas da conta
    print("📋 Testando informações básicas da conta...")
    try:
        url = f"https://graph.facebook.com/v18.0/{instagram_id}"
        params = {
            "fields": "id,username",
            "access_token": access_token
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            username = data.get("username", "N/A")
            print(f"✅ Sucesso! Conta: @{username}")
            print(f"   ID: {data.get('id')}")
            return True
        else:
            print(f"❌ Erro HTTP {response.status_code}")
            print(f"   Resposta: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ Erro na requisição: {str(e)}")
        return False

def main():
    """Função principal"""
    print("🚀 TESTE DE CREDENCIAIS - TODAS AS CONTAS")
    print("=" * 60)
    print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Carregar accounts.json
    try:
        with open('accounts.json', 'r', encoding='utf-8') as f:
            accounts = json.load(f)
        print(f"✅ Arquivo accounts.json carregado com {len(accounts)} contas")
    except Exception as e:
        print(f"❌ Erro ao carregar accounts.json: {str(e)}")
        return
    
    # Testar cada conta
    results = {}
    for account_data in accounts:
        account_name = account_data.get("nome", "Conta sem nome")
        success = test_account_credentials(account_name, account_data)
        results[account_name] = success
    
    # Resumo final
    print("\n📊 RESUMO DOS TESTES")
    print("=" * 60)
    for account_name, success in results.items():
        status = "✅ OK" if success else "❌ FALHOU"
        print(f"{account_name}: {status}")
    
    # Verificar se todas passaram
    all_passed = all(results.values())
    if all_passed:
        print("\n🎉 Todas as contas passaram nos testes!")
    else:
        failed_accounts = [name for name, success in results.items() if not success]
        print(f"\n🚨 CONTAS COM PROBLEMAS: {', '.join(failed_accounts)}")

if __name__ == "__main__":
    main()