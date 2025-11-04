#!/usr/bin/env python3
"""
Teste forçando reload completo dos módulos
"""

import sys
import os
import importlib

print("🔄 TESTE FORCE RELOAD")
print("=" * 50)

# Adicionar src ao path
sys.path.insert(0, 'src')

# Limpar TODOS os módulos relacionados
modules_to_clear = []
for mod_name in list(sys.modules.keys()):
    if any(x in mod_name for x in ['instagram', 'pipeline', 'services']):
        modules_to_clear.append(mod_name)

print(f"🧹 Removendo {len(modules_to_clear)} módulos do cache:")
for mod in modules_to_clear:
    if mod in sys.modules:
        del sys.modules[mod]
        print(f"   - {mod}")

print("\n📄 VERIFICANDO ARQUIVO")
print("=" * 50)

with open('src/pipeline/generate_and_publish.py', 'r', encoding='utf-8') as f:
    first_line = f.readline().strip()
    print(f"Primeira linha: {first_line}")

print("\n🔄 IMPORTANDO COM RELOAD FORÇADO")
print("=" * 50)

try:
    # Import e reload do módulo robust
    import services.instagram_client_robust
    importlib.reload(services.instagram_client_robust)
    from services.instagram_client_robust import InstagramClientRobust
    print(f"✅ InstagramClientRobust carregado: {InstagramClientRobust}")
    print(f"   Módulo: {InstagramClientRobust.__module__}")
    print(f"   Tem _make_request_with_retry: {hasattr(InstagramClientRobust, '_make_request_with_retry')}")
    
    # Import e reload do pipeline
    import pipeline.generate_and_publish
    importlib.reload(pipeline.generate_and_publish)
    from pipeline.generate_and_publish import InstagramClient
    print(f"✅ InstagramClient do pipeline: {InstagramClient}")
    print(f"   Nome da classe: {InstagramClient.__name__}")
    print(f"   Módulo: {InstagramClient.__module__}")
    print(f"   Tem _make_request_with_retry: {hasattr(InstagramClient, '_make_request_with_retry')}")
    print(f"   Tem publish_complete_robust: {hasattr(InstagramClient, 'publish_complete_robust')}")
    
    # Verificar se são a mesma classe
    if InstagramClient is InstagramClientRobust:
        print("🎉 SUCESSO TOTAL: São a mesma classe!")
    elif InstagramClient.__name__ == 'InstagramClientRobust':
        print("🎉 SUCESSO: É InstagramClientRobust!")
    else:
        print(f"❌ FALHA: É {InstagramClient.__name__}")
        
        # Debug detalhado
        print(f"\nDEBUG DETALHADO:")
        print(f"InstagramClientRobust:")
        print(f"  - ID: {id(InstagramClientRobust)}")
        print(f"  - Módulo: {InstagramClientRobust.__module__}")
        print(f"  - Arquivo: {InstagramClientRobust.__module__.__file__ if hasattr(InstagramClientRobust.__module__, '__file__') else 'N/A'}")
        
        print(f"InstagramClient:")
        print(f"  - ID: {id(InstagramClient)}")
        print(f"  - Módulo: {InstagramClient.__module__}")
        
        # Verificar se o módulo services.instagram_client existe
        if 'services.instagram_client' in sys.modules:
            print(f"⚠️  PROBLEMA: services.instagram_client ainda está no cache!")
            old_client = sys.modules['services.instagram_client']
            print(f"   Arquivo: {getattr(old_client, '__file__', 'N/A')}")
        
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()

print("\n📊 MÓDULOS CARREGADOS")
print("=" * 50)
for mod in sorted(sys.modules.keys()):
    if 'instagram' in mod or 'pipeline' in mod:
        print(f"  - {mod}")