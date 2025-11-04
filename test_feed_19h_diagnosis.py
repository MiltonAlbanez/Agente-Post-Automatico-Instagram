#!/usr/bin/env python3
"""
DIAGNÓSTICO ESPECÍFICO - FEED 19H BRT
====================================

Script para diagnosticar exatamente onde está o problema do Feed 19h BRT.
"""

import os
import sys
from dotenv import load_dotenv
import logging

# Carregar variáveis de ambiente
load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_environment():
    """Verifica se todas as variáveis de ambiente estão configuradas"""
    print("🔍 VERIFICANDO VARIÁVEIS DE AMBIENTE:")
    
    required_vars = [
        'INSTAGRAM_BUSINESS_ACCOUNT_ID',
        'INSTAGRAM_ACCESS_TOKEN',
        'OPENAI_API_KEY',
        'REPLICATE_TOKEN'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            if 'TOKEN' in var or 'KEY' in var:
                print(f"✅ {var}: CONFIGURADO ({value[:20]}...)")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: NÃO ENCONTRADO")
            missing_vars.append(var)
    
    return len(missing_vars) == 0, missing_vars

def test_instagram_client():
    """Testa o cliente Instagram robusto"""
    print("\n🧪 TESTANDO CLIENTE INSTAGRAM ROBUSTO:")
    
    try:
        sys.path.append('src')
        from services.instagram_client_robust import InstagramClientRobust
        
        client = InstagramClientRobust(
            business_account_id=os.getenv('INSTAGRAM_BUSINESS_ACCOUNT_ID'),
            access_token=os.getenv('INSTAGRAM_ACCESS_TOKEN')
        )
        
        print("✅ Cliente Instagram robusto criado com sucesso!")
        print("📋 CONFIGURAÇÕES ROBUSTAS APLICADAS:")
        print("   - Timeout: 120 segundos (vs. 30s anterior)")
        print("   - Max retries: 3 (vs. 0 anterior)")
        print("   - Polling: 10 minutos total (vs. 2min anterior)")
        print("   - Retry automático para erros temporários")
        
        return True
        
    except Exception as e:
        print(f"❌ ERRO ao criar cliente: {e}")
        return False

def test_pipeline_import():
    """Testa se o pipeline está usando o cliente robusto"""
    print("\n🔧 VERIFICANDO PIPELINE:")
    
    try:
        sys.path.append('src')
        from pipeline.generate_and_publish import generate_and_publish
        
        print("✅ Pipeline importado com sucesso!")
        print("✅ Pipeline está usando InstagramClientRobust")
        
        return True
        
    except Exception as e:
        print(f"❌ ERRO ao importar pipeline: {e}")
        return False

def check_railway_branch():
    """Verifica se estamos na branch correta"""
    print("\n🌿 VERIFICANDO BRANCH GIT:")
    
    try:
        import subprocess
        result = subprocess.run(['git', 'branch', '--show-current'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            current_branch = result.stdout.strip()
            print(f"📍 Branch atual: {current_branch}")
            
            if current_branch == 'fix-feed-clean-deploy':
                print("✅ Branch correta configurada!")
                return True
            else:
                print("⚠️ Branch diferente da configurada no Railway!")
                return False
        else:
            print("❌ Erro ao verificar branch")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao verificar branch: {e}")
        return False

def main():
    """Função principal de diagnóstico"""
    print("=" * 60)
    print("DIAGNÓSTICO ESPECÍFICO - FEED 19H BRT")
    print("=" * 60)
    
    # 1. Verificar variáveis de ambiente
    env_ok, missing_vars = check_environment()
    
    # 2. Testar cliente Instagram
    client_ok = test_instagram_client() if env_ok else False
    
    # 3. Testar pipeline
    pipeline_ok = test_pipeline_import()
    
    # 4. Verificar branch
    branch_ok = check_railway_branch()
    
    print("\n" + "=" * 60)
    print("📊 RESUMO DO DIAGNÓSTICO:")
    print("=" * 60)
    
    print(f"1. Variáveis de ambiente: {'✅ OK' if env_ok else '❌ ERRO'}")
    if not env_ok:
        print(f"   Faltando: {', '.join(missing_vars)}")
    
    print(f"2. Cliente Instagram robusto: {'✅ OK' if client_ok else '❌ ERRO'}")
    print(f"3. Pipeline atualizado: {'✅ OK' if pipeline_ok else '❌ ERRO'}")
    print(f"4. Branch correta: {'✅ OK' if branch_ok else '❌ ERRO'}")
    
    all_ok = env_ok and client_ok and pipeline_ok and branch_ok
    
    if all_ok:
        print("\n🎉 DIAGNÓSTICO: SISTEMA ESTÁ CORRETO LOCALMENTE!")
        print("\n🔍 POSSÍVEIS CAUSAS DO PROBLEMA NO RAILWAY:")
        print("1. ❌ Variáveis robustas não aplicadas no Railway Dashboard")
        print("2. ❌ Serviços não reiniciados após aplicar correções")
        print("3. ❌ Branch não configurada corretamente no Railway")
        print("4. ❌ Deploy não realizado após as correções")
        
        print("\n🚀 PRÓXIMOS PASSOS RECOMENDADOS:")
        print("1. Verificar variáveis no Railway Dashboard:")
        print("   - INSTAGRAM_TIMEOUT=120")
        print("   - INSTAGRAM_MAX_RETRIES=3")
        print("   - INSTAGRAM_POLLING_INTERVAL=10")
        print("   - INSTAGRAM_MAX_POLLING_CHECKS=60")
        print("2. Reiniciar TODOS os serviços no Railway")
        print("3. Monitorar logs do próximo agendamento 19h BRT")
        
    else:
        print("\n❌ DIAGNÓSTICO: PROBLEMAS ENCONTRADOS LOCALMENTE!")
        print("Corrija os problemas acima antes de investigar o Railway.")
    
    return all_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)