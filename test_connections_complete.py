#!/usr/bin/env python3
"""
Teste completo de conexões para verificação do sistema antes da publicação automática
"""

import sys
import os
from datetime import datetime
import json
import requests

# Adicionar o diretório raiz ao path
sys.path.append('.')

def test_instagram_connection():
    """Testa conexão com Instagram API"""
    print("🔍 Testando conexão com Instagram API...")
    try:
        from src.services.instagram_client import InstagramClient
        from src.config import load_config
        
        config = load_config()
        
        # Obter credenciais do Instagram
        business_account_id = config.get('INSTAGRAM_BUSINESS_ACCOUNT_ID')
        access_token = config.get('INSTAGRAM_ACCESS_TOKEN')
        
        if not business_account_id or not access_token:
            print("❌ Instagram API: Credenciais não encontradas")
            return False, "Credenciais não configuradas"
        
        client = InstagramClient(business_account_id, access_token)
        
        # Teste básico fazendo uma requisição simples
        url = f"{client.BASE}/{business_account_id}"
        params = {"fields": "name,username", "access_token": access_token}
        resp = requests.get(url, params=params, timeout=10)
        
        if resp.ok:
            data = resp.json()
            username = data.get('username', 'N/A')
            print(f"✅ Instagram API: Conectado como @{username}")
            return True, f"Conta: @{username}"
        else:
            print(f"❌ Instagram API: HTTP {resp.status_code}")
            return False, f"HTTP {resp.status_code}"
            
    except Exception as e:
        print(f"❌ Instagram API: Erro - {e}")
        return False, str(e)

def test_rapidapi_connection():
    """Testa conexão com RapidAPI"""
    print("🔍 Testando conexão com RapidAPI...")
    try:
        from src.services.rapidapi_client import RapidAPIClient
        from src.config import load_config
        
        config = load_config()
        
        # Obter credenciais do RapidAPI
        api_key = config.get('RAPIDAPI_KEY')
        host = config.get('RAPIDAPI_HOST')
        
        if not api_key or not host:
            print("❌ RapidAPI: Credenciais não encontradas")
            return False, "Credenciais não configuradas"
        
        key_preview = api_key[:10] + '...'
        print(f"   Host: {host}")
        print(f"   Key: {key_preview}")
        
        client = RapidAPIClient(api_key, host)
        
        # Teste com hashtag simples
        result = client.get_top_by_hashtag('motivation')
        if result and isinstance(result, dict) and len(result) > 0:
            print(f"✅ RapidAPI: Funcionando - resposta recebida")
            return True, f"Host: {host}, Resposta OK"
        else:
            print("⚠️ RapidAPI: Conectado mas sem resultados")
            return True, f"Host: {host}, Sem resultados"
            
    except Exception as e:
        print(f"❌ RapidAPI: Erro - {e}")
        return False, str(e)

def test_database_connection():
    """Testa conexão com banco de dados"""
    print("🔍 Testando conexão com banco de dados...")
    try:
        from src.services.db import Database
        from src.config import load_config
        
        config = load_config()
        
        # Obter DSN do banco
        dsn = config.get('DATABASE_URL')
        if not dsn:
            print("❌ Banco de dados: DSN não encontrado")
            return False, "DSN não configurado"
        
        db = Database(dsn)
        
        # Teste básico de conexão fazendo uma query simples
        with db.conn.cursor() as cur:
            cur.execute("SELECT 1")
            result = cur.fetchone()
            
        if result:
            print("✅ Banco de dados: Conectado")
            return True, "Conexão estabelecida"
        else:
            print("❌ Banco de dados: Falha na query de teste")
            return False, "Falha na query de teste"
        
    except Exception as e:
        print(f"❌ Banco de dados: Erro - {e}")
        return False, str(e)

def main():
    """Executa todos os testes de conexão"""
    print("🚀 TESTE COMPLETO DE CONEXÕES")
    print("=" * 50)
    print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    results = {}
    
    # Teste Instagram API
    instagram_ok, instagram_msg = test_instagram_connection()
    results['instagram'] = {'status': instagram_ok, 'message': instagram_msg}
    print()
    
    # Teste RapidAPI
    rapidapi_ok, rapidapi_msg = test_rapidapi_connection()
    results['rapidapi'] = {'status': rapidapi_ok, 'message': rapidapi_msg}
    print()
    
    # Teste Database
    db_ok, db_msg = test_database_connection()
    results['database'] = {'status': db_ok, 'message': db_msg}
    print()
    
    # Resumo
    print("📊 RESUMO DOS TESTES DE CONEXÃO")
    print("=" * 50)
    
    all_ok = True
    for service, result in results.items():
        status_icon = "✅" if result['status'] else "❌"
        print(f"{status_icon} {service.upper()}: {result['message']}")
        if not result['status']:
            all_ok = False
    
    print()
    if all_ok:
        print("🎉 TODOS OS SISTEMAS CONECTADOS - PRONTO PARA PUBLICAÇÃO!")
    else:
        print("⚠️ ALGUNS SISTEMAS COM PROBLEMAS - VERIFICAR ANTES DA PUBLICAÇÃO")
    
    return results

if __name__ == "__main__":
    main()