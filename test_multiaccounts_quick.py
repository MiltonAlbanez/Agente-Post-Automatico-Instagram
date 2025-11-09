#!/usr/bin/env python3
"""
Teste rápido para verificar se o sistema processa múltiplas contas
"""

import json
import sys
import os
from datetime import datetime

# Adicionar o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_accounts_loading():
    """Testa se o sistema carrega múltiplas contas corretamente"""
    print("🚀 TESTE RÁPIDO - CARREGAMENTO DE MÚLTIPLAS CONTAS")
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
        return False
    
    # Verificar estrutura das contas
    print("\n📋 VERIFICANDO ESTRUTURA DAS CONTAS:")
    print("-" * 40)
    
    for i, account in enumerate(accounts, 1):
        nome = account.get("nome", "Sem nome")
        instagram_id = account.get("instagram_id", "Não encontrado")
        has_token = bool(account.get("instagram_access_token"))
        
        print(f"{i}. {nome}")
        print(f"   Instagram ID: {instagram_id}")
        print(f"   Token presente: {'✅' if has_token else '❌'}")
        print()
    
    # Simular processamento como o scheduler faria
    print("🔄 SIMULANDO PROCESSAMENTO DO SCHEDULER:")
    print("-" * 40)
    
    for account in accounts:
        nome = account.get("nome", "Conta sem nome")
        instagram_id = account.get("instagram_id")
        access_token = account.get("instagram_access_token")
        
        print(f"🔄 Processando conta: {nome}")
        
        if not instagram_id:
            print(f"   ❌ Instagram ID não encontrado")
            continue
            
        if not access_token:
            print(f"   ❌ Access token não encontrado")
            continue
            
        print(f"   ✅ Credenciais OK - ID: {instagram_id}")
        print(f"   ✅ Token presente (primeiros 20 chars): {access_token[:20]}...")
        print()
    
    print("📊 RESUMO:")
    print("-" * 40)
    total_accounts = len(accounts)
    valid_accounts = sum(1 for acc in accounts if acc.get("instagram_id") and acc.get("instagram_access_token"))
    
    print(f"Total de contas: {total_accounts}")
    print(f"Contas válidas: {valid_accounts}")
    
    if valid_accounts == total_accounts:
        print("🎉 Todas as contas estão configuradas corretamente!")
        return True
    else:
        print(f"⚠️ {total_accounts - valid_accounts} conta(s) com problemas de configuração")
        return False

if __name__ == "__main__":
    success = test_accounts_loading()
    if success:
        print("\n✅ Sistema pronto para processar múltiplas contas!")
    else:
        print("\n❌ Problemas encontrados na configuração das contas")