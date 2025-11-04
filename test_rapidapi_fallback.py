#!/usr/bin/env python3
"""
Teste específico para verificar o sistema de fallback do RapidAPI
"""
import os
import sys
from dotenv import load_dotenv

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from services.rapidapi_client import RapidAPIClient

def test_rapidapi_fallback():
    """Testa o sistema de fallback do RapidAPI com múltiplos hosts"""
    load_dotenv()
    
    print("🔍 TESTE DO SISTEMA DE FALLBACK RAPIDAPI")
    print("=" * 60)
    
    # Configurações
    api_key = os.getenv("RAPIDAPI_KEY", "")
    primary_host = os.getenv("RAPIDAPI_HOST", "instagram-scraper-api2.p.rapidapi.com")
    alt_hosts_env = os.getenv("RAPIDAPI_ALT_HOSTS", "")
    
    print(f"🔑 API Key: {api_key[:10]}..." if api_key else "❌ API Key não encontrada")
    print(f"🌐 Host Principal: {primary_host}")
    print(f"🔄 Hosts Alternativos: {alt_hosts_env}")
    print()
    
    if not api_key:
        print("❌ RAPIDAPI_KEY não configurada!")
        return False
    
    # Preparar lista de hosts como no collect.py
    alt_hosts = [h.strip() for h in alt_hosts_env.split(",") if h.strip()]
    seen = set()
    hosts_order = []
    for h in [primary_host] + alt_hosts:
        if h and h not in seen:
            hosts_order.append(h)
            seen.add(h)
    
    print(f"📋 Ordem de teste dos hosts:")
    for i, host in enumerate(hosts_order, 1):
        print(f"   {i}. {host}")
    print()
    
    # Testar cada host individualmente
    hashtag_test = "motivation"
    successful_hosts = []
    
    for i, host in enumerate(hosts_order, 1):
        print(f"🧪 Teste {i}/{len(hosts_order)}: {host}")
        print("-" * 40)
        
        try:
            client = RapidAPIClient(api_key, host)
            
            # Teste simples com hashtag
            print(f"   Testando hashtag '{hashtag_test}'...")
            data = client.get_top_by_hashtag(hashtag_test)
            
            # Verificar se retornou dados válidos
            if data and isinstance(data, dict):
                # Tentar extrair informações básicas
                items_count = 0
                if "data" in data and "items" in data["data"]:
                    items_count = len(data["data"]["items"])
                elif "items" in data:
                    items_count = len(data["items"])
                elif "results" in data:
                    items_count = len(data["results"])
                
                print(f"   ✅ Sucesso! Retornou {items_count} itens")
                print(f"   📊 Chaves da resposta: {list(data.keys())[:5]}")
                successful_hosts.append(host)
            else:
                print(f"   ⚠️ Resposta vazia ou inválida")
                
        except Exception as e:
            error_msg = str(e)
            if "403" in error_msg or "not subscribed" in error_msg.lower():
                print(f"   ❌ Erro de assinatura: {error_msg}")
            elif "404" in error_msg:
                print(f"   ❌ Endpoint não encontrado: {error_msg}")
            elif "429" in error_msg:
                print(f"   ⏳ Rate limit: {error_msg}")
            else:
                print(f"   ❌ Erro: {error_msg}")
        
        print()
    
    # Resumo final
    print("📊 RESUMO DO TESTE")
    print("=" * 60)
    print(f"✅ Hosts funcionais: {len(successful_hosts)}/{len(hosts_order)}")
    
    if successful_hosts:
        print("🎯 Hosts que funcionaram:")
        for host in successful_hosts:
            print(f"   • {host}")
        print()
        print("✅ Sistema de fallback: FUNCIONAL")
        print("💡 O sistema pode usar os hosts alternativos quando o principal falhar.")
        return True
    else:
        print("❌ Nenhum host funcionou")
        print("🔧 Possíveis soluções:")
        print("   1. Verificar se a chave RapidAPI está correta")
        print("   2. Verificar se há assinatura ativa para alguma API de Instagram")
        print("   3. Tentar outras APIs de Instagram no RapidAPI")
        print("   4. Considerar usar a API oficial do Instagram")
        return False

if __name__ == "__main__":
    test_rapidapi_fallback()