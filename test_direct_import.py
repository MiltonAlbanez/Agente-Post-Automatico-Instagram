#!/usr/bin/env python3
"""
Teste direto para verificar o problema de import
"""

import sys
import os
import importlib

print("🔍 TESTE DIRETO DE IMPORT")
print("=" * 50)

# Adicionar src ao path
sys.path.insert(0, 'src')

print(f"📁 Python path: {sys.path[:3]}")
print(f"📁 Diretório atual: {os.getcwd()}")

# Verificar se os arquivos existem
files_to_check = [
    'src/services/instagram_client_robust.py',
    'src/services/instagram_client.py',
    'src/pipeline/generate_and_publish.py'
]

for file_path in files_to_check:
    exists = os.path.exists(file_path)
    print(f"📄 {file_path}: {'✅ Existe' if exists else '❌ Não existe'}")

print("\n🔍 TESTANDO IMPORTS DIRETOS")
print("=" * 50)

try:
    # Import direto do InstagramClientRobust
    print("📦 Importando InstagramClientRobust...")
    from services.instagram_client_robust import InstagramClientRobust
    print(f"✅ InstagramClientRobust: {InstagramClientRobust}")
    print(f"   Módulo: {InstagramClientRobust.__module__}")
    print(f"   Tem _make_request_with_retry: {hasattr(InstagramClientRobust, '_make_request_with_retry')}")
    
except Exception as e:
    print(f"❌ Erro ao importar InstagramClientRobust: {e}")

try:
    # Import direto do InstagramClient antigo
    print("\n📦 Importando InstagramClient antigo...")
    from services.instagram_client import InstagramClient as OldInstagramClient
    print(f"✅ InstagramClient antigo: {OldInstagramClient}")
    print(f"   Módulo: {OldInstagramClient.__module__}")
    print(f"   Tem _make_request_with_retry: {hasattr(OldInstagramClient, '_make_request_with_retry')}")
    
except Exception as e:
    print(f"❌ Erro ao importar InstagramClient antigo: {e}")

print("\n🔍 TESTANDO IMPORT DO PIPELINE")
print("=" * 50)

try:
    # Limpar cache de módulos
    if 'pipeline.generate_and_publish' in sys.modules:
        del sys.modules['pipeline.generate_and_publish']
    
    # Import do pipeline
    print("📦 Importando do pipeline...")
    import pipeline.generate_and_publish as pipeline_module
    
    # Verificar qual InstagramClient está sendo usado
    instagram_client_class = getattr(pipeline_module, 'InstagramClient', None)
    
    if instagram_client_class:
        print(f"✅ InstagramClient do pipeline: {instagram_client_class}")
        print(f"   Nome da classe: {instagram_client_class.__name__}")
        print(f"   Módulo: {instagram_client_class.__module__}")
        print(f"   Tem _make_request_with_retry: {hasattr(instagram_client_class, '_make_request_with_retry')}")
        print(f"   Tem publish_complete_robust: {hasattr(instagram_client_class, 'publish_complete_robust')}")
        
        # Verificar se é a classe correta
        if instagram_client_class.__name__ == 'InstagramClientRobust':
            print("🎉 SUCESSO: Pipeline usando InstagramClientRobust!")
        else:
            print(f"❌ PROBLEMA: Pipeline usando {instagram_client_class.__name__}")
            
            # Verificar se há conflito de imports
            print("\n🔍 ANALISANDO CONFLITO...")
            print("Verificando imports no módulo pipeline...")
            
            # Listar todos os atributos do módulo
            attrs = [attr for attr in dir(pipeline_module) if not attr.startswith('_')]
            print(f"Atributos do módulo: {attrs}")
            
    else:
        print("❌ InstagramClient não encontrado no pipeline!")
        
except Exception as e:
    print(f"❌ Erro ao importar pipeline: {e}")
    import traceback
    traceback.print_exc()

print("\n📊 RESUMO")
print("=" * 50)