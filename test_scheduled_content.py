#!/usr/bin/env python3
"""
Teste para verificar conteúdo programado para o post feed
"""

import sys
import os
from datetime import datetime
import json

# Adicionar o diretório raiz ao path
sys.path.append('.')

def check_database_content():
    """Verifica conteúdo disponível no banco de dados"""
    print("🔍 Verificando conteúdo no banco de dados...")
    try:
        from src.services.db import Database
        from src.config import load_config
        
        config = load_config()
        dsn = config.get('DATABASE_URL')
        
        if not dsn:
            print("❌ DSN do banco não configurado")
            return False, "DSN não configurado"
        
        db = Database(dsn)
        
        # Verificar posts não publicados
        with db.conn.cursor() as cur:
            cur.execute("""
                SELECT COUNT(*) as total, 
                       COUNT(CASE WHEN isposted = FALSE THEN 1 END) as nao_publicados
                FROM top_trends
            """)
            result = cur.fetchone()
            
            if result:
                total, nao_publicados = result
                print(f"✅ Banco de dados: {total} posts total, {nao_publicados} não publicados")
                
                # Mostrar alguns exemplos
                cur.execute("""
                    SELECT prompt, tag, code, created_at 
                    FROM top_trends 
                    WHERE isposted = FALSE 
                    ORDER BY created_at DESC 
                    LIMIT 3
                """)
                examples = cur.fetchall()
                
                if examples:
                    print("📋 Exemplos de conteúdo disponível:")
                    for i, (prompt, tag, code, created_at) in enumerate(examples, 1):
                        prompt_preview = prompt[:50] + "..." if len(prompt) > 50 else prompt
                        print(f"   {i}. Tag: #{tag} | Code: {code}")
                        print(f"      Prompt: {prompt_preview}")
                        print(f"      Criado: {created_at}")
                        print()
                
                return True, f"Total: {total}, Disponíveis: {nao_publicados}"
            else:
                print("❌ Falha ao consultar banco")
                return False, "Falha na consulta"
                
    except Exception as e:
        print(f"❌ Erro no banco: {e}")
        return False, str(e)

def check_accounts_config():
    """Verifica configuração das contas"""
    print("🔍 Verificando configuração das contas...")
    try:
        accounts_file = "accounts.json"
        if not os.path.exists(accounts_file):
            print("❌ Arquivo accounts.json não encontrado")
            return False, "Arquivo accounts.json não encontrado"
        
        with open(accounts_file, 'r', encoding='utf-8') as f:
            accounts = json.load(f)
        
        if not accounts:
            print("❌ Nenhuma conta configurada")
            return False, "Nenhuma conta configurada"
        
        active_accounts = [acc for acc in accounts if acc.get('active', True)]
        feed_accounts = [acc for acc in active_accounts if acc.get('type') == 'feed']
        
        print(f"✅ Contas: {len(accounts)} total, {len(active_accounts)} ativas, {len(feed_accounts)} para feed")
        
        if feed_accounts:
            print("📋 Contas configuradas para feed:")
            for acc in feed_accounts[:3]:  # Mostrar até 3 contas
                username = acc.get('username', 'N/A')
                business_id = acc.get('business_account_id', 'N/A')[:10] + '...'
                print(f"   - @{username} (ID: {business_id})")
        
        return True, f"Feed accounts: {len(feed_accounts)}"
        
    except Exception as e:
        print(f"❌ Erro nas contas: {e}")
        return False, str(e)

def check_content_generation():
    """Verifica se o sistema de geração de conteúdo está funcionando"""
    print("🔍 Testando geração de conteúdo...")
    try:
        from src.services.openai_client import OpenAIClient
        from src.config import load_config
        
        config = load_config()
        
        # Verificar se OpenAI está configurado
        openai_key = config.get('OPENAI_API_KEY')
        if not openai_key:
            print("❌ OpenAI API Key não configurada")
            return False, "OpenAI não configurado"
        
        client = OpenAIClient(openai_key)
        
        # Teste simples de geração
        test_prompt = "Gere uma frase motivacional sobre sucesso"
        result = client.generate_content_from_prompt(test_prompt)
        
        if result and len(result.strip()) > 10:
            print(f"✅ Geração de conteúdo: Funcionando")
            print(f"   Exemplo: {result[:100]}...")
            return True, "Geração funcionando"
        else:
            print("❌ Geração de conteúdo: Falha")
            return False, "Falha na geração"
            
    except Exception as e:
        print(f"❌ Erro na geração: {e}")
        return False, str(e)

def check_image_generation():
    """Verifica se o sistema de geração de imagens está funcionando"""
    print("🔍 Verificando geração de imagens...")
    try:
        from src.services.replicate_client import ReplicateClient
        from src.config import load_config
        
        config = load_config()
        
        # Verificar se Replicate está configurado
        replicate_token = config.get('REPLICATE_API_TOKEN')
        if not replicate_token:
            print("❌ Replicate API Token não configurado")
            return False, "Replicate não configurado"
        
        print("✅ Replicate: Configurado")
        return True, "Replicate configurado"
        
    except Exception as e:
        print(f"❌ Erro no Replicate: {e}")
        return False, str(e)

def main():
    """Executa todos os testes de conteúdo"""
    print("🚀 VERIFICAÇÃO DE CONTEÚDO PROGRAMADO")
    print("=" * 50)
    print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    results = {}
    
    # Teste banco de dados
    db_ok, db_msg = check_database_content()
    results['database'] = {'status': db_ok, 'message': db_msg}
    print()
    
    # Teste contas
    accounts_ok, accounts_msg = check_accounts_config()
    results['accounts'] = {'status': accounts_ok, 'message': accounts_msg}
    print()
    
    # Teste geração de conteúdo
    content_ok, content_msg = check_content_generation()
    results['content_generation'] = {'status': content_ok, 'message': content_msg}
    print()
    
    # Teste geração de imagens
    images_ok, images_msg = check_image_generation()
    results['image_generation'] = {'status': images_ok, 'message': images_msg}
    print()
    
    # Resumo
    print("📊 RESUMO DA VERIFICAÇÃO DE CONTEÚDO")
    print("=" * 50)
    
    all_ok = True
    for service, result in results.items():
        status_icon = "✅" if result['status'] else "❌"
        service_name = service.replace('_', ' ').title()
        print(f"{status_icon} {service_name}: {result['message']}")
        if not result['status']:
            all_ok = False
    
    print()
    if all_ok:
        print("🎉 CONTEÚDO PRONTO PARA PUBLICAÇÃO!")
    else:
        print("⚠️ ALGUNS PROBLEMAS NO CONTEÚDO - VERIFICAR ANTES DA PUBLICAÇÃO")
    
    return results

if __name__ == "__main__":
    main()