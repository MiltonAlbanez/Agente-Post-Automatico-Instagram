#!/usr/bin/env python3
"""
Script para testar a validade do token do Instagram
"""

import requests
import json
import sys
import os
from datetime import datetime

# Adicionar o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from config import load_config

def test_instagram_token():
    """Testa a validade do token do Instagram"""
    print("🔍 Testando validade do token do Instagram...")
    print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)
    
    # Carregar configurações
    config = load_config()
    
    # Verificar se as credenciais estão presentes
    instagram_id = config.get("INSTAGRAM_BUSINESS_ACCOUNT_ID")
    access_token = config.get("INSTAGRAM_ACCESS_TOKEN")
    
    if not instagram_id:
        print("❌ ERRO: INSTAGRAM_BUSINESS_ACCOUNT_ID não encontrado")
        return False
        
    if not access_token:
        print("❌ ERRO: INSTAGRAM_ACCESS_TOKEN não encontrado")
        return False
    
    print(f"📱 Instagram ID: {instagram_id}")
    print(f"🔑 Token (primeiros 20 chars): {access_token[:20]}...")
    print()
    
    # Teste 1: Verificar informações básicas da conta
    print("📋 Teste 1: Informações básicas da conta")
    try:
        url = f"https://graph.facebook.com/v18.0/{instagram_id}"
        params = {
            "fields": "id,username",
            "access_token": access_token
        }
        
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Sucesso! Conta: @{data.get('username', 'N/A')}")
            print(f"   ID: {data.get('id', 'N/A')}")
        else:
            print(f"❌ Erro HTTP {response.status_code}")
            print(f"   Resposta: {response.text}")
            if response.status_code == 400:
                error_data = response.json()
                if "OAuthException" in str(error_data):
                    print("🚨 TOKEN EXPIRADO OU INVÁLIDO!")
                    return False
            return False
            
    except Exception as e:
        print(f"❌ Erro na requisição: {str(e)}")
        return False
    
    print()
    
    # Teste 2: Verificar permissões para publicação
    print("📋 Teste 2: Permissões para publicação")
    try:
        url = f"https://graph.facebook.com/v18.0/{instagram_id}/media"
        params = {
            "limit": 1,
            "access_token": access_token
        }
        
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code == 200:
            print("✅ Permissões de leitura OK")
        else:
            print(f"❌ Erro HTTP {response.status_code}")
            print(f"   Resposta: {response.text}")
            if response.status_code == 400:
                error_data = response.json()
                if "OAuthException" in str(error_data):
                    print("🚨 TOKEN EXPIRADO OU INVÁLIDO!")
                    return False
            
    except Exception as e:
        print(f"❌ Erro na requisição: {str(e)}")
        return False
    
    print()
    
    # Teste 3: Verificar token com Facebook Debug Tool (simulado)
    print("📋 Teste 3: Validação do token")
    try:
        url = "https://graph.facebook.com/debug_token"
        params = {
            "input_token": access_token,
            "access_token": access_token
        }
        
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            token_data = data.get("data", {})
            
            is_valid = token_data.get("is_valid", False)
            expires_at = token_data.get("expires_at")
            app_id = token_data.get("app_id")
            
            if is_valid:
                print("✅ Token válido")
                if expires_at:
                    exp_date = datetime.fromtimestamp(expires_at)
                    print(f"   Expira em: {exp_date.strftime('%Y-%m-%d %H:%M:%S')}")
                else:
                    print("   Sem data de expiração definida")
                print(f"   App ID: {app_id}")
            else:
                print("❌ TOKEN INVÁLIDO!")
                return False
        else:
            print(f"⚠️ Não foi possível validar o token (HTTP {response.status_code})")
            
    except Exception as e:
        print(f"⚠️ Erro na validação do token: {str(e)}")
    
    print()
    print("✅ Todos os testes passaram! Token parece estar funcionando.")
    return True

def test_rapidapi_connection():
    """Testa a conexão com RapidAPI"""
    print("\n🔍 Testando conexão com RapidAPI...")
    print("-" * 60)
    
    config = load_config()
    rapidapi_key = config.get("RAPIDAPI_KEY")
    rapidapi_host = config.get("RAPIDAPI_HOST", "instagram-scraper-api2.p.rapidapi.com")
    
    if not rapidapi_key:
        print("❌ ERRO: RAPIDAPI_KEY não encontrado")
        return False
    
    print(f"🔑 RapidAPI Key (primeiros 10 chars): {rapidapi_key[:10]}...")
    print(f"🌐 Host: {rapidapi_host}")
    print()
    
    # Teste de conexão básica
    try:
        url = f"https://{rapidapi_host}/v1/hashtag"
        headers = {
            "X-RapidAPI-Key": rapidapi_key,
            "X-RapidAPI-Host": rapidapi_host
        }
        params = {
            "hashtag": "test",
            "count": 1
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        if response.status_code == 200:
            print("✅ Conexão com RapidAPI OK")
            return True
        elif response.status_code == 429:
            print("⚠️ Rate limit atingido - mas conexão OK")
            return True
        elif response.status_code == 401:
            print("❌ ERRO: Chave RapidAPI inválida ou expirada")
            return False
        else:
            print(f"⚠️ Resposta inesperada: HTTP {response.status_code}")
            print(f"   Resposta: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ Erro na conexão: {str(e)}")
        return False

def main():
    """Função principal"""
    print("🚀 DIAGNÓSTICO DO SISTEMA DE AUTOMAÇÃO")
    print("=" * 60)
    
    # Testar Instagram
    instagram_ok = test_instagram_token()
    
    # Testar RapidAPI
    rapidapi_ok = test_rapidapi_connection()
    
    print("\n📊 RESUMO DOS TESTES")
    print("=" * 60)
    print(f"Instagram Token: {'✅ OK' if instagram_ok else '❌ FALHOU'}")
    print(f"RapidAPI: {'✅ OK' if rapidapi_ok else '❌ FALHOU'}")
    
    if instagram_ok and rapidapi_ok:
        print("\n🎉 Todos os serviços estão funcionando!")
        print("   O problema pode estar na configuração do cron no Railway.")
    else:
        print("\n🚨 PROBLEMAS IDENTIFICADOS:")
        if not instagram_ok:
            print("   - Token do Instagram inválido ou expirado")
        if not rapidapi_ok:
            print("   - Problemas com RapidAPI")
        print("\n💡 SOLUÇÕES:")
        if not instagram_ok:
            print("   1. Renovar token do Instagram via Facebook Developers")
            print("   2. Verificar se o token tem as permissões corretas")
        if not rapidapi_ok:
            print("   1. Verificar se a chave RapidAPI está correta")
            print("   2. Verificar se não excedeu o limite de requisições")

if __name__ == "__main__":
    main()