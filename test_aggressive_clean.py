#!/usr/bin/env python3
"""
Teste com limpeza agressiva do cache Python
"""

import sys
import os
import importlib
import gc

print("🧹 TESTE LIMPEZA AGRESSIVA")
print("=" * 50)

# Adicionar src ao path
sys.path.insert(0, 'src')

# Limpeza TOTAL de módulos
print("🗑️ REMOVENDO TODOS OS MÓDULOS RELACIONADOS")
modules_to_clear = []
for mod_name in list(sys.modules.keys()):
    if any(x in mod_name.lower() for x in ['instagram', 'pipeline', 'services']):
        modules_to_clear.append(mod_name)

print(f"Removendo {len(modules_to_clear)} módulos:")
for mod in modules_to_clear:
    if mod in sys.modules:
        print(f"  - {mod}")
        del sys.modules[mod]

# Forçar garbage collection
gc.collect()

print("\n🔄 VERIFICANDO ARQUIVO ATUAL")
print("=" * 50)

with open('src/pipeline/generate_and_publish.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for i, line in enumerate(lines[:10], 1):
        if 'instagram' in line.lower():
            print(f"Linha {i}: {line.strip()}")

print("\n🚀 IMPORTAÇÃO FORÇADA PASSO A PASSO")
print("=" * 50)

try:
    # Passo 1: Import direto do robust
    print("1️⃣ Importando InstagramClientRobust...")
    from services.instagram_client_robust import InstagramClientRobust
    print(f"   ✅ Sucesso: {InstagramClientRobust}")
    print(f"   📍 Módulo: {InstagramClientRobust.__module__}")
    print(f"   🔧 Tem _make_request_with_retry: {hasattr(InstagramClientRobust, '_make_request_with_retry')}")
    
    # Passo 2: Verificar se o módulo antigo existe
    print("\n2️⃣ Verificando módulo antigo...")
    try:
        import services.instagram_client
        print(f"   ⚠️ Módulo antigo AINDA EXISTE: {services.instagram_client}")
        # Forçar remoção
        if 'services.instagram_client' in sys.modules:
            del sys.modules['services.instagram_client']
            print("   🗑️ Módulo antigo removido do cache")
    except ImportError:
        print("   ✅ Módulo antigo não encontrado (bom!)")
    
    # Passo 3: Import do pipeline com reload forçado
    print("\n3️⃣ Importando do pipeline...")
    
    # Verificar se já existe no cache
    if 'pipeline.generate_and_publish' in sys.modules:
        print("   🔄 Módulo pipeline já no cache, removendo...")
        del sys.modules['pipeline.generate_and_publish']
    
    if 'pipeline' in sys.modules:
        print("   🔄 Módulo pipeline base já no cache, removendo...")
        del sys.modules['pipeline']
    
    # Import limpo
    from pipeline.generate_and_publish import InstagramClient
    print(f"   ✅ InstagramClient importado: {InstagramClient}")
    print(f"   📍 Nome da classe: {InstagramClient.__name__}")
    print(f"   📍 Módulo: {InstagramClient.__module__}")
    print(f"   🔧 Tem _make_request_with_retry: {hasattr(InstagramClient, '_make_request_with_retry')}")
    print(f"   🔧 Tem publish_complete_robust: {hasattr(InstagramClient, 'publish_complete_robust')}")
    
    # Passo 4: Comparação final
    print("\n4️⃣ COMPARAÇÃO FINAL")
    print("=" * 30)
    
    if InstagramClient is InstagramClientRobust:
        print("🎉 PERFEITO: São exatamente a mesma classe!")
    elif InstagramClient.__name__ == 'InstagramClientRobust':
        print("🎉 SUCESSO: É InstagramClientRobust!")
    else:
        print(f"❌ FALHA: É {InstagramClient.__name__} do módulo {InstagramClient.__module__}")
        
        # Debug final
        print(f"\n🔍 DEBUG FINAL:")
        print(f"InstagramClientRobust ID: {id(InstagramClientRobust)}")
        print(f"InstagramClient ID: {id(InstagramClient)}")
        print(f"Mesmo objeto? {InstagramClient is InstagramClientRobust}")
        
        # Verificar todos os módulos carregados
        print(f"\n📋 MÓDULOS INSTAGRAM CARREGADOS:")
        for mod in sorted(sys.modules.keys()):
            if 'instagram' in mod.lower():
                print(f"  - {mod}")
        
except Exception as e:
    print(f"❌ Erro durante importação: {e}")
    import traceback
    traceback.print_exc()

print("\n📊 RESULTADO FINAL")
print("=" * 50)