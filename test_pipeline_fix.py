#!/usr/bin/env python3
"""
🔧 TESTE CRÍTICO: Verificar se pipeline está usando InstagramClientRobust
"""

import os
import sys
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def test_pipeline_import_detailed():
    """Testa detalhadamente qual classe está sendo importada"""
    print("🔍 TESTE DETALHADO: Verificando imports da pipeline...")
    
    try:
        # Adicionar o diretório src ao path
        sys.path.insert(0, 'src')
        
        # Importar diretamente do pipeline
        from pipeline.generate_and_publish import InstagramClient
        
        print(f"✅ Classe encontrada: {InstagramClient}")
        print(f"✅ Módulo da classe: {InstagramClient.__module__}")
        print(f"✅ Nome da classe: {InstagramClient.__name__}")
        
        # Verificar métodos disponíveis
        methods = [method for method in dir(InstagramClient) if not method.startswith('_')]
        print(f"✅ Métodos disponíveis: {methods}")
        
        # Verificar especificamente os métodos robustos
        has_make_request_with_retry = hasattr(InstagramClient, '_make_request_with_retry')
        has_publish_complete_robust = hasattr(InstagramClient, 'publish_complete_robust')
        
        print(f"✅ Tem _make_request_with_retry: {has_make_request_with_retry}")
        print(f"✅ Tem publish_complete_robust: {has_publish_complete_robust}")
        
        # Verificar se é realmente a classe robusta
        if InstagramClient.__name__ == 'InstagramClientRobust':
            print("🎉 SUCESSO: É realmente InstagramClientRobust!")
            return True
        else:
            print(f"❌ ERRO: É {InstagramClient.__name__}, não InstagramClientRobust!")
            return False
            
    except Exception as e:
        print(f"❌ ERRO ao importar: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

def test_direct_import():
    """Testa importar diretamente o InstagramClientRobust"""
    print("\n🔍 TESTE: Importando InstagramClientRobust diretamente...")
    
    try:
        sys.path.insert(0, 'src')
        from services.instagram_client_robust import InstagramClientRobust
        
        print(f"✅ InstagramClientRobust importado: {InstagramClientRobust}")
        print(f"✅ Módulo: {InstagramClientRobust.__module__}")
        
        # Verificar métodos
        has_make_request_with_retry = hasattr(InstagramClientRobust, '_make_request_with_retry')
        has_publish_complete_robust = hasattr(InstagramClientRobust, 'publish_complete_robust')
        
        print(f"✅ Tem _make_request_with_retry: {has_make_request_with_retry}")
        print(f"✅ Tem publish_complete_robust: {has_publish_complete_robust}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERRO ao importar InstagramClientRobust: {e}")
        return False

def test_import_conflict():
    """Testa se há conflito de imports"""
    print("\n🔍 TESTE: Verificando conflitos de import...")
    
    try:
        sys.path.insert(0, 'src')
        
        # Importar ambos os clientes
        from services.instagram_client import InstagramClient as OldClient
        from services.instagram_client_robust import InstagramClientRobust as RobustClient
        
        print(f"✅ Cliente antigo: {OldClient}")
        print(f"✅ Cliente robusto: {RobustClient}")
        
        # Verificar se são diferentes
        if OldClient != RobustClient:
            print("✅ São classes diferentes (correto)")
            return True
        else:
            print("❌ São a mesma classe (problema!)")
            return False
            
    except Exception as e:
        print(f"❌ ERRO ao testar conflito: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 DIAGNÓSTICO DETALHADO: PROBLEMA DE IMPORT")
    print("=" * 60)
    
    # Executar testes detalhados
    test1 = test_pipeline_import_detailed()
    test2 = test_direct_import()
    test3 = test_import_conflict()
    
    print("\n📊 RESUMO DOS TESTES")
    print("=" * 60)
    print(f"Pipeline import detalhado: {'✅ OK' if test1 else '❌ FALHOU'}")
    print(f"Import direto InstagramClientRobust: {'✅ OK' if test2 else '❌ FALHOU'}")
    print(f"Teste de conflito: {'✅ OK' if test3 else '❌ FALHOU'}")
    
    if test1 and test2 and test3:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
    else:
        print("\n🚨 PROBLEMAS IDENTIFICADOS!")
    
    return test1 and test2 and test3

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)